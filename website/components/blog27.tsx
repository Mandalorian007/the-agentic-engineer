"use client";
import { zodResolver } from "@hookform/resolvers/zod";
import { ArrowRight, Slash } from "lucide-react";
import { Fragment, useCallback, useMemo, useState } from "react";
import { ControllerRenderProps, useForm } from "react-hook-form";
import { z } from "zod";
import Image from "next/image";

import { AspectRatio } from "@/components/ui/aspect-ratio";
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbSeparator,
} from "@/components/ui/breadcrumb";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Checkbox } from "@/components/ui/checkbox";
import { Form, FormControl, FormField, FormItem } from "@/components/ui/form";
import { Label } from "@/components/ui/label";

interface BreadcrumbItem {
  label: string;
  link: string;
}

interface Post {
  category: string;
  title: string;
  summary: string;
  link: string;
  cta: string;
  thumbnail: string;
  readingTime?: string;
}

interface Category {
  label: string;
  value: string;
}

interface FilterFormProps {
  categories: Array<Category>;
  onCategoryChange: (selectedCategories: string[]) => void;
}

interface BlogsResultProps {
  posts: Array<Post>;
  categories: Array<Category>;
}

interface BreadcrumbBlogProps {
  breadcrumb: Array<BreadcrumbItem>;
}

const POSTS_PER_PAGE = 6;

const BREADCRUMB: Array<BreadcrumbItem> = [
  {
    label: "Home",
    link: "/",
  },
  {
    label: "Blog",
    link: "/blog",
  },
];

// Categories from The Agentic Engineer spec - aligned with /create-post command
const CATEGORIES: Array<Category> = [
  {
    label: "All",
    value: "all",
  },
  {
    label: "Tutorials",
    value: "tutorials",
  },
  {
    label: "Case Studies",
    value: "case-studies",
  },
  {
    label: "Guides",
    value: "guides",
  },
  {
    label: "Lists & Tips",
    value: "lists",
  },
  {
    label: "Comparisons",
    value: "comparisons",
  },
  {
    label: "Problem & Solution",
    value: "problem-solution",
  },
  {
    label: "Opinions",
    value: "opinions",
  },
];

const PRIMARY_POST: Post = {
  category: "Case Studies",
  title: "Voice to Blog Automation with Claude Code",
  summary:
    "How I built a fully automated blog publishing pipeline using Claude Code, Python, and AI agents—from voice input to published content.",
  link: "/blog/2025-10-12-voice-to-blog-automation",
  cta: "Read Case Study",
  thumbnail: "https://deifkwefumgah.cloudfront.net/shadcnblocks/block/placeholder-1.svg",
};

