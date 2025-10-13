"use client";

import { useTheme } from "next-themes";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { oneDark, oneLight } from "react-syntax-highlighter/dist/esm/styles/prism";
import { useEffect, useState } from "react";
import { Check, Copy } from "lucide-react";
import { Button } from "@/components/ui/button";

interface CodeBlockProps {
  language: string;
  children: string;
}

/**
 * Theme-aware code block component with copy-to-clipboard functionality
 * Uses oneDark for dark mode, oneLight for light mode
 */
export function CodeBlock({ language, children }: CodeBlockProps) {
  const { resolvedTheme } = useTheme();
  const [mounted, setMounted] = useState(false);
  const [copied, setCopied] = useState(false);

  // Avoid hydration mismatch by waiting for client mount
  useEffect(() => {
    setMounted(true);
  }, []);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(children);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000); // Reset after 2 seconds
    } catch (err) {
      console.error("Failed to copy code:", err);
    }
  };

  if (!mounted) {
    // Return a placeholder during SSR to avoid hydration mismatch
    return (
      <pre className="rounded-lg border p-4 overflow-x-auto bg-muted">
        <code className="font-mono text-sm">{children}</code>
      </pre>
    );
  }

  const style = resolvedTheme === "dark" ? oneDark : oneLight;

  return (
    <div className="relative group">
      <Button
        onClick={handleCopy}
        variant="ghost"
        size="icon"
        className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity z-10 h-8 w-8"
        aria-label={copied ? "Code copied!" : "Copy code to clipboard"}
      >
        {copied ? (
          <Check className="h-4 w-4 text-green-500" />
        ) : (
          <Copy className="h-4 w-4" />
        )}
      </Button>
      <SyntaxHighlighter
        style={style as { [key: string]: React.CSSProperties }}
        language={language}
        PreTag="div"
      >
        {children}
      </SyntaxHighlighter>
    </div>
  );
}
