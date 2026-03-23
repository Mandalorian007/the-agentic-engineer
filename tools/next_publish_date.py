#!/usr/bin/env python3
"""
Get the next publish date based on configured schedule.

Usage:
    uv run tools/next_publish_date.py
"""

import sys
from datetime import datetime
from pathlib import Path
from typing import List, Optional

# Add parent directory to path to import lib modules
sys.path.insert(0, str(Path(__file__).parent.parent))
from lib.config import load_config, get_publishing_config
from lib.scheduling import get_next_publish_date, format_schedule_label


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
    # Load configuration
    try:
        config = load_config()
        pub_config = get_publishing_config(config)
    except Exception as e:
        print(f"❌ Error loading configuration: {e}", file=sys.stderr)
        sys.exit(1)

    posts_dir = Path("website/content/posts")

    # Get all existing post dates
    post_dates = get_all_post_dates(posts_dir)

    # Determine starting date (latest post or today)
    if post_dates:
        after_date = post_dates[-1]
    else:
        after_date = datetime.now()

    # Get next publish date based on configuration
    next_date = get_next_publish_date(after_date, pub_config)

    # Check if this date is already taken
    while next_date in post_dates:
        print(f"⚠️  {format_date_for_dirname(next_date)} is already scheduled, trying next publish day...")
        next_date = get_next_publish_date(next_date, pub_config)

    # Output the result
    schedule_label = format_schedule_label(pub_config)
    print(f"Next available publish date ({schedule_label}):")
    print("-" * 40)
    print(f"Directory name: {format_date_for_dirname(next_date)}-your-slug-here")
    print(f"Frontmatter date: {format_date_for_frontmatter(next_date)}")
    print(f"Day: {next_date.strftime('%A, %B %d, %Y')}")
    print("-" * 40)

    # Show context
    if post_dates:
        latest = post_dates[-1]
        print(f"\nLatest scheduled post: {format_date_for_dirname(latest)} ({latest.strftime('%A')})")
        days_diff = (next_date - latest).days
        print(f"Days until next post: {days_diff}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