const POSTS: Array<Post> = [
  {
    category: "Tutorials",
    title: "Getting Started with AI Agents",
    summary:
      "Learn the fundamentals of building AI agents from scratch with practical examples and real-world use cases.",
    link: "#",
    cta: "Start Learning",
    thumbnail: "https://deifkwefumgah.cloudfront.net/shadcnblocks/block/placeholder-2.svg",
  },
  {
    category: "Productivity",
    title: "Time Management for Developers: What Really Works",
    summary:
      "Learn proven strategies to avoid burnout and stay on top of your tasks without stress.",
    link: "#",
    cta: "Manage Your Time",
    thumbnail: "https://deifkwefumgah.cloudfront.net/shadcnblocks/block/placeholder-3.svg",
  },
  {
    category: "Productivity",
    title: "Automate Your Workflow with Task Runners",
    summary:
      "Use tools like Gulp, npm scripts, and GitHub Actions to automate repetitive development tasks.",
    link: "#",
    cta: "Automate Now",
    thumbnail: "https://deifkwefumgah.cloudfront.net/shadcnblocks/block/placeholder-4.svg",
  },
  {
    category: "Productivity",
    title: "Effective Daily Routines for Developers",
    summary:
      "Discover routines that top developers follow to stay productive, creative, and focused.",
    link: "#",
    cta: "Find Your Flow",
    thumbnail: "https://deifkwefumgah.cloudfront.net/shadcnblocks/block/placeholder-5.svg",
  },
  {
    category: "Productivity",
    title: "Master Git Like a Pro with These Shortcuts",
    summary:
      "Speed up your version control workflow with powerful Git aliases and tips.",
    link: "#",
    cta: "Speed Up Git",
    thumbnail: "https://deifkwefumgah.cloudfront.net/shadcnblocks/block/placeholder-6.svg",
  },
  {
    category: "Productivity",
    title: "Reducing Context Switching as a Developer",
    summary:
      "Minimize distractions and deep-dive into your code with focused work practices.",
    link: "#",
    cta: "Stay Focused",
    thumbnail: "https://deifkwefumgah.cloudfront.net/shadcnblocks/block/placeholder-1.svg",
  },
  {
    category: "Productivity",
    title: "Remote Work Setup: Tools for a Distraction-Free Environment",
    summary:
      "Set up your space and software stack for maximum productivity when working from home.",
    link: "#",
    cta: "Upgrade Your Setup",
    thumbnail: "https://deifkwefumgah.cloudfront.net/shadcnblocks/block/placeholder-2.svg",
  },
  {
    category: "Productivity",
    title: "Pomodoro for Coders: Does It Really Work?",
    summary:
      "A practical review of the Pomodoro technique and its effectiveness for software development.",
    link: "#",
    cta: "Try the Method",
    thumbnail: "https://deifkwefumgah.cloudfront.net/shadcnblocks/block/placeholder-3.svg",
  },
  {
    category: "Accessibility",
    title: "Why Accessibility Should Be Part of Your MVP",
    summary:
      "Making your product inclusive from day one improves usability and reach.",
    link: "#",
    cta: "Learn Why",
    thumbnail: "https://deifkwefumgah.cloudfront.net/shadcnblocks/block/placeholder-4.svg",
  },
  {
    category: "Accessibility",
    title: "Using ARIA Roles Correctly in Your Web App",
    summary:
      "Understand how to enhance screen reader support using ARIA roles and landmarks.",
    link: "#",
    cta: "Improve Semantics",
    thumbnail: "https://deifkwefumgah.cloudfront.net/shadcnblocks/block/placeholder-5.svg",
  },
  {
    category: "Accessibility",
    title: "Color Contrast Tips for Better Readability",
    summary:
      "Learn how to choose accessible color combinations that meet WCAG standards.",
    link: "#",
    cta: "Fix Your Colors",
    thumbnail: "https://deifkwefumgah.cloudfront.net/shadcnblocks/block/placeholder-6.svg",
  },
  {
    category: "Accessibility",
    title: "Keyboard Navigation: The Overlooked User Experience",
    summary:
      "Ensure your website is fully usable with just a keyboard, for accessibility and speed.",
    link: "#",
    cta: "Test Navigation",
    thumbnail: "https://deifkwefumgah.cloudfront.net/shadcnblocks/block/placeholder-1.svg",
  },
  {
    category: "Accessibility",
    title: "Accessible Forms: Labels, Errors & Feedback",
    summary:
      "Improve the usability of your forms by ensuring screen readers and users receive clear instructions.",
    link: "#",
    cta: "Fix Your Forms",
    thumbnail: "https://deifkwefumgah.cloudfront.net/shadcnblocks/block/placeholder-2.svg",
  },
  {
    category: "Accessibility",
    title: "Screen Reader Testing: A Beginner's Guide",
    summary:
      "How to test your site with popular screen readers and what to listen for.",
    link: "#",
    cta: "Start Testing",
    thumbnail: "https://deifkwefumgah.cloudfront.net/shadcnblocks/block/placeholder-3.svg",
  },
  {
    category: "Accessibility",
    title: "Inclusive Design Thinking in UI Development",
    summary:
      "Design interfaces that consider users of all abilities from the start.",
    link: "#",
    cta: "Design for All",
    thumbnail: "https://deifkwefumgah.cloudfront.net/shadcnblocks/block/placeholder-4.svg",
  },
  {
    category: "Accessibility",
    title: "Accessibility Audits: Tools and Checklists",
    summary:
      "Perform thorough accessibility audits with tools like Axe, Lighthouse, and manual checklists.",
    link: "#",
    cta: "Audit Now",
    thumbnail: "https://deifkwefumgah.cloudfront.net/shadcnblocks/block/placeholder-5.svg",
  },
  {
    category: "Performance",
    title: "Lazy Loading Images with Modern HTML",
    summary:
      "Improve load times by using native lazy-loading and fallback strategies for images.",
    link: "#",
    cta: "Optimize Images",
    thumbnail: "https://deifkwefumgah.cloudfront.net/shadcnblocks/block/placeholder-6.svg",
  },
  {
    category: "Performance",
    title: "Minifying JavaScript Without Breaking Your App",
    summary:
      "Best practices for minifying and tree-shaking your JS bundles to boost speed.",
    link: "#",
    cta: "Shrink Your Code",
    thumbnail: "https://deifkwefumgah.cloudfront.net/shadcnblocks/block/placeholder-1.svg",
  },
  {
    category: "Performance",
    title: "Web Vitals Explained: CLS, LCP, FID",
    summary:
      "Learn how to measure and improve Core Web Vitals for a better user experience.",
    link: "#",
    cta: "Improve Vitals",
    thumbnail: "https://deifkwefumgah.cloudfront.net/shadcnblocks/block/placeholder-2.svg",
  },
  {
    category: "Performance",
    title: "Server-Side Rendering vs Client-Side: Which is Faster?",
    summary:
      "Compare SSR and CSR strategies and when to use each for better performance.",
    link: "#",
    cta: "Explore Options",
    thumbnail: "https://deifkwefumgah.cloudfront.net/shadcnblocks/block/placeholder-3.svg",
  },
  {
    category: "Performance",
    title: "Optimizing Fonts for Faster Page Loads",
    summary:
      "Learn techniques for loading fonts without blocking rendering or causing layout shifts.",
    link: "#",
    cta: "Speed Up Fonts",
    thumbnail: "https://deifkwefumgah.cloudfront.net/shadcnblocks/block/placeholder-4.svg",
  },
  {
    category: "Performance",
    title: "Reduce JavaScript Bundle Size with Code Splitting",
    summary:
      "Use dynamic imports and route-based chunking to reduce initial load time.",
    link: "#",
    cta: "Split It Up",
    thumbnail: "https://deifkwefumgah.cloudfront.net/shadcnblocks/block/placeholder-5.svg",
  },
  {
    category: "Performance",
    title: "Caching Strategies for Modern Web Apps",
    summary:
      "Leverage HTTP caching, service workers, and CDNs to improve speed and offline support.",
    link: "#",
    cta: "Cache Smarter",
    thumbnail: "https://deifkwefumgah.cloudfront.net/shadcnblocks/block/placeholder-6.svg",
  },
  {
    category: "Performance",
    title: "Analyzing Performance Bottlenecks with Chrome DevTools",
    summary:
      "Use the Performance tab in DevTools to track down and fix runtime issues in your app.",
    link: "#",
    cta: "Analyze Now",
    thumbnail: "https://deifkwefumgah.cloudfront.net/shadcnblocks/block/placeholder-1.svg",
  },
];

