import Link from "next/link";
import { Button } from "@/components/ui/button";

export default function Home() {
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

      {/* Featured Section - Placeholder */}
      <section className="mt-24">
        <h2 className="text-3xl font-bold mb-8">Featured Posts</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Placeholder cards */}
          {[1, 2, 3].map((i) => (
            <div
              key={i}
              className="border rounded-lg p-6 hover:border-foreground/50 transition-colors"
            >
              <h3 className="font-semibold text-xl mb-2">
                Featured Post {i}
              </h3>
              <p className="text-muted-foreground mb-4">
                This is a placeholder for a featured blog post. Content will be
                loaded dynamically in the next phase.
              </p>
              <Link
                href="/blog"
                className="text-sm font-medium hover:underline"
              >
                Read more →
              </Link>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
