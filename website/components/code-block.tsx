"use client";

import { useTheme } from "next-themes";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { oneDark, oneLight } from "react-syntax-highlighter/dist/esm/styles/prism";
import { useEffect, useState } from "react";

interface CodeBlockProps {
  language: string;
  children: string;
}

/**
 * Theme-aware code block component
 * Uses oneDark for dark mode, oneLight for light mode
 */
export function CodeBlock({ language, children }: CodeBlockProps) {
  const { resolvedTheme } = useTheme();
  const [mounted, setMounted] = useState(false);

  // Avoid hydration mismatch by waiting for client mount
  useEffect(() => {
    setMounted(true);
  }, []);

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
    <SyntaxHighlighter
      style={style as { [key: string]: React.CSSProperties }}
      language={language}
      PreTag="div"
    >
      {children}
    </SyntaxHighlighter>
  );
}