const FilterFormSchema = z.object({
  items: z.array(z.string()).refine((value) => value.length > 0, {
    message: "At least one category should be selected.",
  }),
});

const FilterForm = ({ categories, onCategoryChange }: FilterFormProps) => {
  const form = useForm<z.infer<typeof FilterFormSchema>>({
    resolver: zodResolver(FilterFormSchema),
    defaultValues: {
      items: [CATEGORIES[0].value],
    },
  });

  const handleCheckboxChange = useCallback(
    (
      checked: boolean | string,
      categoryValue: string,
      field: ControllerRenderProps<z.infer<typeof FilterFormSchema>, "items">,
    ) => {
      let updatedValues = checked
        ? [...field.value, categoryValue]
        : field.value.filter((value: string) => value !== categoryValue);

      // If no categories are checked, add "all"
      if (updatedValues.length === 0) {
        form.setValue("items", ["all"]);
        onCategoryChange(["all"]);
        return;
      }

      // Remove "all" if specific category is checked
      if (updatedValues.includes("all")) {
        updatedValues = updatedValues.filter((v: string) => v !== "all");
      }

      // Avoid unnecessary updates
      if (JSON.stringify(field.value) !== JSON.stringify(updatedValues)) {
        form.setValue("items", updatedValues);
        onCategoryChange(updatedValues);
      }
    },
    [form, onCategoryChange],
  );

  return (
    <Form {...form}>
      <form>
        <FormField
          control={form.control}
          name="items"
          render={({ field }) => (
            <FormItem className="flex w-full flex-wrap items-center gap-2.5">
              {categories.map((category) => {
                const isChecked = field.value?.includes(category.value);
                return (
                  <FormItem
                    key={category.value}
                    className="flex flex-row items-start space-x-3 space-y-0"
                  >
                    <FormControl>
                      <Label
                        className={`flex cursor-pointer items-center gap-2.5 rounded-full px-4 py-2 transition-all ${
                          isChecked
                            ? 'bg-primary text-primary-foreground shadow-sm'
                            : 'bg-muted hover:bg-muted/70'
                        }`}
                      >
                        <span className="text-sm font-medium">{category.label}</span>
                        <Checkbox
                          checked={isChecked}
                          onCheckedChange={(checked) =>
                            handleCheckboxChange(checked, category.value, field)
                          }
                          className="sr-only"
                        />
                      </Label>
                    </FormControl>
                  </FormItem>
                );
              })}
            </FormItem>
          )}
        />
      </form>
    </Form>
  );
};

