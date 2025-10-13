/**
 * Blog Listing Page
 * Loads real posts from content/posts and displays with blog27 layout
 */

import { getPublishedPosts } from "@/lib/posts";
import { Blog27 } from "@/components/blog27";
import { formatReadingTime } from "@/lib/reading-time";

// Enable ISR with 1-hour revalidation (future-dated posts will appear within an hour)
export const revalidate = 3600;

export default function BlogListingPage() {
  // Get real published posts (excludes future-dated posts)
  const posts = getPublishedPosts();

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
