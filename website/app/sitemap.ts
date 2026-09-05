import { MetadataRoute } from 'next';
import { getPublishedPosts } from '@/lib/posts';
import { getArchivedIssues } from '@/lib/issues';
import { getAllCategoryIds, getPostsByCategory } from '@/lib/categories';
import { SITE_URL } from '@/lib/site';

/**
 * Both content streams cross into "public" by wall clock, not by deploy: a post
 * on its publish date, an issue when its archive delay elapses. A statically
 * generated sitemap would freeze that list at build time and never list them.
 */
export const revalidate = 3600;

export default function sitemap(): MetadataRoute.Sitemap {
  const baseUrl = SITE_URL;

  // Get all published posts
  const posts = getPublishedPosts();

  // Only issues past their archive delay are public
  const issues = getArchivedIssues();

  // Static pages
  const staticPages: MetadataRoute.Sitemap = [
    {
      url: baseUrl,
      lastModified: new Date(),
      changeFrequency: 'weekly',
      priority: 1.0,
    },
    {
      url: `${baseUrl}/blog`,
      lastModified: new Date(),
      changeFrequency: 'daily',
      priority: 0.9,
    },
    {
      url: `${baseUrl}/about`,
      lastModified: new Date(),
      changeFrequency: 'monthly',
      priority: 0.8,
    },
    {
      url: `${baseUrl}/services`,
      lastModified: new Date(),
      changeFrequency: 'monthly',
      priority: 0.8,
    },
    {
      url: `${baseUrl}/issues`,
      lastModified: new Date(),
      changeFrequency: 'weekly',
      priority: 0.6,
    },
    {
      url: `${baseUrl}/privacy`,
      lastModified: new Date(),
      changeFrequency: 'yearly',
      priority: 0.3,
    },
    {
      url: `${baseUrl}/terms`,
      lastModified: new Date(),
      changeFrequency: 'yearly',
      priority: 0.3,
    },
  ];

  // Category pages. An empty category renders "no posts yet", so submitting it
  // asks Google to index a blank page.
  const categoryPages: MetadataRoute.Sitemap = getAllCategoryIds()
    .filter((categoryId) => getPostsByCategory(categoryId).length > 0)
    .map((categoryId) => ({
      url: `${baseUrl}/blog/category/${categoryId}`,
      lastModified: new Date(),
      changeFrequency: 'weekly' as const,
      priority: 0.8,
    }));

  // Blog post pages
  const postPages: MetadataRoute.Sitemap = posts.map((post) => ({
    url: `${baseUrl}/blog/${post.slug}`,
    lastModified: new Date(post.date),
    changeFrequency: 'monthly' as const,
    priority: 0.7,
  }));

  // Archived newsletter issues. lastModified is the archive date, not the send
  // date: the page did not exist publicly until the delay elapsed.
  const issuePages: MetadataRoute.Sitemap = issues.map((issue) => ({
    url: `${baseUrl}/issues/${issue.slug}`,
    lastModified: new Date(issue.archiveDate),
    changeFrequency: 'yearly' as const,
    priority: 0.5,
  }));

  return [...staticPages, ...categoryPages, ...postPages, ...issuePages];
}
