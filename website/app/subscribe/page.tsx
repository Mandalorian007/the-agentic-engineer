import type { Metadata } from "next";
import Link from "next/link";
import { NewsletterCta } from "@/components/newsletter-cta";
import { NEWSLETTER_NAME, SITE_URL } from "@/lib/site";

/**
 * A short URL for the places that only take a link: a LinkedIn comment, a
 * bio, the end of a talk. The homepage form does the same job for people who
 * arrive at the front door; this is for people sent here on purpose.
 */

export const metadata: Metadata = {
  title: "Subscribe",
  description: `${NEWSLETTER_NAME}: what I changed in how I work, what broke, and one thing you can paste into your own repo. Every Monday.`,
  alternates: { canonical: `${SITE_URL}/subscribe` },
};

export default function SubscribePage() {
  return (
    <div className="container py-12 md:py-20">
      <div className="mx-auto max-w-3xl space-y-8">
        <div className="space-y-3">
          <h1 className="text-4xl font-bold tracking-tight md:text-5xl">
            {NEWSLETTER_NAME}
          </h1>
          <p className="text-xl text-muted-foreground">
            I run AI strategy and the agentic platform at a healthcare startup,
            and I write down what that actually looks like. One email every
            Monday: what I changed in how I work, what broke, and one thing you
            can paste into your own repo.
          </p>
        </div>
        <NewsletterCta
          source="subscribe-page"
          body="Real hooks, commands, and config. Not diagrams. If nothing broke, I say so rather than invent something."
        />
        <p className="text-sm text-muted-foreground">
          Past issues are public a month after they send, on the{" "}
          <Link href="/issues" className="underline underline-offset-4">
            issues page
          </Link>
          .
        </p>
      </div>
    </div>
  );
}
