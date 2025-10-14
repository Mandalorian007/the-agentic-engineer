import { TwitterApi } from 'twitter-api-v2';

// Lazy-load Twitter client (only create when needed)
function getTwitterClient() {
  const client = new TwitterApi({
    appKey: process.env.TWITTER_API_KEY!,
    appSecret: process.env.TWITTER_API_KEY_SECRET!,
    accessToken: process.env.TWITTER_ACCESS_TOKEN!,
    accessSecret: process.env.TWITTER_ACCESS_TOKEN_SECRET!,
  });

  return client.readWrite;
}

export interface Post {
  title: string;
  description: string;
  slug: string;
  date: string;
}

/**
 * Tweet about a newly published blog post
 * Truncates description if needed to stay under 280 chars
 */
export async function tweetNewPost(post: Post): Promise<void> {
  const url = `https://the-agentic-engineer.com/blog/${post.slug}`;

  // Calculate available space for description
  // Format: {title}\n\n{description}\n\n{url}
  const titleLength = post.title.length;
  const urlLength = url.length;
  const newlines = 4; // Two sets of double newlines
  const maxLength = 280;
  const ellipsis = '...';

  const availableForDescription = maxLength - titleLength - urlLength - newlines - ellipsis.length;

  // Truncate description if needed
  let description = post.description;
  if (description.length > availableForDescription) {
    description = description.substring(0, availableForDescription) + ellipsis;
  }

  const tweetText = `${post.title}

${description}

${url}`;

  const client = getTwitterClient();
  await client.v2.tweet(tweetText);
  console.log(`✅ Tweeted about: ${post.title}`);
}

/**
 * Check if a post was published recently (within last 90 minutes)
 * This window accounts for ISR running hourly with some variance
 */
export function isRecentlyPublished(postDate: string): boolean {
  const now = new Date();
  const published = new Date(postDate);
  const ninetyMinutesAgo = new Date(now.getTime() - 90 * 60 * 1000);

  return published > ninetyMinutesAgo && published <= now;
}
