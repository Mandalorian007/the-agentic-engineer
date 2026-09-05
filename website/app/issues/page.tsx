/**
 * The email archive.
 *
 * Every issue that has been sent and has cleared its archive delay lives here.
 * Subscribers get each one first; this page is where they end up afterwards.
 */

import type { Metadata } from "next";
import Link from "next/link";
import { getAllIssues, getArchivedIssues, isArchived } from "@/lib/issues";
import { NewsletterCta } from "@/components/newsletter-cta";
import { PreviewList } from "@/components/preview-list";
import { previewUnpublished } from "@/lib/preview";
import { formatReadingTime } from "@/lib/reading-time";
import { NEWSLETTER_NAME, SITE_URL } from "@/lib/site";

export const revalidate = 3600;

export const metadata: Metadata = {
  title: "Issues",
  description: `The email archive for ${NEWSLETTER_NAME}. What changed in how I work, what broke, and one thing you can paste into your own repo.`,
  alternates: { canonical: `${SITE_URL}/issues` },
};

export default function IssuesPage() {
  const issues = getArchivedIssues();

  // Written but not yet public: either unsent, or still inside the archive
  // delay. Same treatment as scheduled posts, for the same reason.
  const upcoming = previewUnpublished()
    ? getAllIssues()
        .filter((issue) => !isArchived(issue))
        .map((issue) => ({
          slug: issue.slug,
          title: issue.title,
          href: `/issues/${issue.slug}`,
          date: issue.archiveDate,
        }))
    : [];

  return (
    <div className="container py-12 md:py-20">
      <div className="mx-auto max-w-3xl">
        <div className="space-y-3">
          <h1 className="text-4xl font-bold tracking-tight md:text-5xl">
            Issues
          </h1>
          <p className="text-xl text-muted-foreground">
            The email archive for {NEWSLETTER_NAME}. What changed in how I work,
            what broke, and one thing you can paste into your own repo.
          </p>
          <p className="text-muted-foreground">
            Subscribers get each issue a month before it lands here. Everything
            below has already gone out.
          </p>
        </div>

        {issues.length > 0 ? (
          <ul className="mt-12 divide-y border-t">
            {issues.map((issue) => (
              <li key={issue.slug}>
                <Link
                  href={`/issues/${issue.slug}`}
                  className="group flex flex-col gap-1 py-6 transition-colors"
                >
                  <div className="flex items-center gap-3 text-sm text-muted-foreground">
                    <time dateTime={issue.date}>
                      {new Date(issue.date).toLocaleDateString("en-US", {
                        year: "numeric",
                        month: "long",
                        day: "numeric",
                      })}
                    </time>
                    <span>•</span>
                    <span>{formatReadingTime(issue.readingTime)}</span>
                  </div>
                  <h2 className="text-xl font-semibold group-hover:underline">
                    {issue.title}
                  </h2>
                  <p className="text-muted-foreground">{issue.description}</p>
                </Link>
              </li>
            ))}
          </ul>
        ) : (
          <p className="mt-12 rounded-lg border bg-muted/40 p-6 text-muted-foreground">
            The archive is empty for now. Issues appear here a month after they
            go out, so subscribing is the only way to read the early ones. In
            the meantime the <Link href="/blog" className="underline underline-offset-4">blog</Link> is where the long-form work lives.
          </p>
        )}

        {upcoming.length > 0 && (
          <PreviewList
            heading="Not yet archived"
            emptyLabel="Visible because preview mode is on. Dates shown are when each issue reaches the archive."
            items={upcoming}
          />
        )}

        <div className="mt-16">
          <NewsletterCta
            source="issues-index"
            body="Every other Monday, before it reaches this page."
          />
        </div>
      </div>
    </div>
  );
}
