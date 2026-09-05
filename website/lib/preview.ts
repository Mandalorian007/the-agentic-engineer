/**
 * Whether unpublished content is readable at its own URL.
 *
 * Posts and issues are written weeks ahead of their date, and the only honest
 * way to check one is to look at the rendered page. So scheduled content stays
 * reachable in development and on preview deployments, and 404s in production.
 *
 * PREVIEW_UNPUBLISHED wins whenever it is set to "true" or "false", so you can
 * flip it off locally to see exactly what the public sees. Unset, it falls back
 * to "on outside production", which is what makes `next dev` work with no
 * configuration at all.
 *
 * Set it to "true" on Vercel's Preview environment. Never on Production.
 *
 * Anything rendered under this flag is also marked noindex by its caller, so a
 * preview URL that leaks cannot be indexed as real content.
 */
export function previewUnpublished(): boolean {
  const flag = process.env.PREVIEW_UNPUBLISHED;

  if (flag === "true") return true;
  if (flag === "false") return false;

  return process.env.NODE_ENV !== "production";
}
