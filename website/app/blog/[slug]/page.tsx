/**
 * Individual Blog Post Page
 * Inspired by shadcnblocks blogpost5 design
 * Features: Post content, author info, table of contents sidebar
 * TODO: Wire up with actual MDX content and rendering in Phase 3
 */

import Link from "next/link";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";

// Placeholder data - will be replaced with getPostBySlug() from lib/posts.ts
const PLACEHOLDER_POST = {
  title: "Example Blog Post",
  description: "This is a placeholder blog post.",
  date: "2025-10-12",
  category: "tutorials",
  hashtags: ["ai-agents", "python", "tutorial"],
  content: `
    <h2>Introduction</h2>
    <p>This is placeholder content. In Phase 3, we'll integrate MDX rendering with react-markdown, remark-gfm, and react-syntax-highlighter.</p>

    <h2>Section 1</h2>
    <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.</p>

    <h2>Section 2</h2>
    <p>Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p>

    <h2>Conclusion</h2>
    <p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.</p>
  `,
};

export default function BlogPostPage({
  params,
}: {
  params: { slug: string };
}) {
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
        <span className="text-foreground">{params.slug}</span>
      </nav>

      <div className="grid grid-cols-1 lg:grid-cols-[1fr_300px] gap-12">
        {/* Main Content */}
        <article>
          {/* Category Badge */}
          <div className="mb-4">
            <Badge variant="secondary">{PLACEHOLDER_POST.category}</Badge>
          </div>

          {/* Title */}
          <h1 className="text-4xl md:text-5xl font-bold mb-4">
            {PLACEHOLDER_POST.title}
          </h1>

          {/* Meta */}
          <div className="flex items-center gap-4 text-sm text-muted-foreground mb-8">
            <time dateTime={PLACEHOLDER_POST.date}>
              {new Date(PLACEHOLDER_POST.date).toLocaleDateString("en-US", {
                year: "numeric",
                month: "long",
                day: "numeric",
              })}
            </time>
          </div>

          <Separator className="mb-8" />

          {/* Content - Will be replaced with MDX rendering */}
          <div
            className="prose prose-neutral dark:prose-invert max-w-none"
            dangerouslySetInnerHTML={{ __html: PLACEHOLDER_POST.content }}
          />

          <Separator className="my-8" />

          {/* HashTags */}
          <div className="flex flex-wrap gap-2">
            {PLACEHOLDER_POST.hashtags.map((tag) => (
              <Badge key={tag} variant="outline">
                #{tag}
              </Badge>
            ))}
          </div>
        </article>

        {/* Sidebar */}
        <aside className="lg:sticky lg:top-24 h-fit">
          <div className="border rounded-lg p-6">
            <h3 className="font-semibold mb-4">On This Page</h3>
            {/* Table of Contents - will be auto-generated from headings in Phase 3 */}
            <nav className="space-y-2 text-sm">
              <Link
                href="#introduction"
                className="block text-muted-foreground hover:text-foreground"
              >
                Introduction
              </Link>
              <Link
                href="#section-1"
                className="block text-muted-foreground hover:text-foreground"
              >
                Section 1
              </Link>
              <Link
                href="#section-2"
                className="block text-muted-foreground hover:text-foreground"
              >
                Section 2
              </Link>
              <Link
                href="#conclusion"
                className="block text-muted-foreground hover:text-foreground"
              >
                Conclusion
              </Link>
            </nav>
          </div>

          {/* Share section placeholder */}
          <div className="mt-6 border rounded-lg p-6">
            <h3 className="font-semibold mb-4">Share this article</h3>
            <p className="text-sm text-muted-foreground">
              Social share buttons will be added here
            </p>
          </div>
        </aside>
      </div>
    </div>
  );
}
