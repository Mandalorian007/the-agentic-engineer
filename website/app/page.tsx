import type { Metadata } from "next";
import Link from "next/link";
import Image from "next/image";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { AspectRatio } from "@/components/ui/aspect-ratio";
import { Badge } from "@/components/ui/badge";
import { ArrowRight } from "lucide-react";
import { NewsletterForm } from "@/components/newsletter-form";
import { NEWSLETTER_NAME, SITE_NAME, SITE_DESCRIPTION } from "@/lib/site";
import { getPostBySlug } from "@/lib/posts";
import { formatReadingTime } from "@/lib/reading-time";

// Revalidate every hour to show new posts as they're published
export const revalidate = 3600;

export const metadata: Metadata = {
  // The layout's title template would render "The Agentic Engineer | The
  // Agentic Engineer" here, so the homepage states its title absolutely.
  title: { absolute: SITE_NAME },
  description: SITE_DESCRIPTION,
  alternates: { canonical: "/" },
  openGraph: { title: SITE_NAME, description: SITE_DESCRIPTION, url: "/" },
};

// Curated rather than chronological: these are the three posts search traffic
// actually lands on, and each one maps to a piece of the thesis.
const START_HERE = [
  {
    slug: "2025-10-13-taming-claude-yolo-mode",
    blurb: "Encode the safety checks you already run without thinking.",
  },
  {
    slug: "2025-11-10-spec-driven-development-planning-templates",
    blurb: "Encode how you plan work before any code gets written.",
  },
  {
    slug: "2025-12-01-claude-code-primitives-guide",
    blurb: "The pieces you encode into, and what each one is good for.",
  },
];

const ONBOARDING_ROWS = [
  {
    junior: "“Run the tests before you push”",
    encoded: "a hook that blocks the commit",
  },
  {
    junior: "“Read the spec before you write code”",
    encoded: "a planning template",
  },
  {
    junior: "“Never touch prod config”",
    encoded: "a permission rule",
  },
  {
    junior: "“We name things like this”",
    encoded: "context checked into the repo",
  },
  {
    junior: "“I'll review your first few PRs closely”",
    encoded: "evals that gate the merge",
  },
];

// TODO: repoint at the manifesto post once it ships.
const METHOD_URL = "/blog/2025-10-20-agentic-engineering-guide";

export default function Home() {
  const startHere = START_HERE.map((entry) => ({
    ...entry,
    post: getPostBySlug(entry.slug),
  })).filter((entry) => entry.post !== null);

  return (
    <div className="container py-12 md:py-20">
      {/* Hero */}
      <section className="mx-auto flex max-w-3xl flex-col items-center space-y-6 text-center">
        <Badge variant="outline">By a builder, for builders</Badge>
        <h1 className="text-4xl font-bold tracking-tight md:text-6xl">
          Encode what you&rsquo;re great at. Hand it to agents one step at a time.
        </h1>
        <p className="max-w-2xl text-xl text-muted-foreground">
          Getting good results out of an agent is like teaching a new junior on
          the team. You already know how to do that. The work is writing it down.
        </p>
        <div className="w-full max-w-xl pt-2">
          <NewsletterForm source="home-hero" />
          <p className="mt-2 text-sm text-muted-foreground">
            The <span className="font-medium text-foreground">{NEWSLETTER_NAME}</span>.
            What I changed, what broke, and one thing you can paste into your own
            repo. Every other Monday. Unsubscribe whenever. Your address goes
            to Buttondown and nowhere else, as described in the{" "}
            <Link href="/privacy" className="underline underline-offset-4">
              privacy policy
            </Link>
            .
          </p>
        </div>
      </section>

      {/* Start here */}
      <section className="mt-24">
        <div className="mb-8 flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <h2 className="text-3xl font-bold">Start here</h2>
            <p className="mt-2 text-muted-foreground">
              The three posts most people arrive for, and what each one encodes.
            </p>
          </div>
          <Button variant="ghost" asChild>
            <Link href="/blog">
              All posts
              <ArrowRight className="ml-2 h-4 w-4" />
            </Link>
          </Button>
        </div>
        <div className="grid grid-cols-1 gap-6 md:grid-cols-3">
          {startHere.map(({ slug, blurb, post }, index) => (
            <Link key={slug} href={`/blog/${slug}`} className="block h-full w-full">
              <Card className="size-full rounded-lg border py-0 transition-colors hover:border-foreground/50">
                <CardContent className="p-0">
                  <AspectRatio ratio={1.520833333} className="overflow-hidden bg-muted">
                    {post!.heroImage ? (
                      <Image
                        src={post!.heroImage}
                        alt={post!.title}
                        fill
                        className="object-cover object-center"
                        priority={index === 0}
                        sizes="(max-width: 768px) 100vw, 33vw"
                      />
                    ) : (
                      <div className="flex size-full items-center justify-center bg-gradient-to-br from-blue-100 to-purple-100 dark:from-blue-950 dark:to-purple-950">
                        <span className="text-muted-foreground">Coming Soon</span>
                      </div>
                    )}
                  </AspectRatio>
                  <div className="flex w-full flex-col gap-4 p-5">
                    <h3 className="text-lg font-medium leading-tight md:text-xl">
                      {post!.title}
                    </h3>
                    <p className="text-sm font-medium leading-[1.4] text-muted-foreground">
                      {blurb}
                    </p>
                    <div className="flex items-center justify-between">
                      <Button size="sm" variant="outline">
                        Read More
                        <ArrowRight className="ml-2 h-4 w-4" />
                      </Button>
                      <span className="text-xs text-muted-foreground">
                        {formatReadingTime(post!.readingTime)}
                      </span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>
      </section>

      {/* It's onboarding, not prompting */}
      <section className="mt-24">
        <div className="mx-auto max-w-3xl">
          <h2 className="text-3xl font-bold">It&rsquo;s onboarding, not prompting</h2>
          <p className="mt-3 text-lg text-muted-foreground">
            You wouldn&rsquo;t hand a new hire a ticket and walk away. You&rsquo;d
            tell them the things you stopped noticing you know.
          </p>

          <div className="mt-10 border-t">
            <div className="hidden grid-cols-2 gap-8 border-b py-3 text-sm font-medium text-muted-foreground sm:grid">
              <span>What you&rsquo;d tell a junior</span>
              <span>What you encode</span>
            </div>
            {ONBOARDING_ROWS.map((row) => (
              <div
                key={row.junior}
                className="grid grid-cols-1 gap-1 border-b py-4 sm:grid-cols-2 sm:gap-8"
              >
                <p className="font-medium">{row.junior}</p>
                <p className="text-muted-foreground">{row.encoded}</p>
              </div>
            ))}
          </div>

          <p className="mt-8 text-lg">
            None of this is new to you. You&rsquo;ve just never written it down.
          </p>

          <div className="mt-8">
            <Button size="lg" asChild>
              <Link href={METHOD_URL}>
                Read the method
                <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
            </Button>
          </div>
        </div>
      </section>

      {/* Consulting, demoted */}
      <section className="mt-24 border-t pt-8">
        <div className="flex flex-col items-start justify-between gap-3 text-sm text-muted-foreground sm:flex-row sm:items-center">
          <p>Running this inside a large engineering org? I do that too.</p>
          <Link
            href="/services"
            className="font-medium text-foreground underline underline-offset-4"
          >
            Hire me
          </Link>
        </div>
      </section>
    </div>
  );
}
