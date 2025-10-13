/**
 * Legal document utilities
 * Loads privacy policy and terms of service from markdown files
 */

import fs from "fs";
import path from "path";

const legalDir = path.join(process.cwd(), "content", "legal");

export interface LegalDocument {
  content: string;
  lastUpdated: string | null;
}

/**
 * Load a legal document by filename
 */
export function getLegalDocument(filename: string): LegalDocument {
  const filePath = path.join(legalDir, filename);
  const content = fs.readFileSync(filePath, "utf-8");

  // Extract last updated date from the markdown
  const lastUpdatedMatch = content.match(/\*\*Last Updated:\*\* (.+)/);
  const lastUpdated = lastUpdatedMatch ? lastUpdatedMatch[1] : null;

  return {
    content,
    lastUpdated,
  };
}

/**
 * Get privacy policy
 */
export function getPrivacyPolicy(): LegalDocument {
  return getLegalDocument("privacy-policy.md");
}

/**
 * Get terms of service
 */
export function getTermsOfService(): LegalDocument {
  return getLegalDocument("terms-of-service.md");
}
