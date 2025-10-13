/**
 * Calculate estimated reading time for markdown content
 */
export function calculateReadingTime(content: string): number {
  // Strip markdown syntax (headings, links, images, code blocks)
  const plainText = content
    .replace(/```[\s\S]*?```/g, '') // Remove code blocks
    .replace(/`[^`]*`/g, '') // Remove inline code
    .replace(/!\[.*?\]\(.*?\)/g, '') // Remove images
    .replace(/\[([^\]]+)\]\([^\)]+\)/g, '$1') // Remove links, keep text
    .replace(/#{1,6}\s/g, '') // Remove heading markers
    .replace(/[*_~]/g, ''); // Remove emphasis markers

  // Count words (split on whitespace, filter empty)
  const words = plainText.trim().split(/\s+/).filter(w => w.length > 0).length;

  // Average reading speed: 200 words/minute
  // Round up to nearest minute (always show at least 1 min)
  return Math.max(1, Math.ceil(words / 200));
}

/**
 * Format reading time for display
 */
export function formatReadingTime(minutes: number): string {
  return `${minutes} min read`;
}
