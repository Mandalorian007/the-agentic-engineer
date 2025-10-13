/**
 * Terms of Service Page
 * Displays the terms of service from markdown with styling
 */

import Link from "next/link";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { getTermsOfService } from "@/lib/legal";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Terms of Service | The Agentic Engineer",
  description: "Terms of service for The Agentic Engineer blog. Review the terms and conditions for using our website.",
};

export default function TermsPage() {
  const doc = getTermsOfService();

  return (
    <div className="container py-12">
      {/* Breadcrumb */}
      <nav className="mb-8 text-sm text-muted-foreground">
        <Link href="/" className="hover:text-foreground">
          Home
        </Link>
        {" / "}
        <span className="text-foreground">Terms of Service</span>
      </nav>

      {/* Content */}
      <article className="mx-auto max-w-4xl">
        <div className="prose prose-neutral dark:prose-invert max-w-none">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>
            {doc.content}
          </ReactMarkdown>
        </div>

        {/* Footer Navigation */}
        <div className="mt-12 pt-8 border-t">
          <div className="flex flex-col sm:flex-row gap-4 justify-between text-sm">
            <Link
              href="/privacy"
              className="text-muted-foreground hover:text-foreground"
            >
              Privacy Policy →
            </Link>
            <Link
              href="/"
              className="text-muted-foreground hover:text-foreground"
            >
              ← Back to Home
            </Link>
          </div>
        </div>
      </article>
    </div>
  );
}
