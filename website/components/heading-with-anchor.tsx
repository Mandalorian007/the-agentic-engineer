"use client";

import { useState } from "react";
import { Link as LinkIcon, Check } from "lucide-react";
import { Button } from "@/components/ui/button";

interface HeadingWithAnchorProps {
  id: string;
  level: "h2" | "h3" | "h4";
  children: React.ReactNode;
}

/**
 * Heading component with hover-to-reveal anchor link
 * Copies direct link to section when clicked
 */
export function HeadingWithAnchor({ id, level, children }: HeadingWithAnchorProps) {
  const [copied, setCopied] = useState(false);

  const handleCopyLink = async () => {
    try {
      const url = `${window.location.origin}${window.location.pathname}#${id}`;
      await navigator.clipboard.writeText(url);
      setCopied(true);

      // Also update URL without scrolling
      window.history.pushState(null, "", `#${id}`);

      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error("Failed to copy link:", err);
    }
  };

  const Tag = level;

  return (
    <Tag id={id} className="group relative scroll-mt-24">
      <span className="flex items-center gap-2">
        {children}
        <Button
          variant="ghost"
          size="icon"
          onClick={handleCopyLink}
          className="opacity-0 group-hover:opacity-100 transition-opacity h-6 w-6 -ml-1"
          aria-label={copied ? "Link copied!" : "Copy link to section"}
        >
          {copied ? (
            <Check className="h-4 w-4 text-green-500" />
          ) : (
            <LinkIcon className="h-4 w-4 text-muted-foreground" />
          )}
        </Button>
      </span>
    </Tag>
  );
}
