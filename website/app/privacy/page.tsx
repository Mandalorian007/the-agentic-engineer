/**
 * Privacy Policy Page
 * Displays the privacy policy from markdown with styling
 */

import Link from "next/link";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { getPrivacyPolicy } from "@/lib/legal";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Privacy Policy | The Agentic Engineer",
  description: "Privacy policy for The Agentic Engineer blog. Learn how we collect, use, and protect your information.",
};

export default function PrivacyPage() {
  const doc = getPrivacyPolicy();

  return (
    <div className="container py-12">
      {/* Breadcrumb */}
      <nav className="mb-8 text-sm text-muted-foreground">
        <Link href="/" className="hover:text-foreground">
          Home
        </Link>
        {" / "}
        <span className="text-foreground">Privacy Policy</span>
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
              href="/terms"
              className="text-muted-foreground hover:text-foreground"
            >
              Terms of Service →
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
