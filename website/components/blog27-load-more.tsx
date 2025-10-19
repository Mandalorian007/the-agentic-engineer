"use client";
import { useCallback, useMemo, useState } from "react";
import { Button } from "@/components/ui/button";
import { FilterForm } from "@/components/blog27-filter";
import { BlogCard } from "@/components/blog-card";

interface Post {
  category: string;
  title: string;
  summary: string;
  link: string;
  cta: string;
  thumbnail: string;
  readingTime?: string;
  isPrimary?: boolean;
}

interface Category {
  label: string;
  value: string;
}

interface BlogsResultProps {
  posts: Array<Post>;
  categories: Array<Category>;
  postsPerPage?: number;
}

export const BlogsResult = ({ posts, categories, postsPerPage = 6 }: BlogsResultProps) => {
  const [visibleCount, setVisibleCount] = useState(postsPerPage);
  const [selectedCategories, setSelectedCategories] = useState<string[]>([
    categories[0]?.value || "all",
  ]);

  const handleCategoryChange = useCallback((selected: string[]) => {
    setSelectedCategories(selected);
    setVisibleCount(postsPerPage);
  }, [postsPerPage]);

  const handleLoadMore = useCallback(() => {
    setVisibleCount((prev) => prev + postsPerPage);
  }, [postsPerPage]);

  const filteredPosts = useMemo(() => {
    // If "all" is selected, show all posts
    if (selectedCategories.includes("all")) {
      return posts;
    }

    // Otherwise filter by selected categories
    return posts.filter((post) =>
      selectedCategories.includes(post.category.toLowerCase())
    );
  }, [posts, selectedCategories]);

  const postsToDisplay = filteredPosts;
  const hasMore = visibleCount < postsToDisplay.length;

  return (
    <div>
      <FilterForm
        categories={categories}
        onCategoryChange={handleCategoryChange}
      />
      <div className="flex w-full flex-col gap-4 py-8 lg:gap-8">
        {postsToDisplay.length === 0 ? (
          <div className="flex min-h-[300px] items-center justify-center rounded-lg border border-dashed">
            <div className="text-center space-y-4 p-8">
              <p className="text-muted-foreground text-lg font-medium">
                No posts found in the selected categories.
              </p>
              <p className="text-muted-foreground text-sm">
                Try selecting different categories or view all posts.
              </p>
              <Button
                variant="outline"
                className="mt-2"
                onClick={() => handleCategoryChange(["all"])}
              >
                Show All Posts
              </Button>
            </div>
          </div>
        ) : (
          <>
            <div className="grid gap-10 md:grid-cols-2 lg:grid-cols-3">
              {postsToDisplay.slice(0, visibleCount).map((post) => (
                <BlogCard key={post.title} {...post} />
              ))}
            </div>
            <div className="flex justify-center">
              {hasMore && (
                <Button variant="secondary" onClick={handleLoadMore}>
                  Load More
                </Button>
              )}
            </div>
          </>
        )}
      </div>
    </div>
  );
};
