/**
 * Blog Listing Page
 * Inspired by shadcnblocks blog27 design
 * Features: Category filters, post cards, pagination
 * TODO: Wire up with actual MDX content in Phase 3
 */

import Link from "next/link";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

// Placeholder data - will be replaced with actual posts from lib/posts.ts
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
  {
    slug: "example-post-2",
    title: "Voice to Blog Automation Case Study",
    description:
      "How I built an automated blog publishing pipeline using Claude Code and Python.",
    date: "2025-10-11",
    category: "case-studies",
    hashtags: ["automation", "claude-code", "workflow"],
  },
  {
    slug: "example-post-3",
    title: "Understanding Context Windows",
    description:
      "A comprehensive guide to managing context in large language models.",
    date: "2025-10-10",
    category: "guides",
    hashtags: ["llm", "context", "fundamentals"],
  },
];

const CATEGORIES = [
  { id: "all", name: "All" },
  { id: "tutorials", name: "Tutorials" },
  { id: "case-studies", name: "Case Studies" },
  { id: "guides", name: "Guides" },
  { id: "lists", name: "Lists & Tips" },
  { id: "comparisons", name: "Comparisons" },
  { id: "problem-solution", name: "Problem & Solution" },
  { id: "opinions", name: "Opinions" },
];

export default function BlogListingPage() {
  return (
    <div className="container py-12">
      {/* Header */}
      <div className="mb-12">
        <h1 className="text-4xl font-bold mb-4">Blog</h1>
        <p className="text-xl text-muted-foreground max-w-2xl">
          Explore articles about AI agents, automation, and engineering best
          practices.
        </p>
      </div>

      {/* Category Filters */}
      <div className="mb-8 flex flex-wrap gap-2">
        {CATEGORIES.map((category) => (
          <Button
            key={category.id}
            variant={category.id === "all" ? "default" : "outline"}
            size="sm"
            asChild
          >
            <Link
              href={
                category.id === "all"
                  ? "/blog"
                  : `/blog/category/${category.id}`
              }
            >
              {category.name}
            </Link>
          </Button>
        ))}
      </div>

      {/* Post Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {PLACEHOLDER_POSTS.map((post) => (
          <Link key={post.slug} href={`/blog/${post.slug}`}>
            <Card className="h-full hover:border-foreground/50 transition-colors cursor-pointer">
              <CardHeader>
                <div className="mb-2">
                  <Badge variant="secondary">{post.category}</Badge>
                </div>
                <h2 className="text-2xl font-semibold mb-2">{post.title}</h2>
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
        ))}
      </div>

      {/* Load More - Placeholder */}
      <div className="mt-12 text-center">
        <Button variant="outline" size="lg">
          Load More
        </Button>
      </div>
    </div>
  );
}
