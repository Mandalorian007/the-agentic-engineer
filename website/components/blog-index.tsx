"use client";

import { useMemo, useState } from "react";
import { Button } from "@/components/ui/button";
import { PostCard } from "@/components/post-card";

interface IndexPost {
  slug: string;
  title: string;
  description: string;
  date: string;
  category: string;
  categoryLabel: string;
  readingTime: string;
  heroImage?: string;
}

interface Category {
  label: string;
  value: string;
}

interface BlogIndexProps {
  posts: IndexPost[];
  categories: Category[];
}

const POSTS_PER_PAGE = 16;

export function BlogIndex({ posts, categories }: BlogIndexProps) {
  const [activeCategory, setActiveCategory] = useState<string>("all");
  const [visibleCount, setVisibleCount] = useState(POSTS_PER_PAGE);

  const filtered = useMemo(() => {
    if (activeCategory === "all") return posts;
    return posts.filter((post) => post.category === activeCategory);
  }, [activeCategory, posts]);

  const visible = filtered.slice(0, visibleCount);
  const hasMore = visibleCount < filtered.length;

  const handleCategoryChange = (value: string) => {
    setActiveCategory(value);
    setVisibleCount(POSTS_PER_PAGE);
  };

  return (
    <div className="space-y-8">
      {/* Filter pills */}
      <div className="flex flex-wrap items-center gap-2">
        {categories.map((cat) => {
          const active = cat.value === activeCategory;
          return (
            <button
              key={cat.value}
              type="button"
              onClick={() => handleCategoryChange(cat.value)}
              className={`rounded-full px-3.5 py-1.5 text-sm font-medium transition-colors ${
                active
                  ? "bg-foreground text-background"
                  : "border border-border text-muted-foreground hover:border-foreground/30 hover:text-foreground"
              }`}
            >
              {cat.label}
            </button>
          );
        })}
      </div>

      {/* Grid header — count + structural divider */}
      <div className="flex items-baseline justify-between border-t border-border pt-4">
        <p className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
          {filtered.length} {filtered.length === 1 ? "post" : "posts"}
          {activeCategory !== "all" && (
            <span className="ml-2 font-normal normal-case tracking-normal text-muted-foreground/70">
              in {categories.find((c) => c.value === activeCategory)?.label}
            </span>
          )}
        </p>
      </div>

      {/* Empty state */}
      {filtered.length === 0 ? (
        <div className="flex min-h-[200px] items-center justify-center rounded-lg border border-dashed">
          <div className="space-y-2 p-8 text-center">
            <p className="text-sm font-medium text-muted-foreground">
              No posts in this category yet.
            </p>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => handleCategoryChange("all")}
            >
              Show all posts
            </Button>
          </div>
        </div>
      ) : (
        <>
          <div className="grid grid-cols-1 gap-x-5 gap-y-8 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
            {visible.map((post, index) => (
              <PostCard
                key={post.slug}
                slug={post.slug}
                title={post.title}
                description={post.description}
                date={post.date}
                categoryLabel={post.categoryLabel}
                readingTime={post.readingTime}
                heroImage={post.heroImage}
                priority={index < 4}
              />
            ))}
          </div>
          {hasMore && (
            <div className="flex justify-center pt-2">
              <Button
                variant="outline"
                onClick={() => setVisibleCount((n) => n + POSTS_PER_PAGE)}
              >
                Load more
              </Button>
            </div>
          )}
        </>
      )}
    </div>
  );
}
