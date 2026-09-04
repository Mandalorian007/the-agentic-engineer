import { Feed } from 'feed';
import { getPublishedPosts } from '@/lib/posts';
import { remark } from 'remark';
import remarkGfm from 'remark-gfm';
import remarkHtml from 'remark-html';
import { SITE_URL, SITE_NAME, SITE_TAGLINE, AUTHOR, FEED_ID_ORIGIN } from '@/lib/site';

// Limit RSS feed to most recent posts (standard practice: 10-20 posts)
const RSS_FEED_LIMIT = 20;

/** Minimal mdast shape, so this needs no unist-util-visit dependency. */
interface MarkdownNode {
  type: string;
  url?: string;
  value?: string;
  children?: MarkdownNode[];
}

const PUBLIC_PREFIX = '../../public/';

function absolutizeUrl(url: string, postUrl: string): string {
  // Images are authored relative to the MDX file's location on disk
  if (url.startsWith(PUBLIC_PREFIX)) {
    return `${SITE_URL}/${url.slice(PUBLIC_PREFIX.length)}`;
  }
  // Site-relative, but leave protocol-relative //cdn.example.com alone
  if (url.startsWith('/') && !url.startsWith('//')) {
    return `${SITE_URL}${url}`;
  }
  // A bare fragment means nothing in an inbox; resolve it against the post
  if (url.startsWith('#')) {
    return `${postUrl}${url}`;
  }
  return url;
}

/**
 * Rewrite every relative URL to an absolute one.
 *
 * Feed readers and email clients have no site context, so a relative path is a
 * broken image or a dead link. This walks the parsed syntax tree rather than
 * string-replacing over raw markdown: `code` and `inlineCode` nodes carry no
 * url, so a markdown snippet inside a fenced block is untouched by
 * construction. A blind regex would happily rewrite the example code we
 * publish, which on this blog is most of the point.
 */
function remarkAbsoluteUrls(postUrl: string) {
  return () => (tree: MarkdownNode) => {
    const walk = (node: MarkdownNode) => {
      if (
        node.url &&
        (node.type === 'link' || node.type === 'image' || node.type === 'definition')
      ) {
        node.url = absolutizeUrl(node.url, postUrl);
      }

      // Raw HTML passed through the markdown (an <a href> or <img src>).
      // Safe to rewrite: a fenced block is a `code` node, never an `html` one.
      if (node.type === 'html' && node.value) {
        node.value = node.value.replace(
          /\b(href|src)="([^"]*)"/g,
          (_match, attribute, url) => `${attribute}="${absolutizeUrl(url, postUrl)}"`
        );
      }

      node.children?.forEach(walk);
    };

    walk(tree);
  };
}

/**
 * Convert MDX content to HTML for RSS feed
 */
async function mdxToHtml(mdxContent: string, postUrl: string): Promise<string> {
  const result = await remark()
    .use(remarkGfm)
    .use(remarkAbsoluteUrls(postUrl))
    .use(remarkHtml)
    .process(mdxContent);

  return result.toString();
}

export async function GET() {
  // Only include most recent posts (sorted by date descending)
  const posts = getPublishedPosts().slice(0, RSS_FEED_LIMIT);

  // RSS 2.0 spells <author> as "email (Name)", so the address is required or
  // the element is dropped. It is already published on /about and /services.
  const author = {
    name: AUTHOR.name,
    email: AUTHOR.email,
    link: AUTHOR.url,
  };

  const feed = new Feed({
    title: SITE_NAME,
    description: SITE_TAGLINE,
    // Identifier is frozen; link follows the canonical host.
    id: FEED_ID_ORIGIN,
    link: SITE_URL,
    language: 'en',
    // The square logo, not the 1200x630 share card. RSS 2.0 caps channel
    // <image> at 144x400 and readers enforce it, so the card renders badly or
    // gets dropped entirely.
    image: `${SITE_URL}/the-agentic-engineer-logo.webp`,
    favicon: `${SITE_URL}/favicon.ico`,
    copyright: `© ${new Date().getFullYear()} ${AUTHOR.name}`,
    // Render time, not the newest post's date, so editing an older post still
    // moves lastBuildDate and readers know to refetch.
    updated: new Date(),
    feedLinks: {
      rss: `${SITE_URL}/feed.xml`,
    },
    author,
  });

  // Add each post to the feed
  for (const post of posts) {
    const postUrl = `${SITE_URL}/blog/${post.slug}`;
    const htmlContent = await mdxToHtml(post.content, postUrl);

    feed.addItem({
      title: post.title,
      // Stable across host changes. See FEED_ID_ORIGIN.
      id: `${FEED_ID_ORIGIN}/blog/${post.slug}`,
      link: postUrl,
      description: post.description,
      content: htmlContent,
      date: new Date(post.date),
      category: [{ name: post.category }],
      image: post.heroImage ? `${SITE_URL}${post.heroImage}` : undefined,
      author: [author],
    });
  }

  return new Response(feed.rss2(), {
    headers: {
      'Content-Type': 'application/rss+xml; charset=utf-8',
      'Cache-Control': 'public, max-age=3600, s-maxage=3600',
    },
  });
}
