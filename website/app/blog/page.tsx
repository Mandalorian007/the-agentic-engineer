/**
 * Blog Listing Page
 * Loads real posts from content/posts and displays with blog27 layout
 */

import { getPublishedPosts } from "@/lib/posts";
import { Blog27 } from "@/components/blog27";
import { formatReadingTime } from "@/lib/reading-time";
import { tweetNewPost, isRecentlyPublished } from "@/lib/twitter";

// Enable ISR with 1-hour revalidation (future-dated posts will appear within an hour)
export const revalidate = 3600;

export default async function BlogListingPage() {
  // Get real published posts (excludes future-dated posts)
  const posts = getPublishedPosts();

  // Check for newly published posts and tweet about them
  // This runs when ISR regenerates the page (hourly)
  for (const post of posts) {
    if (isRecentlyPublished(post.date)) {
      try {
        await tweetNewPost({
          title: post.title,
          description: post.description,
          slug: post.slug,
          date: post.date,
        });
      } catch (error) {
        // Log error but don't fail the page render
        console.error(`Failed to tweet about ${post.slug}:`, error);
      }
    }
  }

  // Transform posts to blog27 format
  const transformedPosts = posts.map((post) => {
    // Extract first hero image from content for thumbnail
    const imageMatch = post.content.match(/!\[.*?\]\(\.\.\/\.\.\/public\/(.*?\.webp)\)/);
    const thumbnail = imageMatch
      ? `/${imageMatch[1]}`
      : "https://deifkwefumgah.cloudfront.net/shadcnblocks/block/placeholder-1.svg";

    return {
      category: post.category, // Pass category ID for filtering (e.g., "case-studies")
      title: post.title,
      summary: post.description,
      link: `/blog/${post.slug}`,
      cta: "Read More",
      thumbnail,
      readingTime: formatReadingTime(post.readingTime),
    };
  });

  // Use first post as primary (featured) post
  const primaryPost = transformedPosts[0] || null;
  const remainingPosts = transformedPosts.slice(1);

  return (
    <Blog27
      primaryPost={primaryPost}
      posts={remainingPosts}
    />
  );
}