const BlogsResult = ({ posts, categories }: BlogsResultProps) => {
  const [visibleCount, setVisibleCount] = useState(POSTS_PER_PAGE);
  const [selectedCategories, setSelectedCategories] = useState<string[]>([
    CATEGORIES[0].value,
  ]);
  const handleCategoryChange = useCallback((selected: string[]) => {
    setSelectedCategories(selected);
    setVisibleCount(POSTS_PER_PAGE);
  }, []);

  const handleLoadMore = useCallback(() => {
    setVisibleCount((prev) => prev + POSTS_PER_PAGE);
  }, []);
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

const BreadcrumbBlog = ({ breadcrumb }: BreadcrumbBlogProps) => {
  return (
    <Breadcrumb>
      <BreadcrumbList>
        {breadcrumb.map((item, i) => {
          return (
            <Fragment key={`${item.label}`}>
              <BreadcrumbItem>
                <BreadcrumbLink href={item.link}>{item.label}</BreadcrumbLink>
              </BreadcrumbItem>
              {i < breadcrumb.length - 1 ? (
                <BreadcrumbSeparator>
                  <Slash />
                </BreadcrumbSeparator>
              ) : null}
            </Fragment>
          );
        })}
      </BreadcrumbList>
    </Breadcrumb>
  );
};

const BlogCard = ({ category, title, thumbnail, summary, link, cta, readingTime }: Post) => {
  /**
   * Format category ID to display name
   * Examples:
   *   "case-studies" -> "Case Studies"
   *   "tutorials" -> "Tutorials"
   *   "problem-solution" -> "Problem Solution"
   */
  const formatCategory = (cat: string): string => {
    return cat
      .split('-')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

  return (
    <a href={link} className="block h-full w-full">
      <Card className="size-full rounded-lg border py-0">
        <CardContent className="p-0">
          <div className="text-muted-foreground border-b p-2.5 text-sm font-medium leading-[1.2]">
            {formatCategory(category)}
          </div>
          <AspectRatio ratio={1.520833333} className="overflow-hidden">
            <Image
              src={thumbnail}
              alt={title}
              fill
              className="object-cover object-center"
            />
          </AspectRatio>
          <div className="flex w-full flex-col gap-5 p-5">
            <h2 className="text-lg font-medium leading-tight md:text-xl">
              {title}
            </h2>
            <div className="w-full max-w-[20rem]">
              <p className="text-muted-foreground text-sm font-medium leading-[1.4]">
                {summary}
              </p>
            </div>
            <div className="flex items-center justify-between">
              <Button size="sm" variant="outline">
                {cta}
                <ArrowRight />
              </Button>
              {readingTime && (
                <span className="text-xs text-muted-foreground">
                  {readingTime}
                </span>
              )}
            </div>
          </div>
        </CardContent>
      </Card>
    </a>
  );
};

interface Blog27Props {
  primaryPost?: Post | null;
  posts?: Array<Post>;
}

const Blog27 = ({ primaryPost = PRIMARY_POST, posts = POSTS }: Blog27Props) => {
  return (
    <section className="pb-32">
      <div className="bg-muted bg-[url('https://deifkwefumgah.cloudfront.net/shadcnblocks/block/patterns/dot-pattern-2.svg')] bg-[length:3.125rem_3.125rem] bg-repeat">
        <div className="container flex flex-col items-start justify-start gap-16 py-20 lg:flex-row lg:items-center lg:justify-between">
          <div className="flex w-full flex-col justify-between gap-12">
            <div className="flex w-full max-w-[36rem] flex-col gap-8">
              <BreadcrumbBlog breadcrumb={BREADCRUMB} />
              <div className="flex w-full flex-col gap-5">
                <h1 className="text-[2.5rem] font-semibold leading-[1.2] md:text-5xl lg:text-6xl">
                  The Agentic Engineer Blog
                </h1>
                <p className="text-muted-foreground text-xl leading-[1.4]">
                  Exploring AI agents, automation, and engineering with practical insights and real-world examples.
                </p>
              </div>
            </div>
          </div>

          {primaryPost && (
            <div className="w-full max-w-[27.5rem]">
              <BlogCard {...primaryPost} />
            </div>
          )}
        </div>
      </div>
      <div className="py-20">
        <div className="container flex flex-col gap-8">
          <h2 className="text-[1.75rem] font-medium leading-none md:text-[2.25rem] lg:text-[2rem]">
            All Blogs
          </h2>
          <div>
            <BlogsResult posts={posts} categories={CATEGORIES} />
          </div>
        </div>
      </div>
    </section>
  );
};

export { Blog27 };
