import { revalidatePath } from 'next/cache';
import { NextRequest } from 'next/server';
import { getAllCategoryIds } from '@/lib/categories';

/**
 * On-demand revalidation endpoint
 *
 * Called by GitHub Actions on publish morning, before the tweet and before the
 * issue goes out, so every surface that links a post already shows it.
 *
 * Usage:
 *   curl -X POST \
 *     -H "Authorization: Bearer YOUR_SECRET" \
 *     -H "Content-Type: application/json" \
 *     -d '{"slug":"2026-09-07-example"}' \
 *     https://agentic-engineer.com/api/revalidate
 */
export async function POST(request: NextRequest) {
  try {
    // Security: Verify secret token
    const authHeader = request.headers.get('authorization');
    const token = authHeader?.replace('Bearer ', '');
    const expectedToken = process.env.REVALIDATE_SECRET;

    if (!token || token !== expectedToken) {
      return Response.json(
        { message: 'Invalid or missing token' },
        { status: 401 }
      );
    }

    // An optional slug lets the caller purge the one page the tweet links to.
    // Body is optional: a bare POST still refreshes every listing.
    let slug: string | undefined;
    try {
      const body = await request.json();
      if (typeof body?.slug === 'string' && /^[a-z0-9-]{1,128}$/i.test(body.slug)) {
        slug = body.slug;
      }
    } catch {
      // No body, or not JSON. Fall through to the listings-only refresh.
    }

    const paths = [
      '/',                  // Home page
      '/blog',              // Blog listing
      '/issues',            // Email archive (issues appear by date)
      // Both streams cross into public by wall clock, so the sitemap has to be
      // purged too or a newly public page never gets submitted.
      '/sitemap.xml',
      // Category counts and listings change with every new post.
      ...getAllCategoryIds().map((id) => `/blog/category/${id}`),
      ...(slug ? [`/blog/${slug}`] : []),
    ];

    for (const path of paths) {
      revalidatePath(path);
    }

    return Response.json({
      revalidated: true,
      paths,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    console.error('Revalidation error:', error);
    return Response.json(
      { message: 'Error revalidating', error: String(error) },
      { status: 500 }
    );
  }
}

// Health check endpoint
export async function GET() {
  return Response.json({
    status: 'ok',
    message: 'Revalidation endpoint is active. Use POST with Authorization header to trigger revalidation.'
  });
}
