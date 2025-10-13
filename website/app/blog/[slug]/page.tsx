/**
 * Individual Blog Post Page
 * Features: Real MDX content rendering, metadata, hashtags, JSON-LD, ISR revalidation
 */

import Link from "next/link";
import { notFound } from "next/navigation";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { getPostBySlug, getAllPostSlugs } from "@/lib/posts";
import { getCategoryById } from "@/lib/categories";
import Image from "next/image";
import { CodeBlock } from "@/components/code-block";

// ISR: Revalidate every 1 hour (3600 seconds)
export const revalidate = 3600;

interface BlogPostPageProps {
  params: Promise<{
    slug: string;
  }>;
}

// Generate static params for all posts
export async function generateStaticParams() {
  const slugs = getAllPostSlugs();
  return slugs.map((slug) => ({ slug }));
}

// Generate metadata for SEO
export async function generateMetadata(props: BlogPostPageProps) {
  const params = await props.params;
  const post = getPostBySlug(params.slug);

  if (!post) {
    return {
      title: "Post Not Found",
    };
  }

  return {
    title: post.title,
    description: post.description,
    openGraph: {
      title: post.title,
      description: post.description,
      type: "article",
      publishedTime: post.date,
    },
  };
}

export default async function BlogPostPage(props: BlogPostPageProps) {
  const params = await props.params;
  const post = getPostBySlug(params.slug);

  if (!post) {
    notFound();
  }

  const category = getCategoryById(post.category);

  // Generate JSON-LD structured data for SEO
  const jsonLd = {
    "@context": "https://schema.org",
    "@type": "BlogPosting",
    "headline": post.title,
    "description": post.description,
    "image": post.content.match(/!\[.*?\]\(\.\.\/\.\.\/public\/(.*?)\)/g)?.map(img => {
      const match = img.match(/!\[.*?\]\(\.\.\/\.\.\/public\/(.*?)\)/);
      return match ? `https://the-agentic-engineer.com/${match[1]}` : null;
    }).filter(Boolean) || [],
    "datePublished": post.date,
    "dateModified": post.date,
    "author": {
      "@type": "Person",
      "name": "The Agentic Engineer"
    },
    "publisher": {
      "@type": "Organization",
      "name": "The Agentic Engineer",
      "logo": {
        "@type": "ImageObject",
        "url": "https://the-agentic-engineer.com/logo.png"
      }
    },
    "url": `https://the-agentic-engineer.com/blog/${params.slug}`,
    "keywords": post.hashtags?.join(", ") || "",
    "articleSection": category?.name || post.category,
    "mainEntityOfPage": {
      "@type": "WebPage",
      "@id": `https://the-agentic-engineer.com/blog/${params.slug}`
    }
  };

  return (
    <>
      {/* JSON-LD Structured Data */}
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />

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
        <span className="text-foreground">{post.title}</span>
      </nav>

      <div className="grid grid-cols-1 lg:grid-cols-[1fr_300px] gap-12">
        {/* Main Content */}
        <article>
          {/* Category Badge */}
          <div className="mb-4">
            <Link href={`/blog/category/${post.category}`}>
              <Badge variant="secondary" className="cursor-pointer hover:bg-secondary/80">
                {category?.name || post.category}
              </Badge>
            </Link>
          </div>

          {/* Title */}
          <h1 className="text-4xl md:text-5xl font-bold mb-4">
            {post.title}
          </h1>

          {/* Meta */}
          <div className="flex items-center gap-4 text-sm text-muted-foreground mb-8">
            <time dateTime={post.date}>
              {new Date(post.date).toLocaleDateString("en-US", {
                year: "numeric",
                month: "long",
                day: "numeric",
              })}
            </time>
          </div>

          <Separator className="mb-8" />

          {/* MDX Content */}
          <div className="prose prose-neutral dark:prose-invert max-w-none">
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              components={{
                // Custom code block with syntax highlighting
                code(props) {
                  const { children, className, ...rest } = props;
                  const match = /language-(\w+)/.exec(className || '');

                  // Multi-line code block with theme-aware syntax highlighting
                  if (match) {
                    return (
                      <CodeBlock language={match[1]}>
                        {String(children).replace(/\n$/, '')}
                      </CodeBlock>
                    );
                  }

                  // Inline code - let @tailwindcss/typography handle styling
                  return <code {...rest}>{children}</code>;
                },
                // Custom image component with Next.js Image
                img({ src, alt }) {
                  // Handle relative image paths from MDX file location
                  const srcString = typeof src === 'string' ? src : '';

                  // Convert ../../public/blog/... to /blog/...
                  let imageSrc = srcString;
                  if (srcString.startsWith('../../public/')) {
                    imageSrc = srcString.replace('../../public', '');
                  } else if (srcString.startsWith('./')) {
                    // Legacy support: ./image.webp -> /blog/{slug}/image.webp
                    imageSrc = `/blog/${params.slug}/${srcString.slice(2)}`;
                  }

                  return (
                    <span className="block my-8">
                      <Image
                        src={imageSrc}
                        alt={alt || ''}
                        width={1200}
                        height={675}
                        className="rounded-lg"
                        priority={false}
                        unoptimized
                      />
                    </span>
                  );
                },
              }}
            >
              {post.content}
            </ReactMarkdown>
          </div>

          <Separator className="my-8" />

          {/* HashTags */}
          {post.hashtags && post.hashtags.length > 0 && (
            <div className="flex flex-wrap gap-2">
              {post.hashtags.map((tag) => (
                <Badge key={tag} variant="outline">
                  #{tag}
                </Badge>
              ))}
            </div>
          )}
        </article>

        {/* Sidebar */}
        <aside className="lg:sticky lg:top-24 h-fit">
          <div className="border rounded-lg p-6">
            <h3 className="font-semibold mb-4">About This Post</h3>
            <div className="space-y-3 text-sm">
              <div>
                <p className="text-muted-foreground mb-1">Category</p>
                <Link href={`/blog/category/${post.category}`}>
                  <Badge variant="secondary" className="cursor-pointer hover:bg-secondary/80">
                    {category?.name || post.category}
                  </Badge>
                </Link>
              </div>
              <div>
                <p className="text-muted-foreground mb-1">Published</p>
                <p className="font-medium">
                  {new Date(post.date).toLocaleDateString("en-US", {
                    year: "numeric",
                    month: "long",
                    day: "numeric",
                  })}
                </p>
              </div>
            </div>
          </div>

          {/* Navigation */}
          <div className="mt-6 border rounded-lg p-6">
            <h3 className="font-semibold mb-4">Navigation</h3>
            <div className="space-y-2 text-sm">
              <Link
                href="/blog"
                className="block text-muted-foreground hover:text-foreground"
              >
                ← All Posts
              </Link>
              <Link
                href={`/blog/category/${post.category}`}
                className="block text-muted-foreground hover:text-foreground"
              >
                More in {category?.name}
              </Link>
            </div>
          </div>
        </aside>
      </div>
    </div>
    </>
  );
}
