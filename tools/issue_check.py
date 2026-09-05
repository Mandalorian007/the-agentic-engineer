#!/usr/bin/env python3
"""
Quality checker for newsletter issues (MDX format).

The blog's seo_check.py cannot be reused here: it requires a `category` from the
blog's seven, and issues have none. This is the lighter sibling for issues.

Usage:
    uv run tools/issue_check.py website/content/issues/2026-09-21-slug.mdx
"""

import argparse
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from lib.config import load_config, get_newsletter_config
from lib.frontmatter import parse_frontmatter, FrontmatterError

# Most email clients truncate subject lines past roughly this length.
SUBJECT_MAX = 50
DESCRIPTION_MIN = 150
DESCRIPTION_MAX = 160
# Shorter than this and it is a note, not an issue. Longer and it wants to be a post.
BODY_MIN_WORDS = 250
BODY_MAX_WORDS = 900

REQUIRED_FIELDS = ['title', 'subject', 'description', 'date']


def parse_date(value) -> datetime:
    """Parse an ISO 8601 frontmatter date, tolerating the trailing Z."""
    if isinstance(value, datetime):
        return value.replace(tzinfo=None)
    text = str(value).strip().replace('Z', '+00:00')
    return datetime.fromisoformat(text).replace(tzinfo=None)


def analyze_issue(issue_path: Path, archive_delay_days: int) -> tuple[list, list]:
    """
    Check one issue file.

    Returns:
        (errors, warnings) as lists of strings
    """
    errors: list[str] = []
    warnings: list[str] = []

    if not issue_path.exists():
        return [f"File not found: {issue_path}"], []

    if issue_path.suffix != '.mdx':
        return [f"Expected a .mdx file, got {issue_path.suffix}"], []

    try:
        frontmatter, body = parse_frontmatter(issue_path.read_text(encoding='utf-8'))
    except (OSError, FrontmatterError) as e:
        return [f"Could not parse frontmatter: {e}"], []

    # --- required fields ---
    for field in REQUIRED_FIELDS:
        if not frontmatter.get(field):
            errors.append(f"Missing required frontmatter field: {field}")

    # --- subject ---
    subject = str(frontmatter.get('subject', ''))
    if subject:
        if len(subject) > SUBJECT_MAX:
            warnings.append(
                f"Subject is {len(subject)} chars, over {SUBJECT_MAX}. "
                f"Most clients will truncate it."
            )
        else:
            print(f"  Subject: {len(subject)}/{SUBJECT_MAX} chars")

    # --- description ---
    description = str(frontmatter.get('description', ''))
    if description:
        if len(description) < DESCRIPTION_MIN:
            warnings.append(
                f"Description is {len(description)} chars, under {DESCRIPTION_MIN}. "
                f"Aim for {DESCRIPTION_MIN}-{DESCRIPTION_MAX}."
            )
        elif len(description) > DESCRIPTION_MAX:
            warnings.append(
                f"Description is {len(description)} chars, over {DESCRIPTION_MAX}. "
                f"Search results will cut it off."
            )
        else:
            print(f"  Description: {len(description)}/{DESCRIPTION_MAX} chars")

    # --- dates ---
    send_date = None
    if frontmatter.get('date'):
        try:
            send_date = parse_date(frontmatter['date'])
        except ValueError:
            errors.append(f"Invalid date: {frontmatter['date']!r} (expected ISO 8601)")

    if frontmatter.get('archive_date'):
        try:
            archive_date = parse_date(frontmatter['archive_date'])
            if send_date and archive_date <= send_date:
                errors.append(
                    f"archive_date ({archive_date:%Y-%m-%d}) must be after "
                    f"date ({send_date:%Y-%m-%d}). Otherwise the archive page "
                    f"goes public before subscribers get the email."
                )
            elif send_date:
                gap = (archive_date - send_date).days
                print(f"  Archive delay: {gap} days")
        except ValueError:
            errors.append(
                f"Invalid archive_date: {frontmatter['archive_date']!r} (expected ISO 8601)"
            )
    elif send_date:
        default = send_date + timedelta(days=archive_delay_days)
        print(f"  Archive delay: {archive_delay_days} days (default) "
              f"-> {default:%Y-%m-%d}")

    # --- body ---
    word_count = len(body.split())
    if word_count < BODY_MIN_WORDS:
        warnings.append(
            f"Body is {word_count} words, under {BODY_MIN_WORDS}. "
            f"Thin for an issue."
        )
    elif word_count > BODY_MAX_WORDS:
        warnings.append(
            f"Body is {word_count} words, over {BODY_MAX_WORDS}. "
            f"This may want to be a blog post."
        )
    else:
        print(f"  Body: {word_count} words")

    # --- issue-specific content checks ---
    if '](../../public/' in body:
        errors.append(
            "Issue references a local image. Issues carry no image directory; "
            "images belong in the blog post."
        )

    if '```' not in body:
        warnings.append(
            "No code block found. Every issue should carry one pasteable artifact."
        )

    if 'category' in frontmatter:
        warnings.append(
            "`category` is set but issues are not part of the blog taxonomy. Remove it."
        )

    return errors, warnings


# The website cannot read blog-config.yaml at build time, so the archive delay
# is stated in two places. Nothing links them, and a change to one silently
# leaves the site holding issues back for a different number of days than the
# tooling reports.
ISSUES_TS = Path("website/lib/issues.ts")
_DELAY_RE = re.compile(r"DEFAULT_ARCHIVE_DELAY_DAYS\s*=\s*(\d+)")


def check_archive_delay_agreement(config_delay: int) -> list:
    """Warn when blog-config.yaml and website/lib/issues.ts disagree."""
    if not ISSUES_TS.exists():
        return []

    match = _DELAY_RE.search(ISSUES_TS.read_text())
    if not match:
        return [f"Could not find DEFAULT_ARCHIVE_DELAY_DAYS in {ISSUES_TS}"]

    site_delay = int(match.group(1))
    if site_delay != config_delay:
        return [
            f"Archive delay mismatch: blog-config.yaml says {config_delay} days, "
            f"{ISSUES_TS} says {site_delay}. The site is what readers get."
        ]
    return []


def main() -> int:
    parser = argparse.ArgumentParser(description="Quality check a newsletter issue")
    parser.add_argument("path", help="Path to the issue .mdx file")
    args = parser.parse_args()

    try:
        newsletter = get_newsletter_config(load_config())
    except Exception as e:
        print(f"❌ Error loading configuration: {e}", file=sys.stderr)
        return 1

    issue_path = Path(args.path)
    print(f"\n📋 Issue check: {issue_path.name}")
    print("=" * 60)

    errors, warnings = analyze_issue(issue_path, newsletter['archive_delay_days'])
    warnings.extend(check_archive_delay_agreement(newsletter['archive_delay_days']))

    for error in errors:
        print(f"❌ {error}")
    for warning in warnings:
        print(f"⚠️  {warning}")

    if not errors and not warnings:
        print("✅ No issues found")

    print(f"\nTotal: {len(errors)} error(s), {len(warnings)} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
