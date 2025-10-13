import { Post, getPublishedPosts } from './posts';

/**
 * Hardcoded category definitions
 * Aligned with /create-post command blog formats
 */
export const CATEGORIES = {
  'tutorials': {
    name: 'Tutorials & How-Tos',
    description: 'Step-by-step guides teaching skills and processes'
  },
  'case-studies': {
    name: 'Case Studies',
    description: 'Real-world project showcases and results'
  },
  'guides': {
    name: 'Guides & Fundamentals',
    description: 'Beginner-friendly introductions to complex topics'
  },
  'lists': {
    name: 'Lists & Tips',
    description: 'Curated collections of tools, tips, and strategies'
  },
  'comparisons': {
    name: 'Comparisons & Reviews',
    description: 'Side-by-side comparisons and product reviews'
  },
  'problem-solution': {
    name: 'Problem & Solution',
    description: 'Addressing pain points with practical solutions'
  },
  'opinions': {
    name: 'Opinions & Analysis',
    description: 'Perspectives, analysis, and myth debunking'
  }
} as const;

export type CategoryId = keyof typeof CATEGORIES;

/**
 * Get category metadata by ID
 */
export function getCategoryById(categoryId: string) {
  if (categoryId in CATEGORIES) {
    return CATEGORIES[categoryId as CategoryId];
  }
  return null;
}

/**
 * Get all category IDs
 */
export function getAllCategoryIds(): CategoryId[] {
  return Object.keys(CATEGORIES) as CategoryId[];
}

/**
 * Get posts filtered by category
 */
export function getPostsByCategory(categoryId: string): Post[] {
  const posts = getPublishedPosts();
  return posts.filter((post) => post.category === categoryId);
}

/**
 * Get post count per category
 */
export function getCategoryCounts(): Record<string, number> {
  const posts = getPublishedPosts();
  const counts: Record<string, number> = {};

  // Initialize all categories with 0
  Object.keys(CATEGORIES).forEach((categoryId) => {
    counts[categoryId] = 0;
  });

  // Count posts per category
  posts.forEach((post) => {
    if (post.category in counts) {
      counts[post.category]++;
    }
  });

  return counts;
}

/**
 * Validate if a category ID is valid
 */
export function isValidCategory(categoryId: string): boolean {
  return categoryId in CATEGORIES;
}
