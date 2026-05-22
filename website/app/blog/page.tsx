import { getPublishedPosts } from "@/lib/posts";
import { formatReadingTime } from "@/lib/reading-time";
import { CATEGORY_LABELS } from "@/lib/categories";
import { BlogIndex } from "@/components/blog-index";
import { PostCard } from "@/components/post-card";

// Enable ISR with 1-hour revalidation (future-dated posts will appear within an hour)
export const revalidate = 3600;

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

  return (
    <div className="container py-12 md:py-20">
      {/* Hero: title + description on the left, latest post card on the right */}
      <section className="flex flex-col items-start gap-10 lg:flex-row lg:items-center lg:gap-16">
        <div className="w-full max-w-[36rem] space-y-4">
          <h1 className="text-4xl font-bold tracking-tight md:text-5xl">
            Blog
          </h1>
          <p className="text-lg text-muted-foreground">
            Notes on agentic developer platforms, MCP, evals, and what
            makes AI coding tools ship inside large engineering orgs.
          </p>
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
    </div>
  );
}
