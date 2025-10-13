/**
 * Category Filter Page
 * Filters blog posts by category with ISR revalidation
 */

import Link from "next/link";
import { notFound } from "next/navigation";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { getCategoryById, getPostsByCategory, getAllCategoryIds } from "@/lib/categories";

// ISR: Revalidate every 1 hour (3600 seconds)
export const revalidate = 3600;

interface CategoryPageProps {
  params: Promise<{
    category: string;
  }>;
}

// Generate static params for all categories
export async function generateStaticParams() {
  const categoryIds = getAllCategoryIds();
  return categoryIds.map((categoryId) => ({ category: categoryId }));
}

// Generate metadata for SEO
export async function generateMetadata(props: CategoryPageProps) {
  const params = await props.params;
  const categoryInfo = getCategoryById(params.category);

  if (!categoryInfo) {
    return {
      title: "Category Not Found",
    };
  }

  return {
    title: `${categoryInfo.name} | The Agentic Engineer`,
    description: categoryInfo.description,
    openGraph: {
      title: `${categoryInfo.name} | The Agentic Engineer`,
      description: categoryInfo.description,
      type: "website",
    },
  };
}

export default async function CategoryPage(props: CategoryPageProps) {
  const params = await props.params;
  const categoryInfo = getCategoryById(params.category);

  if (!categoryInfo) {
    notFound();
  }

  // Get posts for this category
  const posts = getPostsByCategory(params.category);

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
        {posts.length > 0 ? (
          posts.map((post) => (
            <Link key={post.slug} href={`/blog/${post.slug}`}>
              <Card className="h-full hover:border-foreground/50 transition-colors cursor-pointer">
                <CardHeader>
                  <div className="mb-2">
                    <Badge variant="secondary">{categoryInfo.name}</Badge>
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
                  <p className="text-sm text-muted-foreground">
                    {new Date(post.date).toLocaleDateString("en-US", {
                      year: "numeric",
                      month: "long",
                      day: "numeric",
                    })}
                  </p>
                </CardContent>
              </Card>
            </Link>
          ))
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
