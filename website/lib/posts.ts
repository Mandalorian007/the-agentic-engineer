import fs from 'fs';
import path from 'path';
import matter from 'gray-matter';
import { calculateReadingTime } from './reading-time';

const postsDirectory = path.join(process.cwd(), 'content/posts');

export interface Post {
  slug: string;
  title: string;
  description: string;
  date: string;
  category: string;
  hashtags: string[];
  content: string;
  heroImage?: string;
  readingTime: number;
}

/**
 * Get all posts from content/posts directory
 * Posts are sorted by date descending (newest first)
 */
export function getAllPosts(): Post[] {
  // Get all MDX files
  const fileNames = fs.readdirSync(postsDirectory);

  const posts = fileNames
    .filter((fileName) => fileName.endsWith('.mdx'))
    .map((fileName) => {
      // Extract slug from filename (remove .mdx extension)
      const slug = fileName.replace(/\.mdx$/, '');

      // Read file contents
      const fullPath = path.join(postsDirectory, fileName);
      const fileContents = fs.readFileSync(fullPath, 'utf8');

      // Parse frontmatter
      const { data, content } = matter(fileContents);

      // Extract hero image from content (first image reference)
      const heroImageMatch = content.match(/!\[.*?\]\((\.\.\/\.\.\/public\/blog\/[^)]+)\)/);
      const heroImage = heroImageMatch ? heroImageMatch[1].replace('../../public', '') : undefined;

      return {
        slug,
        title: data.title,
        description: data.description,
        date: data.date,
        category: data.category,
        hashtags: data.hashtags || [],
        content,
        heroImage,
        readingTime: calculateReadingTime(content),
      } as Post;
    });

  // Sort by date descending
  return posts.sort((a, b) => {
    const dateA = new Date(a.date).getTime();
    const dateB = new Date(b.date).getTime();
    return dateB - dateA;
  });
}

/**
 * Get only published posts (excludes future-dated posts)
 * Filters out posts with dates in the future
 */
export function getPublishedPosts(): Post[] {
  const allPosts = getAllPosts();
  const now = new Date();

  return allPosts.filter((post) => {
    const postDate = new Date(post.date);
    return postDate <= now;
  });
}

/**
 * Get a single post by slug
 * Returns null if post not found
 */
export function getPostBySlug(slug: string): Post | null {
  try {
    const fullPath = path.join(postsDirectory, `${slug}.mdx`);
    const fileContents = fs.readFileSync(fullPath, 'utf8');

    const { data, content } = matter(fileContents);

    // Extract hero image from content (first image reference)
    const heroImageMatch = content.match(/!\[.*?\]\((\.\.\/\.\.\/public\/blog\/[^)]+)\)/);
    const heroImage = heroImageMatch ? heroImageMatch[1].replace('../../public', '') : undefined;

    return {
      slug,
      title: data.title,
      description: data.description,
      date: data.date,
      category: data.category,
      hashtags: data.hashtags || [],
      content,
      heroImage,
      readingTime: calculateReadingTime(content),
    } as Post;
  } catch {
    return null;
  }
}

/**
 * Get recent published posts (limit to N posts)
 * Only returns posts that are already published (not future-dated)
 */
export function getRecentPosts(limit: number = 3): Post[] {
  const publishedPosts = getPublishedPosts();
  return publishedPosts.slice(0, limit);
}

/**
 * Get all unique slugs for static generation
 */
export function getAllPostSlugs(): string[] {
  const fileNames = fs.readdirSync(postsDirectory);
  return fileNames
    .filter((fileName) => fileName.endsWith('.mdx'))
    .map((fileName) => fileName.replace(/\.mdx$/, ''));
}
