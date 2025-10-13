import { MetadataRoute } from 'next';
import { getPublishedPosts } from '@/lib/posts';
import { getAllCategoryIds } from '@/lib/categories';

export default function sitemap(): MetadataRoute.Sitemap {
  const baseUrl = 'https://the-agentic-engineer.com';

  // Get all published posts
  const posts = getPublishedPosts();

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
  ];

  // Category pages
  const categoryPages: MetadataRoute.Sitemap = getAllCategoryIds().map(
    (categoryId) => ({
      url: `${baseUrl}/blog/category/${categoryId}`,
      lastModified: new Date(),
      changeFrequency: 'weekly' as const,
      priority: 0.8,
    })
  );

  // Blog post pages
  const postPages: MetadataRoute.Sitemap = posts.map((post) => ({
    url: `${baseUrl}/blog/${post.slug}`,
    lastModified: new Date(post.date),
    changeFrequency: 'monthly' as const,
    priority: 0.7,
  }));

  return [...staticPages, ...categoryPages, ...postPages];
}
