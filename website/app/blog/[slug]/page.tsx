/**
 * Individual Blog Post Page
 * Features: Real MDX content rendering, metadata, hashtags
 */

import Link from "next/link";
import { notFound } from "next/navigation";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { oneDark } from "react-syntax-highlighter/dist/esm/styles/prism";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { getPostBySlug, getAllPostSlugs } from "@/lib/posts";
import { getCategoryById } from "@/lib/categories";
import Image from "next/image";

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
                  // Destructure incompatible props to avoid type conflicts
                  const { children, className, style, ref, ...rest } = props;
                  const match = /language-(\w+)/.exec(className || '');

                  // Multi-line code block with syntax highlighting
                  if (match) {
                    return (
                      <SyntaxHighlighter
                        style={oneDark}
                        language={match[1]}
                        PreTag="div"
                        {...rest}
                      >
                        {String(children).replace(/\n$/, '')}
                      </SyntaxHighlighter>
                    );
                  }

                  // Inline code with oneDark theme styling (matches react-syntax-highlighter)
                  return (
                    <code
                      className="relative rounded px-[0.4rem] py-[0.2rem] font-mono text-sm font-normal border"
                      style={{
                        backgroundColor: '#282c34',
                        color: '#abb2bf',
                        borderColor: 'rgba(171, 178, 191, 0.15)',
                      }}
                      {...rest}
                    >
                      {children}
                    </code>
                  );
                },
                // Custom image component with Next.js Image
                img({ src, alt }) {
                  // Handle relative image paths
                  const srcString = typeof src === 'string' ? src : '';
                  const imageSrc = srcString.startsWith('./')
                    ? `/blog/${params.slug}/${srcString.slice(2)}`
                    : srcString;

                  return (
                    <span className="block my-8">
                      <Image
                        src={imageSrc}
                        alt={alt || ''}
                        width={1200}
                        height={675}
                        className="rounded-lg"
                        priority={false}
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
  );
}
