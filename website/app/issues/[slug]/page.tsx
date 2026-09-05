/**
 * A single archived newsletter issue.
 *
 * Gating happens here, not only in generateStaticParams. dynamicParams defaults
 * to true, so Next will happily render an unlisted slug on demand; both layers
 * are required to keep an unsent issue private.
 *
 * Preview mode opens the gate in development and on preview deployments so a
 * pre-written issue can be proofread as a page. Those renders are noindex.
 */

import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { CodeBlock } from "@/components/code-block";
import { HeadingWithAnchor } from "@/components/heading-with-anchor";
import { NewsletterCta } from "@/components/newsletter-cta";
import { AuthorSignature } from "@/components/author-signature";
import { UnpublishedBanner } from "@/components/unpublished-banner";
import { getIssueBySlug, getArchivedIssueSlugs, isArchived } from "@/lib/issues";
import { previewUnpublished } from "@/lib/preview";
import { generateHeadingId } from "@/lib/toc";
import { formatReadingTime } from "@/lib/reading-time";
import { AUTHOR, SITE_URL, NEWSLETTER_NAME } from "@/lib/site";

export const revalidate = 3600;

interface IssuePageProps {
  params: Promise<{ slug: string }>;
}

export async function generateStaticParams() {
  return getArchivedIssueSlugs().map((slug) => ({ slug }));
}

export async function generateMetadata(
  props: IssuePageProps,
): Promise<Metadata> {
  const params = await props.params;
  const issue = getIssueBySlug(params.slug);

  if (!issue) {
    return { title: "Not Found", robots: { index: false, follow: false } };
  }

  // A previewable issue still must not be indexed, and must not leak its
  // description into a card before subscribers have seen it.
  if (!isArchived(issue)) {
    if (!previewUnpublished()) {
      return { title: "Not Found", robots: { index: false, follow: false } };
    }
    return {
      title: `${issue.title} (preview)`,
      robots: { index: false, follow: false },
    };
  }

  const url = `${SITE_URL}/issues/${params.slug}`;

  return {
    title: issue.title,
    description: issue.description,
    alternates: { canonical: url },
    openGraph: {
      title: issue.title,
      description: issue.description,
      type: "article",
      publishedTime: issue.archiveDate,
      url,
      // Next assigns openGraph wholesale rather than merging it, so omitting
      // images here would drop the layout's card and share as a bare link.
      images: [{ url: "/og", width: 1200, height: 630, alt: issue.title }],
    },
    twitter: {
      card: "summary_large_image",
      title: issue.title,
      description: issue.description,
      images: ["/og"],
    },
  };
}

export default async function IssuePage(props: IssuePageProps) {
  const params = await props.params;
  const issue = getIssueBySlug(params.slug);

  if (!issue) {
    notFound();
  }

  // An issue that has not been sent, or is still inside its archive delay,
  // does not exist as far as the public site is concerned.
  const archived = isArchived(issue);

  if (!archived && !previewUnpublished()) {
    notFound();
  }

  const jsonLd = {
    "@context": "https://schema.org",
    "@type": "BlogPosting",
    headline: issue.title,
    description: issue.description,
    datePublished: issue.archiveDate,
    dateModified: issue.archiveDate,
    author: {
      "@type": "Person",
      name: AUTHOR.name,
      url: AUTHOR.url,
    },
    isPartOf: {
      "@type": "PublicationIssue",
      name: NEWSLETTER_NAME,
    },
    url: `${SITE_URL}/issues/${params.slug}`,
    mainEntityOfPage: {
      "@type": "WebPage",
      "@id": `${SITE_URL}/issues/${params.slug}`,
    },
  };

  return (
    <>
      {archived && (
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
        />
      )}

      <div className="container py-12">
        <nav className="mb-8 text-sm text-muted-foreground">
          <Link href="/" className="hover:text-foreground">
            Home
          </Link>
          {" / "}
          <Link href="/issues" className="hover:text-foreground">
            Issues
          </Link>
          {" / "}
          <span className="text-foreground">{issue.title}</span>
        </nav>

        <article className="mx-auto max-w-3xl">
          {!archived && (
            <UnpublishedBanner
              label="This issue reaches the archive on"
              date={issue.archiveDate}
            />
          )}

          <div className="mb-4">
            <Badge variant="secondary">{NEWSLETTER_NAME}</Badge>
          </div>

          <h1 className="mb-4 text-4xl font-bold md:text-5xl">{issue.title}</h1>

          <div className="mb-8 flex flex-wrap items-center gap-x-4 gap-y-1 text-sm text-muted-foreground">
            <Link
              href="/about"
              className="font-medium text-foreground hover:underline"
            >
              {AUTHOR.name}
            </Link>
            <span>•</span>
            <time dateTime={issue.date}>
              Sent{" "}
              {new Date(issue.date).toLocaleDateString("en-US", {
                year: "numeric",
                month: "long",
                day: "numeric",
              })}
            </time>
            <span>•</span>
            <span>{formatReadingTime(issue.readingTime)}</span>
          </div>

          <Separator className="mb-8" />

          <div className="prose prose-neutral dark:prose-invert max-w-none">
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              components={{
                h2(props) {
                  const { children } = props;
                  return (
                    <HeadingWithAnchor
                      id={generateHeadingId(String(children))}
                      level="h2"
                    >
                      {children}
                    </HeadingWithAnchor>
                  );
                },
                h3(props) {
                  const { children } = props;
                  return (
                    <HeadingWithAnchor
                      id={generateHeadingId(String(children))}
                      level="h3"
                    >
                      {children}
                    </HeadingWithAnchor>
                  );
                },
                h4(props) {
                  const { children } = props;
                  return (
                    <HeadingWithAnchor
                      id={generateHeadingId(String(children))}
                      level="h4"
                    >
                      {children}
                    </HeadingWithAnchor>
                  );
                },
                code(props) {
                  const { children, className, ...rest } = props;
                  const match = /language-(\w+)/.exec(className || "");

                  if (match) {
                    return (
                      <CodeBlock language={match[1]}>
                        {String(children).replace(/\n$/, "")}
                      </CodeBlock>
                    );
                  }

                  return <code {...rest}>{children}</code>;
                },
                // Issues are not supposed to carry images, but an author-relative
                // path would otherwise render as a silently broken <img>. Rewrite
                // it to a site path so the failure is visible, not invisible.
                img({ src, alt }) {
                  const srcString = typeof src === "string" ? src : "";
                  const imageSrc = srcString.startsWith("../../public/")
                    ? srcString.replace("../../public", "")
                    : srcString;

                  // eslint-disable-next-line @next/next/no-img-element
                  return <img src={imageSrc} alt={alt || ""} loading="lazy" />;
                },
              }}
            >
              {issue.content}
            </ReactMarkdown>
          </div>

          <Separator className="my-8" />

          <AuthorSignature />

          <div className="mt-12">
            <NewsletterCta source={`issue:${params.slug}`} />
          </div>

          <p className="mt-8 text-sm text-muted-foreground">
            <Link href="/issues" className="hover:text-foreground">
              ← All issues
            </Link>
            <span className="mx-3">·</span>
            <Link href="/blog" className="hover:text-foreground">
              Read the blog →
            </Link>
          </p>
        </article>
      </div>
    </>
  );
}
