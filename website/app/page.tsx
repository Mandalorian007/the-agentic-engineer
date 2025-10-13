import Link from "next/link";
import Image from "next/image";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { AspectRatio } from "@/components/ui/aspect-ratio";
import { ArrowRight } from "lucide-react";
import { getRecentPosts } from "@/lib/posts";
import { CATEGORY_LABELS } from "@/lib/categories";
import { formatReadingTime } from "@/lib/reading-time";

export default function Home() {
  const recentPosts = getRecentPosts(3);

  return (
    <div className="container py-12 md:py-24">
      {/* Hero Section */}
      <section className="flex flex-col items-center text-center space-y-6 max-w-3xl mx-auto">
        <h1 className="text-4xl md:text-6xl font-bold tracking-tight">
          Welcome to The Agentic Engineer
        </h1>
        <p className="text-xl text-muted-foreground max-w-2xl">
          Exploring AI agents, automation, and engineering with practical
          insights and real-world examples.
        </p>
        <div className="flex gap-4">
          <Button size="lg" asChild>
            <Link href="/blog">Read the Blog</Link>
          </Button>
          <Button size="lg" variant="outline" asChild>
            <Link href="/blog/category/tutorials">View Tutorials</Link>
          </Button>
        </div>
      </section>

      {/* Recent Posts Section */}
      <section className="mt-24">
        <h2 className="text-3xl font-bold mb-8">Recent Posts</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {recentPosts.map((post) => (
            <Link key={post.slug} href={`/blog/${post.slug}`} className="block h-full w-full">
              <Card className="size-full rounded-lg border py-0 hover:border-foreground/50 transition-colors">
                <CardContent className="p-0">
                  <div className="text-muted-foreground border-b p-2.5 text-sm font-medium leading-[1.2]">
                    {CATEGORY_LABELS[post.category as keyof typeof CATEGORY_LABELS] || post.category}
                  </div>
                  <AspectRatio ratio={1.520833333} className="overflow-hidden bg-muted">
                    {post.heroImage ? (
                      <Image
                        src={post.heroImage}
                        alt={post.title}
                        fill
                        className="object-cover object-center"
                      />
                    ) : (
                      <div className="flex items-center justify-center size-full bg-gradient-to-br from-blue-100 to-purple-100 dark:from-blue-950 dark:to-purple-950">
                        <span className="text-muted-foreground">Coming Soon</span>
                      </div>
                    )}
                  </AspectRatio>
                  <div className="flex w-full flex-col gap-5 p-5">
                    <h2 className="text-lg font-medium leading-tight md:text-xl">
                      {post.title}
                    </h2>
                    <div className="w-full max-w-[20rem]">
                      <p className="text-muted-foreground text-sm font-medium leading-[1.4] line-clamp-3">
                        {post.description}
                      </p>
                    </div>
                    <div className="flex items-center justify-between">
                      <Button size="sm" variant="outline">
                        Read More
                        <ArrowRight className="w-4 h-4 ml-2" />
                      </Button>
                      <span className="text-xs text-muted-foreground">
                        {formatReadingTime(post.readingTime)}
                      </span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>
      </section>
    </div>
  );
}
