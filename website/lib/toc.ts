export interface Heading {
  id: string;
  text: string;
  level: number;
}

/**
 * Generate a URL-safe ID from heading text
 */
export function generateHeadingId(text: string): string {
  return text
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/(^-|-$)/g, '');
}

/**
 * Extract H2 headings only from markdown content (main sections)
 * H3 and H4 are subsections and can clutter the TOC
 */
export function extractHeadings(content: string): Heading[] {
  const headingRegex = /^(#{2})\s+(.+)$/gm;
  const matches = Array.from(content.matchAll(headingRegex));

  return matches.map((match) => {
    const level = match[1].length;
    const text = match[2].trim();
    const id = generateHeadingId(text);

    return { id, text, level };
  });
}
