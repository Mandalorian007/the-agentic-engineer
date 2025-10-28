import fs from "fs";
import path from "path";

/**
 * Get the hero image path for a blog post slug
 *
 * Scans the public/blog/{slug}/ directory for a hero-*.webp file
 * and returns the absolute URL for use in Open Graph and Twitter Card metadata.
 *
 * @param slug - The blog post slug (e.g., "2025-11-20-afternoon-build-full-stack-saas")
 * @returns Full URL to hero image or null if not found
 */
export function getHeroImagePath(slug: string): string | null {
  try {
    // Construct path to post image directory
    const imageDir = path.join(process.cwd(), "public", "blog", slug);

    // Check if directory exists
    if (!fs.existsSync(imageDir)) {
      return null;
    }

    // Read all files in directory
    const files = fs.readdirSync(imageDir);

    // Find first file matching hero-*.webp pattern
    const heroImage = files
      .filter((file) => file.startsWith("hero-") && file.endsWith(".webp"))
      .sort()[0]; // Sort alphabetically and take first match

    if (!heroImage) {
      return null;
    }

    // Return absolute URL (required for social media metadata)
    return `https://agentic-engineer.com/blog/${slug}/${heroImage}`;
  } catch (error) {
    // Gracefully handle any errors (permissions, fs issues, etc.)
    console.error(`Error finding hero image for slug "${slug}":`, error);
    return null;
  }
}
