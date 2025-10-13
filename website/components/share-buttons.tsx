"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { FaFacebookF, FaLinkedinIn, FaXTwitter } from "react-icons/fa6";
import { Link as LinkIcon, Check } from "lucide-react";

interface ShareButtonsProps {
  url: string;
  title: string;
}

export function ShareButtons({ url, title }: ShareButtonsProps) {
  const [copied, setCopied] = useState(false);

  const handleCopyLink = async () => {
    try {
      await navigator.clipboard.writeText(url);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error("Failed to copy:", err);
    }
  };

  return (
    <div className="border rounded-lg p-6">
      <h3 className="font-semibold mb-4">Share this article</h3>
      <div className="flex gap-2 flex-wrap">
        <Button
          variant="secondary"
          size="icon"
          className="group rounded-full"
          onClick={handleCopyLink}
          aria-label={copied ? "Link copied!" : "Copy link"}
        >
          {copied ? (
            <Check className="text-primary h-4 w-4" />
          ) : (
            <LinkIcon className="text-muted-foreground group-hover:text-primary h-4 w-4 transition-colors" />
          )}
        </Button>
        <Button
          variant="secondary"
          size="icon"
          className="group rounded-full"
          asChild
        >
          <a
            href={`https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(url)}`}
            target="_blank"
            rel="noopener noreferrer"
            aria-label="Share on Facebook"
          >
            <FaFacebookF className="text-muted-foreground group-hover:text-primary h-4 w-4 transition-colors" />
          </a>
        </Button>
        <Button
          variant="secondary"
          size="icon"
          className="group rounded-full"
          asChild
        >
          <a
            href={`https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(url)}`}
            target="_blank"
            rel="noopener noreferrer"
            aria-label="Share on LinkedIn"
          >
            <FaLinkedinIn className="text-muted-foreground group-hover:text-primary h-4 w-4 transition-colors" />
          </a>
        </Button>
        <Button
          variant="secondary"
          size="icon"
          className="group rounded-full"
          asChild
        >
          <a
            href={`https://twitter.com/intent/tweet?url=${encodeURIComponent(url)}&text=${encodeURIComponent(title)}`}
            target="_blank"
            rel="noopener noreferrer"
            aria-label="Share on Twitter"
          >
            <FaXTwitter className="text-muted-foreground group-hover:text-primary h-4 w-4 transition-colors" />
          </a>
        </Button>
      </div>
    </div>
  );
}
