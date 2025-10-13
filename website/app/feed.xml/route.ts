import { Feed } from 'feed';
import { getPublishedPosts } from '@/lib/posts';
import { remark } from 'remark';
import remarkGfm from 'remark-gfm';
import remarkHtml from 'remark-html';

const siteUrl = 'https://the-agentic-engineer.com';

// Limit RSS feed to most recent posts (standard practice: 10-20 posts)
const RSS_FEED_LIMIT = 20;

/**
 * Convert MDX content to HTML for RSS feed
 */
async function mdxToHtml(mdxContent: string): Promise<string> {
  const result = await remark()
    .use(remarkGfm)
    .use(remarkHtml)
    .process(mdxContent);

  return result.toString();
}

export async function GET() {
  // Only include most recent posts (sorted by date descending)
  const posts = getPublishedPosts().slice(0, RSS_FEED_LIMIT);

  const feed = new Feed({
    title: 'The Agentic Engineer',
    description: 'AI automation, development workflows, and agentic engineering',
    id: siteUrl,
    link: siteUrl,
    language: 'en',
    image: `${siteUrl}/og-image.png`,
    favicon: `${siteUrl}/favicon.ico`,
    copyright: `All rights reserved ${new Date().getFullYear()}, The Agentic Engineer`,
    updated: posts.length > 0 ? new Date(posts[0].date) : new Date(),
    feedLinks: {
      rss: `${siteUrl}/feed.xml`,
    },
    author: {
      name: 'The Agentic Engineer',
      link: siteUrl,
    },
  });

  // Add each post to the feed
  for (const post of posts) {
    const postUrl = `${siteUrl}/blog/${post.slug}`;
    const htmlContent = await mdxToHtml(post.content);

    feed.addItem({
      title: post.title,
      id: postUrl,
      link: postUrl,
      description: post.description,
      content: htmlContent,
      date: new Date(post.date),
      category: [{ name: post.category }],
      image: post.heroImage ? `${siteUrl}${post.heroImage}` : undefined,
    });
  }

  return new Response(feed.rss2(), {
    headers: {
      'Content-Type': 'application/rss+xml; charset=utf-8',
      'Cache-Control': 'public, max-age=3600, s-maxage=3600',
    },
  });
}
