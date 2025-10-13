"use client";

import { useEffect, useState } from "react";
import { cn } from "@/lib/utils";
import type { Heading } from "@/lib/toc";

interface TableOfContentsProps {
  headings: Heading[];
}

export function TableOfContents({ headings }: TableOfContentsProps) {
  const [activeId, setActiveId] = useState<string>("");

  useEffect(() => {
    // Set up IntersectionObserver for active section highlighting
    if (headings.length > 0) {
      const observer = new IntersectionObserver(
        (entries) => {
          entries.forEach((entry) => {
            if (entry.isIntersecting) {
              setActiveId(entry.target.id);
            }
          });
        },
        {
          rootMargin: '-80px 0px -66%', // Account for navbar height
          threshold: 0,
        }
      );

      // Observe all heading elements
      headings.forEach((heading) => {
        const element = document.getElementById(heading.id);
        if (element) {
          observer.observe(element);
        }
      });

      return () => observer.disconnect();
    }
  }, [headings]);

  // Don't show TOC if there are fewer than 3 headings
  if (headings.length < 3) {
    return null;
  }

  return (
    <div className="border rounded-lg p-6">
      <h3 className="font-semibold mb-4">On This Page</h3>
      <nav>
        <ul className="space-y-2">
          {headings.map((heading) => (
            <li key={heading.id}>
              <a
                href={`#${heading.id}`}
                className={cn(
                  "block py-1 text-sm transition-colors duration-200",
                  activeId === heading.id
                    ? "text-primary font-medium"
                    : "text-muted-foreground hover:text-foreground"
                )}
                onClick={(e) => {
                  e.preventDefault();
                  const element = document.getElementById(heading.id);
                  if (element) {
                    const navbarHeight = 80; // Account for navbar + padding
                    const elementPosition = element.getBoundingClientRect().top;
                    const offsetPosition = elementPosition + window.scrollY - navbarHeight;

                    window.scrollTo({
                      top: offsetPosition,
                      behavior: 'smooth',
                    });
                  }
                }}
              >
                {heading.text}
              </a>
            </li>
          ))}
        </ul>
      </nav>
    </div>
  );
}
