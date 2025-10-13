/**
 * Footer Component
 * Inspired by shadcnblocks footer16 design
 * Features: Logo, navigation links, social icons, copyright
 */

import Link from "next/link";
import { Separator } from "@/components/ui/separator";

export function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="w-full border-t bg-background">
      <div className="container py-12">
        <div className="grid grid-cols-1 gap-8 md:grid-cols-4">
          {/* Logo & Description */}
          <div className="md:col-span-2">
            <Link href="/" className="flex items-center space-x-2 mb-4">
              <span className="text-xl font-bold">The Agentic Engineer</span>
            </Link>
            <p className="text-sm text-muted-foreground max-w-xs">
              Exploring AI agents, automation, and engineering with practical
              insights and real-world examples.
            </p>
          </div>

          {/* Navigation Links */}
          <div>
            <h3 className="font-semibold mb-4">Navigation</h3>
            <ul className="space-y-2 text-sm text-muted-foreground">
              <li>
                <Link
                  href="/"
                  className="hover:text-foreground transition-colors"
                >
                  Home
                </Link>
              </li>
              <li>
                <Link
                  href="/blog"
                  className="hover:text-foreground transition-colors"
                >
                  Blog
                </Link>
              </li>
            </ul>
          </div>

          {/* Categories (placeholder for future) */}
          <div>
            <h3 className="font-semibold mb-4">Categories</h3>
            <ul className="space-y-2 text-sm text-muted-foreground">
              <li>
                <Link
                  href="/blog/category/tutorials"
                  className="hover:text-foreground transition-colors"
                >
                  Tutorials
                </Link>
              </li>
              <li>
                <Link
                  href="/blog/category/case-studies"
                  className="hover:text-foreground transition-colors"
                >
                  Case Studies
                </Link>
              </li>
              <li>
                <Link
                  href="/blog/category/guides"
                  className="hover:text-foreground transition-colors"
                >
                  Guides
                </Link>
              </li>
            </ul>
          </div>
        </div>

        <Separator className="my-8" />

        {/* Copyright */}
        <div className="flex flex-col items-center justify-between gap-4 md:flex-row">
          <p className="text-sm text-muted-foreground">
            © {currentYear} The Agentic Engineer. All rights reserved.
          </p>
          {/* Placeholder for social links */}
          <div className="flex items-center space-x-4">
            <span className="text-sm text-muted-foreground">
              {/* TODO: Add social icons when needed */}
            </span>
          </div>
        </div>
      </div>
    </footer>
  );
}
