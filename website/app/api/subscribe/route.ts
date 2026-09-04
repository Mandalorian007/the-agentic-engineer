import { NextRequest } from 'next/server';
import { z } from 'zod';
import { rateLimit, clientKey } from '@/lib/rate-limit';
import { SITE_URL, NEWSLETTER_NAME, AUTHOR } from '@/lib/site';

/**
 * Newsletter subscribe endpoint
 *
 * Provider-agnostic seam. Set BUTTONDOWN_API_KEY (or swap the
 * subscribeWithProvider body for Kit/Resend) to go live.
 *
 * With no provider configured, non-production runs log the address to the
 * server console and return success so the full UI can be reviewed locally.
 * Production without a provider fails loudly rather than dropping addresses.
 */

const SubscribeSchema = z.object({
  email: z.string().email().max(254),
  // Written verbatim into provider metadata, so constrain the shape too
  source: z.string().max(64).regex(/^[a-z0-9:_-]+$/i).optional(),
});

const SUCCESS_MESSAGE = "You're in. Check your inbox to confirm.";
// Buttondown does not resend a confirmation to someone already on the list, so
// telling them to check their inbox sends them to wait for nothing.
const ALREADY_SUBSCRIBED_MESSAGE = "You're already on the list. Nothing to do.";

type SubscribeResult = 'created' | 'existing';
/** Buttondown can hang; without this the route hangs with it. */
const PROVIDER_TIMEOUT_MS = 10_000;

// Every accepted request costs an outbound call to a metered provider and can
// send a confirmation email to an address the caller does not own.
const RATE_LIMIT = 5;
const RATE_WINDOW_MS = 10 * 60 * 1000;

class SubscribeError extends Error {
  constructor(readonly userMessage: string, readonly logDetail: string) {
    super(logDetail);
  }
}

async function subscribeWithProvider(
  email: string,
  source: string
): Promise<SubscribeResult> {
  const apiKey = process.env.BUTTONDOWN_API_KEY;

  if (!apiKey) {
    if (process.env.NODE_ENV === 'production') {
      throw new Error('No newsletter provider configured');
    }
    console.log(`[subscribe:preview] ${email} (source: ${source})`);
    return 'created';
  }

  const response = await fetch('https://api.buttondown.com/v1/subscribers', {
    method: 'POST',
    headers: {
      Authorization: `Token ${apiKey}`,
      'Content-Type': 'application/json',
      // Upsert rather than reject. Without this a returning reader, or anyone
      // who previously unsubscribed, gets a hard error. Verified: this turns
      // the duplicate 400 into a 201 and resubscribes the unsubscribed.
      'X-Buttondown-Collision-Behavior': 'add',
    },
    body: JSON.stringify({
      email_address: email,
      // `source` lives in metadata, not tags. Tag auto-creation needs a paid
      // add-on and would mint one tag per post slug; metadata is free, is
      // queryable, and holds arbitrary strings.
      metadata: { newsletter: NEWSLETTER_NAME, source },
    }),
    signal: AbortSignal.timeout(PROVIDER_TIMEOUT_MS),
  });

  // 201 is a new subscriber, 200 is the collision header matching an existing
  // one. The distinction is the only thing separating "check your inbox" from
  // an inbox that will stay empty.
  if (response.ok) return response.status === 201 ? 'created' : 'existing';

  // Buttondown reports every failure as 400 plus a `code`, so the status alone
  // cannot tell "already subscribed" from "genuinely rejected".
  let code = '';
  let detail = '';
  try {
    const body = await response.json();
    code = body?.code ?? '';
    detail = body?.detail ?? '';
  } catch {
    // Non-JSON error body; fall through to the generic case.
  }

  switch (code) {
    // Belt and braces: the collision header should already have handled this.
    case 'email_already_exists':
      return 'existing';

    // Buttondown's spam firewall rejected the address. Retrying will not help,
    // so do not invite one.
    case 'subscriber_blocked':
      throw new SubscribeError(
        `That address was rejected by our spam filter. If that's wrong, email ${AUTHOR.email} and I'll add you by hand.`,
        `subscriber_blocked: ${detail}`
      );

    default:
      throw new SubscribeError(
        'Could not sign you up right now. Try again in a minute?',
        `Provider responded ${response.status} ${code}: ${detail}`
      );
  }
}

/**
 * Reject cross-site form posts. Absent Origin (curl, older clients) passes.
 *
 * The apex domain is not the only host that serves this site: preview
 * deployments run on *.vercel.app, and www redirects to the apex. Comparing
 * against SITE_URL alone 403s the smoke test you run before launch.
 */
function isForeignOrigin(request: NextRequest): boolean {
  const origin = request.headers.get('origin');
  if (!origin) return false;
  if (process.env.NODE_ENV !== 'production') return false;

  let hostname: string;
  try {
    hostname = new URL(origin).hostname;
  } catch {
    return true;
  }

  const site = new URL(SITE_URL).hostname;

  return !(
    hostname === site ||
    hostname === `www.${site}` ||
    hostname.endsWith('.vercel.app')
  );
}

export async function POST(request: NextRequest) {
  if (isForeignOrigin(request)) {
    return Response.json({ message: 'Invalid request origin' }, { status: 403 });
  }

  let parsed;

  try {
    parsed = SubscribeSchema.safeParse(await request.json());
  } catch {
    return Response.json({ message: 'Invalid request body' }, { status: 400 });
  }

  if (!parsed.success) {
    return Response.json(
      { message: 'That email address does not look right.' },
      { status: 400 }
    );
  }

  // Limit only what would actually reach the provider. Counting rejected typos
  // lets someone lock themselves out by mistyping their own address.
  const { ok, retryAfter } = rateLimit(
    `subscribe:${clientKey(request)}`,
    RATE_LIMIT,
    RATE_WINDOW_MS
  );

  if (!ok) {
    return Response.json(
      { message: 'Too many attempts. Try again in a few minutes.' },
      { status: 429, headers: { 'Retry-After': String(retryAfter) } }
    );
  }

  const { email, source = 'unknown' } = parsed.data;

  try {
    const result = await subscribeWithProvider(email, source);
    return Response.json({
      message: result === 'existing' ? ALREADY_SUBSCRIBED_MESSAGE : SUCCESS_MESSAGE,
    });
  } catch (error) {
    if (error instanceof SubscribeError) {
      console.error('Subscribe error:', error.logDetail);
      return Response.json({ message: error.userMessage }, { status: 502 });
    }

    console.error('Subscribe error:', error);
    return Response.json(
      { message: 'Could not sign you up right now. Try again in a minute?' },
      { status: 500 }
    );
  }
}
