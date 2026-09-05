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
import { getPostBySlug, getPublishedPosts, isPublished } from "@/lib/posts";
import { getCategoryById } from "@/lib/categories";
import Image from "next/image";
import { CodeBlock } from "@/components/code-block";
import { ShareButtons } from "@/components/share-buttons";
import { TableOfContents } from "@/components/table-of-contents";
import { ReadingProgress } from "@/components/reading-progress";
import { HeadingWithAnchor } from "@/components/heading-with-anchor";
import { NewsletterCta } from "@/components/newsletter-cta";
import { AuthorSignature } from "@/components/author-signature";
import { UnpublishedBanner } from "@/components/unpublished-banner";
import { previewUnpublished } from "@/lib/preview";
import { SITE_URL, SITE_NAME, AUTHOR } from "@/lib/site";
import { extractHeadings, generateHeadingId } from "@/lib/toc";
import { formatReadingTime } from "@/lib/reading-time";
import { getHeroImagePath } from "@/lib/og-image";

// ISR: Revalidate every 1 hour (3600 seconds)
export const revalidate = 3600;

interface BlogPostPageProps {
  params: Promise<{
    slug: string;
  }>;
}

// Only published posts are prerendered. A scheduled post is still reachable
// on demand (dynamicParams defaults to true), which is what the gate below and
// preview mode are for.
export async function generateStaticParams() {
  return getPublishedPosts().map((post) => ({ slug: post.slug }));
}

// Generate metadata for SEO
export async function generateMetadata(props: BlogPostPageProps) {
  const params = await props.params;
  const post = getPostBySlug(params.slug);

  if (!post) {
    return {
      title: "Post Not Found",
      robots: { index: false, follow: false },
    };
  }

  // A scheduled post must not leak its title and description into a card, and
  // must never be indexed, even while preview mode keeps it readable.
  if (!isPublished(post)) {
    if (!previewUnpublished()) {
      return { title: "Post Not Found", robots: { index: false, follow: false } };
    }
    return {
      title: `${post.title} (preview)`,
      robots: { index: false, follow: false },
    };
  }

  // Get hero image for Open Graph and Twitter Card
  const heroImageUrl = getHeroImagePath(params.slug);
  const postUrl = `${SITE_URL}/blog/${params.slug}`;

  return {
    title: post.title,
    description: post.description,
    alternates: { canonical: postUrl },
    openGraph: {
      title: post.title,
      description: post.description,
      type: "article",
      publishedTime: post.date,
      url: postUrl,
      ...(heroImageUrl && {
        images: [
          {
            url: heroImageUrl,
            width: 1024,
            height: 1024,
            alt: post.title,
          },
        ],
      }),
    },
    ...(heroImageUrl && {
      twitter: {
        card: "summary_large_image",
        title: post.title,
        description: post.description,
        images: [heroImageUrl],
      },
    }),
  };
}

