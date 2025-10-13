"use client";

import { useEffect, useState } from "react";

/**
 * Reading progress bar component
 * Shows a horizontal bar at the top of the page that fills as the user scrolls
 * Uses shadcn/ui theme colors (primary for the bar, muted for background)
 */
export function ReadingProgress() {
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    const updateProgress = () => {
      // Calculate scroll progress as a percentage
      const scrollHeight = document.documentElement.scrollHeight - window.innerHeight;
      const scrolled = window.scrollY;
      const progressPercent = scrollHeight > 0 ? (scrolled / scrollHeight) * 100 : 0;
      setProgress(Math.min(progressPercent, 100));
    };

    // Update on scroll
    window.addEventListener("scroll", updateProgress, { passive: true });

    // Update on mount in case page loads scrolled
    updateProgress();

    return () => window.removeEventListener("scroll", updateProgress);
  }, []);

  return (
    <div className="fixed top-0 left-0 right-0 z-50 h-1 bg-muted/30">
      <div
        className="h-full bg-primary transition-all duration-150 ease-out"
        style={{ width: `${progress}%` }}
        role="progressbar"
        aria-valuenow={Math.round(progress)}
        aria-valuemin={0}
        aria-valuemax={100}
        aria-label="Reading progress"
      />
    </div>
  );
}
