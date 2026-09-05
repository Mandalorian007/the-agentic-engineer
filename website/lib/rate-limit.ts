/**
 * In-memory sliding-window rate limiter.
 *
 * Deliberately dependency-free. On Vercel each serverless instance keeps its
 * own counters, so this is not a distributed limit and a determined attacker
 * spread across cold starts can exceed it. It is not trying to be airtight: it
 * exists so a single client cannot sit in a loop driving outbound calls to a
 * paid provider, which is the realistic abuse of a public subscribe form.
 *
 * If this ever needs to be exact, swap the Map for Upstash Redis and keep the
 * same signature.
 */

interface Window {
  hits: number[];
  /** Cheap TTL so the map cannot grow without bound. */
  expires: number;
}

const windows = new Map<string, Window>();

/** Drop entries nothing has touched for a while. */
function sweep(now: number) {
  if (windows.size < 5_000) return;
  for (const [key, window] of windows) {
    if (window.expires < now) windows.delete(key);
  }
}

export interface RateLimitResult {
  ok: boolean;
  /** Seconds until the caller may retry. Zero when ok. */
  retryAfter: number;
}

export function rateLimit(
  key: string,
  limit: number,
  windowMs: number
): RateLimitResult {
  const now = Date.now();
  sweep(now);

  const cutoff = now - windowMs;
  const existing = windows.get(key);
  const hits = (existing?.hits ?? []).filter((time) => time > cutoff);

  if (hits.length >= limit) {
    const oldest = hits[0];
    return {
      ok: false,
      retryAfter: Math.max(1, Math.ceil((oldest + windowMs - now) / 1000)),
    };
  }

  hits.push(now);
  windows.set(key, { hits, expires: now + windowMs });

  return { ok: true, retryAfter: 0 };
}

/**
 * Best-effort client address.
 *
 * On Vercel `x-forwarded-for` is set by the edge and its first entry is the
 * real client. Locally it is usually absent, so everything shares one bucket.
 */
export function clientKey(request: Request): string {
  const forwarded = request.headers.get('x-forwarded-for');
  if (forwarded) return forwarded.split(',')[0].trim();
  return request.headers.get('x-real-ip') ?? 'unknown';
}
