import fs from 'fs';
import path from 'path';
import matter from 'gray-matter';
import { calculateReadingTime } from './reading-time';

const issuesDirectory = path.join(process.cwd(), 'content/issues');

/**
 * Days between an issue being emailed and its archive page going public.
 * Must match `newsletter.archive_delay_days` in blog-config.yaml.
 */
export const DEFAULT_ARCHIVE_DELAY_DAYS = 30;

export interface Issue {
  slug: string;
  title: string;
  subject: string;
  description: string;
  /** When the email goes out. */
  date: string;
  /** When this page becomes publicly visible. Always resolved. */
  archiveDate: string;
  content: string;
  readingTime: number;
}

/** Adds whole days as elapsed time. setDate() works in server-local wall clock,
 *  which shifts the result by an hour across a DST boundary. */
function addDays(date: Date, days: number): Date {
  return new Date(date.getTime() + days * 24 * 60 * 60 * 1000);
}

/** Throws on a missing or unparseable date rather than yielding Invalid Date. */
function requireDate(value: unknown, field: string, fileName: string): Date {
  const parsed = new Date(value as string | Date);
  if (!value || Number.isNaN(parsed.getTime())) {
    throw new Error(`${fileName}: ${field} is missing or unparseable (${String(value)})`);
  }
  return parsed;
}

function parseIssue(fileName: string): Issue {
  const slug = fileName.replace(/\.mdx$/, '');
  const fullPath = path.join(issuesDirectory, fileName);
  const { data, content } = matter(fs.readFileSync(fullPath, 'utf8'));

  const sentAt = requireDate(data.date, 'date', fileName);

  // A missing archive_date defaults to "public later" rather than "public now".
  // Getting this backwards would leak an issue before subscribers received it.
  const archiveDate = data.archive_date
    ? requireDate(data.archive_date, 'archive_date', fileName)
    : addDays(sentAt, DEFAULT_ARCHIVE_DELAY_DAYS);

  return {
    slug,
    title: data.title,
    subject: data.subject ?? data.title,
    description: data.description,
    // Normalized: an unquoted YAML date parses to a Date, not a string, and
    // would otherwise reach <time dateTime> as "Mon Jan 05 2026 06:00:00 GMT…"
    date: sentAt.toISOString(),
    archiveDate: archiveDate.toISOString(),
    content,
    readingTime: calculateReadingTime(content),
  };
}

/**
 * Get every issue on disk, including unsent and unarchived ones.
 * Sorted by send date descending. Not for public rendering.
 */
export function getAllIssues(): Issue[] {
  if (!fs.existsSync(issuesDirectory)) {
    return [];
  }

  return fs
    .readdirSync(issuesDirectory)
    .filter((fileName) => fileName.endsWith('.mdx'))
    .map((fileName) => {
      // One malformed file must not take down /issues and the sitemap with it.
      // At build time an uncaught throw here fails the whole production deploy.
      try {
        return parseIssue(fileName);
      } catch (error) {
        console.error(`Skipping issue: ${(error as Error).message}`);
        return null;
      }
    })
    .filter((issue): issue is Issue => issue !== null)
    .sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime());
}

/**
 * Whether an issue is publicly readable.
 *
 * Both clauses matter. The archive date is the delay that makes subscribing
 * worth something; the send date guard stops a pre-written issue with a
 * mistyped archive_date from appearing before it has actually been emailed.
 */
export function isArchived(issue: Issue, now: Date = new Date()): boolean {
  return new Date(issue.date) <= now && new Date(issue.archiveDate) <= now;
}

/** Issues whose archive delay has elapsed. This is the public list. */
export function getArchivedIssues(): Issue[] {
  const now = new Date();
  return getAllIssues().filter((issue) => isArchived(issue, now));
}

/**
 * Get one issue by slug, ungated.
 *
 * Callers that render publicly must check isArchived() themselves. Kept
 * ungated so tooling and previews can reach unpublished issues.
 */
export function getIssueBySlug(slug: string): Issue | null {
  try {
    return parseIssue(`${slug}.mdx`);
  } catch {
    return null;
  }
}

/** Slugs safe to pre-render. */
export function getArchivedIssueSlugs(): string[] {
  return getArchivedIssues().map((issue) => issue.slug);
}
