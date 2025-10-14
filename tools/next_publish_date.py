#!/usr/bin/env python3
"""
Get the next Monday publish date for blog post scheduling.

Usage:
    uv run tools/next_publish_date.py
"""

import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional


def get_next_monday(date: datetime) -> datetime:
    """Get the next Monday after the given date."""
    # weekday(): Monday is 0, Sunday is 6
    days_until_monday = (7 - date.weekday()) % 7
    if days_until_monday == 0:
        # If today is Monday, get next Monday
        days_until_monday = 7

    next_monday = date + timedelta(days=days_until_monday)
    return next_monday.replace(hour=10, minute=0, second=0, microsecond=0)


def extract_date_from_filename(filename: str) -> Optional[datetime]:
    """Extract date from post filename (YYYY-MM-DD-slug.mdx format)."""
    # Remove .mdx extension if present
    name = filename.replace('.mdx', '')
    parts = name.split('-')
    if len(parts) < 4:  # Need at least YYYY-MM-DD-slug
        return None

    try:
        year = int(parts[0])
        month = int(parts[1])
        day = int(parts[2])
        return datetime(year, month, day)
    except (ValueError, IndexError):
        return None


def get_all_post_dates(posts_dir: Path) -> List[datetime]:
    """Get all post dates from MDX filenames."""
    dates = []

    if not posts_dir.exists():
        return dates

    for item in posts_dir.iterdir():
        if item.is_file() and item.suffix == '.mdx':
            date = extract_date_from_filename(item.name)
            if date:
                dates.append(date)

    return sorted(dates)


def format_date_for_dirname(date: datetime) -> str:
    """Format date for directory name (YYYY-MM-DD)."""
    return date.strftime("%Y-%m-%d")


def format_date_for_frontmatter(date: datetime) -> str:
    """Format date for frontmatter (ISO 8601 with timezone)."""
    return date.strftime("%Y-%m-%dT%H:%M:%SZ")


def main():
    posts_dir = Path("website/content/posts")

    # Get all existing post dates
    post_dates = get_all_post_dates(posts_dir)

    # Determine starting date (latest post or today)
    if post_dates:
        after_date = post_dates[-1]
    else:
        after_date = datetime.now()

    # Get next Monday
    next_monday = get_next_monday(after_date)

    # Check if this Monday is already taken
    while next_monday in post_dates:
        print(f"⚠️  {format_date_for_dirname(next_monday)} is already scheduled, trying next Monday...")
        next_monday = get_next_monday(next_monday)

    # Output the result
    print("Next available Monday for publishing:")
    print("-" * 40)
    print(f"Directory name: {format_date_for_dirname(next_monday)}-your-slug-here")
    print(f"Frontmatter date: {format_date_for_frontmatter(next_monday)}")
    print(f"Day: {next_monday.strftime('%A, %B %d, %Y')}")
    print("-" * 40)

    # Show context
    if post_dates:
        latest = post_dates[-1]
        print(f"\nLatest scheduled post: {format_date_for_dirname(latest)} ({latest.strftime('%A')})")
        days_diff = (next_monday - latest).days
        print(f"Days until next post: {days_diff}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
