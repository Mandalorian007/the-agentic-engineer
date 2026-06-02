import { Post, getPublishedPosts } from './posts';

/**
 * Hardcoded category definitions
 * Aligned with /create-post command blog formats
 *
 * SELECTION RULE — classify by READER INTENT, not dominant wordcount.
 * Ask "what would a reader search or filter to FIND this post?" and honor the
 * title's promise when the post delivers on it. A how-to with a strong opinion
 * is still a `tutorial`. An "X vs Y" post is a `comparison` even if its thesis
 * is "it doesn't matter." An explainer answering "what is X" is a `guide`.
 * `opinions` is the bucket where the ARGUMENT is the deliverable — reach for it
 * last, never as a fallback for any post that merely carries a point of view.
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
    description: 'Explainers and introductions that make a complex topic make sense'
  },
  'lists': {
    name: 'Lists & Tips',
    description: 'Curated collections of tools, tips, and strategies'
  },
  'comparisons': {
    name: 'Comparisons & Reviews',
    description: 'Side-by-side "X vs Y" decisions and product reviews'
  },
  'problem-solution': {
    name: 'Problem & Solution',
    description: 'Addressing pain points with practical solutions'
  },
  'opinions': {
    name: 'Opinions & Analysis',
    description: 'Posts where the argument itself is the takeaway — perspective, analysis, myth-debunking'
  }
} as const;

export type CategoryId = keyof typeof CATEGORIES;

/**
 * Simple category labels for display
 */
export const CATEGORY_LABELS: Record<CategoryId, string> = {
  'tutorials': 'Tutorials & How-Tos',
  'case-studies': 'Case Studies',
  'guides': 'Guides & Fundamentals',
  'lists': 'Lists & Tips',
  'comparisons': 'Comparisons & Reviews',
  'problem-solution': 'Problem & Solution',
  'opinions': 'Opinions & Analysis',
};

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
