/**
 * Category Filter Page
 * Filters blog posts by category
 * TODO: Wire up with getPostsByCategory() from lib/categories.ts in Phase 3
 */

import Link from "next/link";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

// Placeholder - will be replaced with lib/categories.ts
const CATEGORIES: Record<string, { name: string; description: string }> = {
  tutorials: {
    name: "Tutorials & How-Tos",
    description: "Step-by-step guides teaching skills and processes",
  },
  "case-studies": {
    name: "Case Studies",
    description: "Real-world project showcases and results",
  },
  guides: {
    name: "Guides & Fundamentals",
    description: "Beginner-friendly introductions to complex topics",
  },
  lists: {
    name: "Lists & Tips",
    description: "Curated collections of tools, tips, and strategies",
  },
  comparisons: {
    name: "Comparisons & Reviews",
    description: "Side-by-side comparisons and product reviews",
  },
  "problem-solution": {
    name: "Problem & Solution",
    description: "Addressing pain points with practical solutions",
  },
  opinions: {
    name: "Opinions & Analysis",
    description: "Perspectives, analysis, and myth debunking",
  },
};

// Placeholder posts - will be filtered by category in Phase 3
const PLACEHOLDER_POSTS = [
  {
    slug: "example-post-1",
    title: "Getting Started with AI Agents",
    description:
      "Learn the fundamentals of building AI agents from scratch with practical examples.",
    date: "2025-10-12",
    category: "tutorials",
    hashtags: ["ai-agents", "python", "tutorial"],
  },
];

export default function CategoryPage({
  params,
}: {
  params: { category: string };
}) {
  const categoryInfo = CATEGORIES[params.category];

  if (!categoryInfo) {
    return (
      <div className="container py-12">
        <h1 className="text-4xl font-bold">Category not found</h1>
        <p className="mt-4">
          <Link href="/blog" className="text-primary hover:underline">
            ← Back to all posts
          </Link>
        </p>
      </div>
    );
  }

  return (
    <div className="container py-12">
      {/* Breadcrumb */}
      <nav className="mb-8 text-sm text-muted-foreground">
        <Link href="/" className="hover:text-foreground">
          Home
        </Link>
        {" / "}
        <Link href="/blog" className="hover:text-foreground">
          Blog
        </Link>
        {" / "}
        <span className="text-foreground">{categoryInfo.name}</span>
      </nav>

      {/* Category Header */}
      <div className="mb-12">
        <h1 className="text-4xl font-bold mb-4">{categoryInfo.name}</h1>
        <p className="text-xl text-muted-foreground">
          {categoryInfo.description}
        </p>
      </div>

      {/* Back to All */}
      <div className="mb-8">
        <Button variant="outline" size="sm" asChild>
          <Link href="/blog">← All Posts</Link>
        </Button>
      </div>

      {/* Post Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {PLACEHOLDER_POSTS.filter((post) => post.category === params.category)
          .length > 0 ? (
          PLACEHOLDER_POSTS.filter((post) => post.category === params.category).map(
            (post) => (
              <Link key={post.slug} href={`/blog/${post.slug}`}>
                <Card className="h-full hover:border-foreground/50 transition-colors cursor-pointer">
                  <CardHeader>
                    <div className="mb-2">
                      <Badge variant="secondary">{post.category}</Badge>
                    </div>
                    <h2 className="text-2xl font-semibold mb-2">
                      {post.title}
                    </h2>
                    <p className="text-muted-foreground">{post.description}</p>
                  </CardHeader>
                  <CardContent>
                    <div className="flex flex-wrap gap-2 mb-4">
                      {post.hashtags.map((tag) => (
                        <Badge key={tag} variant="outline">
                          #{tag}
                        </Badge>
                      ))}
                    </div>
                    <p className="text-sm text-muted-foreground">{post.date}</p>
                  </CardContent>
                </Card>
              </Link>
            )
          )
        ) : (
          <div className="col-span-full text-center py-12">
            <p className="text-muted-foreground">
              No posts in this category yet.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
