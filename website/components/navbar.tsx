/**
 * Navbar Component
 * Inspired by shadcnblocks navbar8 design
 * Features: Logo, navigation links, auth buttons (placeholder for future Clerk integration)
 */

import Link from "next/link";
import { Button } from "@/components/ui/button";

export function Navbar() {
  return (
    <header className="sticky top-0 z-50 w-full border-b border-border/40 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-16 items-center justify-between">
        {/* Logo */}
        <Link href="/" className="flex items-center space-x-2">
          <span className="text-xl font-bold">The Agentic Engineer</span>
        </Link>

        {/* Navigation Links */}
        <nav className="hidden md:flex items-center space-x-6 text-sm font-medium">
          <Link
            href="/"
            className="transition-colors hover:text-foreground/80 text-foreground/60"
          >
            Home
          </Link>
          <Link
            href="/blog"
            className="transition-colors hover:text-foreground/80 text-foreground/60"
          >
            Blog
          </Link>
        </nav>

        {/* Auth Buttons - Placeholder for future Clerk integration */}
        <div className="flex items-center space-x-4">
          {/* TODO: Replace with Clerk components when auth is implemented
              <SignedOut>
                <SignInButton />
                <SignUpButton />
              </SignedOut>
              <SignedIn>
                <UserButton />
              </SignedIn>
          */}
          <Button variant="ghost" size="sm" asChild>
            <Link href="/auth/signin">Log in</Link>
          </Button>
          <Button size="sm" asChild>
            <Link href="/auth/signup">Sign up</Link>
          </Button>
        </div>
      </div>
    </header>
  );
}
