"""Shared content-stream lookups.

Blog posts and newsletter issues use the same on-disk convention
(``YYYY-MM-DD-slug.mdx`` with an ISO 8601 ``date`` in frontmatter), so finding
"the entry scheduled for this date" is one function for both.
"""

from datetime import date as date_type, datetime, timezone
from pathlib import Path
from typing import Optional, Tuple

from lib.frontmatter import parse_frontmatter


def parse_entry_date(value) -> Optional[date_type]:
    """Parse a frontmatter date into a calendar date, tolerating a trailing Z."""
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.date()
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00")).date()
    except ValueError:
        return None


def load_entries(content_dir: Path) -> list:
    """
    Every parseable entry in a stream, oldest first.

    Returns a list of ``(path, frontmatter, body, date)``. Files that fail to
    parse or carry no usable date are warned about and skipped rather than
    raising: one bad file should not stop the day's email from going out.
    """
    if not content_dir.exists():
        return []

    entries = []

    for mdx_file in sorted(content_dir.glob("*.mdx")):
        try:
            frontmatter, body = parse_frontmatter(mdx_file.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"⚠️  Warning: Failed to parse {mdx_file.name}: {e}")
            continue

        entry_date = parse_entry_date(frontmatter.get("date"))
        if entry_date is None:
            print(f"⚠️  Warning: {mdx_file.name} has no usable `date`, skipping")
            continue

        entries.append((mdx_file, frontmatter, body, entry_date))

    entries.sort(key=lambda entry: (entry[3], entry[0].name))
    return entries


def get_entry_for_date(
    content_dir: Path,
    target_date: Optional[date_type] = None,
) -> Optional[Tuple[Path, dict, str]]:
    """
    Find the single entry scheduled for a date.

    Args:
        content_dir: Directory of ``YYYY-MM-DD-slug.mdx`` files
        target_date: Date to look for (defaults to today UTC)

    Returns:
        ``(path, frontmatter, body)`` for the match, or None.

        When more than one file claims the same date the first by filename wins
        and a warning is printed. Sending two emails for one slot is worse than
        sending the wrong one of two, which a dry run would have caught.
    """
    if target_date is None:
        target_date = datetime.now(timezone.utc).date()

    matches = [e for e in load_entries(content_dir) if e[3] == target_date]

    if not matches:
        return None

    if len(matches) > 1:
        names = ", ".join(m[0].name for m in matches)
        print(f"⚠️  Warning: {len(matches)} entries dated {target_date}: {names}")
        print(f"   Using {matches[0][0].name}")

    path, frontmatter, body, _ = matches[0]
    return path, frontmatter, body


def get_previous_entry_date(
    content_dir: Path,
    before_date: date_type,
) -> Optional[date_type]:
    """Date of the most recent entry strictly before ``before_date``, if any."""
    earlier = [e[3] for e in load_entries(content_dir) if e[3] < before_date]
    return earlier[-1] if earlier else None


def get_latest_entry_in_window(
    content_dir: Path,
    after: date_type,
    through: date_type,
) -> Optional[Tuple[Path, dict, str]]:
    """
    The newest entry published in ``(after, through]``.

    Half-open at the start so an entry that was already covered by the previous
    issue is not attached twice, and inclusive at the end so a post shipping the
    same morning as the issue still counts.
    """
    in_window = [e for e in load_entries(content_dir) if after < e[3] <= through]

    if not in_window:
        return None

    path, frontmatter, body, _ = in_window[-1]
    return path, frontmatter, body
