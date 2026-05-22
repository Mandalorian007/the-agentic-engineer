// Single source of truth for author credentials and contact surface.
// Used by /about, the homepage hero, /services, and the post-page author bio.
// If you update the EXPERIENCE timeline on /about, sync the JSON-LD constants there too.

export const AUTHOR_NAME = "Matthew Fontana";
export const CURRENT_ROLE = "Staff Engineer at Airbnb";
export const PRIOR_ROLES_SHORT = "ex-Spotify, ex-UPS";

// Anchor for the tenure badge. Update only if the canonical start year changes.
export const ENTERPRISE_START_YEAR = 2013;
export const TENURE_YEARS = new Date().getFullYear() - ENTERPRISE_START_YEAR;

export const CONTACT_EMAIL = "matthew.fontana@agentic-engineer.com";
export const GITHUB_URL = "https://github.com/Mandalorian007";
export const LINKEDIN_URL = "https://www.linkedin.com/in/matthew-fontana/";
export const TAC_URL = "https://tabletopadventurecreator.com";

// One-line credential summary used in homepage byline, services Why-me, and post author bio.
export const CREDENTIAL_LINE = `${CURRENT_ROLE} · ${PRIOR_ROLES_SHORT} · ${TENURE_YEARS} yrs in enterprise software`;
