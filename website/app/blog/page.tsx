/**
 * Blog listing.
 *
 * Hero with the latest post, then the filterable index. Scheduled posts are
 * listed separately and only while previewing, so it is never ambiguous which
 * ones a reader can actually see.
 */

import type { Metadata } from "next";
import { getAllPosts, getPublishedPosts, isPublished } from "@/lib/posts";
import { formatReadingTime } from "@/lib/reading-time";
import { CATEGORY_LABELS } from "@/lib/categories";
import { BlogIndex } from "@/components/blog-index";
import { PostCard } from "@/components/post-card";
import { NewsletterCta } from "@/components/newsletter-cta";
import { PreviewList } from "@/components/preview-list";
import { previewUnpublished } from "@/lib/preview";

// Enable ISR with 1-hour revalidation (future-dated posts will appear within an hour)
export const revalidate = 3600;

const BLOG_TITLE = "Blog";
const BLOG_DESCRIPTION =
  "Tutorials and field notes on encoding what you already know into agent workflows: hooks, commands, evals, and the guardrails that make them safe to run.";

export const metadata: Metadata = {
  title: BLOG_TITLE,
  description: BLOG_DESCRIPTION,
  alternates: { canonical: "/blog" },
  openGraph: { title: BLOG_TITLE, description: BLOG_DESCRIPTION, url: "/blog" },
};

const CATEGORIES = [
  { label: "All", value: "all" },
  { label: "Tutorials", value: "tutorials" },
  { label: "Case Studies", value: "case-studies" },
  { label: "Guides", value: "guides" },
  { label: "Lists & Tips", value: "lists" },
  { label: "Comparisons", value: "comparisons" },
  { label: "Problem & Solution", value: "problem-solution" },
  { label: "Opinions", value: "opinions" },
];

export default function BlogListingPage() {
  const allPosts = getPublishedPosts().map((post) => ({
    slug: post.slug,
    title: post.title,
    description: post.description,
    date: post.date,
    category: post.category,
    categoryLabel:
      CATEGORY_LABELS[post.category as keyof typeof CATEGORY_LABELS] ??
      post.category,
    readingTime: formatReadingTime(post.readingTime),
    heroImage: post.heroImage,
  }));

  const latest = allPosts[0];
  const rest = allPosts.slice(1);

  const scheduled = previewUnpublished()
    ? getAllPosts()
        .filter((post) => !isPublished(post))
        .map((post) => ({
          slug: post.slug,
          title: post.title,
          href: `/blog/${post.slug}`,
          date: post.date,
        }))
    : [];

  return (
    <div className="container py-12 md:py-20">
      {/* Hero: title + description on the left, latest post card on the right */}
      <section className="flex flex-col items-start gap-10 lg:flex-row lg:items-center lg:gap-16">
        <div className="w-full max-w-[36rem] space-y-4">
          <h1 className="text-4xl font-bold tracking-tight md:text-5xl">
            {BLOG_TITLE}
          </h1>
          <p className="text-lg text-muted-foreground">{BLOG_DESCRIPTION}</p>
        </div>
        {latest && (
          <div className="w-full lg:max-w-[28rem]">
            <p className="mb-3 text-[10px] font-semibold uppercase tracking-[0.12em] text-muted-foreground">
              Latest post
            </p>
            <PostCard
              slug={latest.slug}
              title={latest.title}
              description={latest.description}
              date={latest.date}
              categoryLabel={latest.categoryLabel}
              readingTime={latest.readingTime}
              heroImage={latest.heroImage}
              priority
            />
          </div>
        )}
      </section>

      <div className="mt-16">
        <BlogIndex posts={rest} categories={CATEGORIES} />
      </div>

      {scheduled.length > 0 && (
        <PreviewList
          heading="Scheduled"
          emptyLabel="Visible because preview mode is on. Dates shown are when each post goes live."
          items={scheduled}
        />
      )}

      <div className="mt-16">
        <NewsletterCta source="blog-index" />
      </div>
    </div>
  );
}
