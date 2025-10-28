import { revalidatePath } from 'next/cache';
import { NextRequest } from 'next/server';

/**
 * On-demand revalidation endpoint
 *
 * Called by GitHub Actions before posting to social media to ensure
 * pages show the latest posts before tweets go out.
 *
 * Usage:
 *   curl -X POST \
 *     -H "Authorization: Bearer YOUR_SECRET" \
 *     https://agentic-engineer.com/api/revalidate
 */
export async function POST(request: NextRequest) {
  try {
    // Security: Verify secret token
    const authHeader = request.headers.get('authorization');
    const token = authHeader?.replace('Bearer ', '');
    const expectedToken = process.env.REVALIDATE_SECRET;

    // Debug info (remove after testing)
    const debug = {
      receivedLength: token?.length || 0,
      expectedLength: expectedToken?.length || 0,
      receivedPrefix: token?.substring(0, 5) || 'none',
      expectedPrefix: expectedToken?.substring(0, 5) || 'none',
      hasWhitespace: token ? /\s/.test(token) : false,
    };

    if (!token || token !== expectedToken) {
      return Response.json(
        {
          message: 'Invalid or missing token',
          debug
        },
        { status: 401 }
      );
    }

    // Revalidate key pages that show recent posts
    revalidatePath('/');              // Home page
    revalidatePath('/blog');          // Blog listing

    // Note: Individual post pages use longer revalidate times
    // since their content doesn't change after publish

    return Response.json({
      revalidated: true,
      paths: ['/', '/blog'],
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
    message: 'Revalidation endpoint is active. Use POST with Authorization header to trigger revalidation.',
    envVarConfigured: !!process.env.REVALIDATE_SECRET,
    envVarLength: process.env.REVALIDATE_SECRET?.length || 0
  });
}
