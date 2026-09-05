/**
 * Site and author identity: one source of truth.
 *
 * These strings end up in metadata, JSON-LD, the RSS feed, and the visible
 * byline on every post. They were previously duplicated across five files
 * and drifted apart, so change them here and nowhere else.
 */

/**
 * The canonical origin. No www.
 *
 * Canonicals, OG urls, JSON-LD, the feed, and the sitemap all derive from
 * this, so it has to be the host Vercel actually serves as primary. If www is
 * ever made primary again, every one of those starts pointing at a redirect.
 */
export const SITE_URL = "https://agentic-engineer.com";

/**
 * The origin used to mint permanent feed identifiers. Frozen on purpose.
 *
 * RSS GUIDs are opaque keys, not addresses (ours carry isPermaLink="false").
 * A reader that sees a new GUID shows the item as new, so deriving them from
 * SITE_URL means any future host change silently republishes the whole archive
 * to every subscriber. Items already in the wild were minted against the apex.
 *
 * It currently matches SITE_URL. That is a coincidence, not a rule, and the
 * two must stay separate constants: SITE_URL is where the site is today, this
 * is what every already-delivered feed item was keyed on. Never change it.
 */
export const FEED_ID_ORIGIN = "https://agentic-engineer.com";
export const SITE_NAME = "The Agentic Engineer";

export const SITE_DESCRIPTION =
  "Encode the checks, guardrails, and judgment you already have, then hand work to agents one step at a time. AI development workflows by a builder, for builders.";

/** Shorter form, for the RSS channel and other tight slots. */
export const SITE_TAGLINE =
  "Encoding what you're great at into agent workflows. By a builder, for builders.";

/**
 * The newsletter. Named separately from the site because it is its own thing:
 * subscribers get the letter first, the archive follows a month later.
 */
export const NEWSLETTER_NAME = "Agentic Engineer Journey";

export const AUTHOR = {
  name: "Matthew Fontana",
  /** The brand name doubles as the job title. That is the whole point of it. */
  title: "Agentic Engineer",
  location: "Hoboken, NJ",
  role: "Staff engineer at Airbnb",
  email: "matthew.fontana@agentic-engineer.com",
  url: `${SITE_URL}/about`,
  github: "https://github.com/Mandalorian007",
  linkedin: "https://www.linkedin.com/in/matthew-fontana/",
  avatar: "/about/matthew-fontana.webp",
} as const;

/** The signature line. Swap the separator here and it changes everywhere. */
export const AUTHOR_SIGNATURE = `${AUTHOR.name}, ${AUTHOR.title}`;