export default async function BlogPostPage(props: BlogPostPageProps) {
  const params = await props.params;
  const post = getPostBySlug(params.slug);

  if (!post) {
    notFound();
  }

  // Scheduled posts stay readable in development and on preview deployments so
  // they can be proofread as pages, and 404 in production.
  const published = isPublished(post);

  if (!published && !previewUnpublished()) {
    notFound();
  }

  const category = getCategoryById(post.category);

  // Extract headings for Table of Contents
  const headings = extractHeadings(post.content);

  // Track image index for priority loading (first image gets priority for LCP)
  let imageIndex = 0;

  // Generate JSON-LD structured data for SEO
  const jsonLd = {
    "@context": "https://schema.org",
    "@type": "BlogPosting",
    "headline": post.title,
    "description": post.description,
    "image": post.content.match(/!\[.*?\]\(\.\.\/\.\.\/public\/(.*?)\)/g)?.map(img => {
      const match = img.match(/!\[.*?\]\(\.\.\/\.\.\/public\/(.*?)\)/);
      return match ? `${SITE_URL}/${match[1]}` : null;
    }).filter(Boolean) || [],
    "datePublished": post.date,
    "dateModified": post.date,
    "author": {
      "@type": "Person",
      "name": AUTHOR.name,
      "url": AUTHOR.url,
      // Entity disambiguation for search engines: ties the byline to a real,
      // verifiable profile rather than a name string.
      "sameAs": [AUTHOR.linkedin, AUTHOR.github]
    },
    "publisher": {
      "@type": "Organization",
      "name": SITE_NAME,
      "logo": {
        "@type": "ImageObject",
        "url": `${SITE_URL}/the-agentic-engineer-logo.webp`
      }
    },
    "url": `${SITE_URL}/blog/${params.slug}`,
    "keywords": post.hashtags?.join(", ") || "",
    "articleSection": category?.name || post.category,
    "mainEntityOfPage": {
      "@type": "WebPage",
      "@id": `${SITE_URL}/blog/${params.slug}`
    }
  };

  return (
    <>
      {/* JSON-LD Structured Data. Withheld on an unpublished preview so a
          scheduled post cannot be picked up as a real article. */}
      {published && (
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
        />
      )}

      {/* Reading Progress Bar */}
      <ReadingProgress />

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
          {!published && (
            <UnpublishedBanner label="Scheduled to publish on" date={post.date} />
          )}

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
          <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-sm text-muted-foreground mb-8">
            <Link href="/about" className="font-medium text-foreground hover:underline">
              {AUTHOR.name}
            </Link>
            <span>•</span>
            <time dateTime={post.date}>
              {new Date(post.date).toLocaleDateString("en-US", {
                year: "numeric",
                month: "long",
                day: "numeric",
              })}
            </time>
            <span>•</span>
            <span>{formatReadingTime(post.readingTime)}</span>
          </div>

          <Separator className="mb-8" />

          {/* MDX Content */}
          <div className="prose prose-neutral dark:prose-invert max-w-none">
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              components={{
                // Add IDs and anchor links to headings
                h2(props) {
                  const { children } = props;
                  const text = String(children);
                  const id = generateHeadingId(text);
                  return <HeadingWithAnchor id={id} level="h2">{children}</HeadingWithAnchor>;
                },
                h3(props) {
                  const { children } = props;
                  const text = String(children);
                  const id = generateHeadingId(text);
                  return <HeadingWithAnchor id={id} level="h3">{children}</HeadingWithAnchor>;
                },
                h4(props) {
                  const { children } = props;
                  const text = String(children);
                  const id = generateHeadingId(text);
                  return <HeadingWithAnchor id={id} level="h4">{children}</HeadingWithAnchor>;
                },
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

                  // First image (hero) gets priority for LCP optimization
                  const isFirstImage = imageIndex === 0;
                  imageIndex++;

                  return (
                    <span className="block my-8">
                      <Image
                        src={imageSrc}
                        alt={alt || ''}
                        width={1200}
                        height={675}
                        className="rounded-lg"
                        priority={isFirstImage}
                        sizes="(max-width: 768px) 100vw, (max-width: 1200px) 80vw, 1200px"
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

          {/* Sign-off: put a name and a face on the argument. */}
          <div className="mt-10">
            <AuthorSignature />
          </div>

          {/* Newsletter: the highest-intent moment on the site is right here,
              when someone has just finished the whole post. */}
          <div className="mt-12">
            <NewsletterCta source={`post:${params.slug}`} />
          </div>
        </article>

        {/* Sidebar */}
        <aside className="lg:sticky lg:top-24 h-fit space-y-6">
          {/* Share This Article */}
          <ShareButtons
            url={`${SITE_URL}/blog/${params.slug}`}
            title={post.title}
          />

          {/* Table of Contents */}
          <TableOfContents headings={headings} />
        </aside>
      </div>
    </div>
    </>
  );
}
