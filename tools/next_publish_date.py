#!/usr/bin/env python3
"""
Get the next publish date based on configured schedule.

Usage:
    uv run tools/next_publish_date.py
"""

import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional

# Add parent directory to path to import lib modules
sys.path.insert(0, str(Path(__file__).parent.parent))
from lib.config import load_config, get_publishing_config


# Map day names to weekday numbers (Python's datetime convention)
DAY_MAP = {
    'monday': 0,
    'tuesday': 1,
    'wednesday': 2,
    'thursday': 3,
    'friday': 4,
    'saturday': 5,
    'sunday': 6
}


def get_next_publish_date(after_date: datetime, publish_days: List[str], publish_time: str) -> datetime:
    """
    Get the next publish date based on configured days.

    Args:
        after_date: Find next publish date after this date
        publish_days: List of day names (e.g., ["monday", "thursday"])
        publish_time: Time to publish in HH:MM:SS format

    Returns:
        Next available publish date as datetime
    """
    # Parse publish time
    time_parts = publish_time.split(':')
    hour = int(time_parts[0])
    minute = int(time_parts[1]) if len(time_parts) > 1 else 0
    second = int(time_parts[2]) if len(time_parts) > 2 else 0

    # Convert day names to weekday numbers
    target_weekdays = [DAY_MAP[day.lower()] for day in publish_days]
    target_weekdays.sort()  # Sort for consistent behavior

    # Start from the day after after_date
    current_date = after_date + timedelta(days=1)
    current_date = current_date.replace(hour=hour, minute=minute, second=second, microsecond=0)

    # Find the next occurrence of any target weekday
    days_checked = 0
    max_days = 7  # At most we need to check 7 days ahead

    while days_checked < max_days:
        if current_date.weekday() in target_weekdays:
            return current_date
        current_date += timedelta(days=1)
        days_checked += 1

    # This should never happen if target_weekdays is valid
    raise ValueError(f"Could not find next publish date. Check publish_days: {publish_days}")


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
        publish_days = pub_config['days']
        publish_time = pub_config['time']
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
    next_date = get_next_publish_date(after_date, publish_days, publish_time)

    # Check if this date is already taken
    while next_date in post_dates:
        print(f"⚠️  {format_date_for_dirname(next_date)} is already scheduled, trying next publish day...")
        next_date = get_next_publish_date(next_date, publish_days, publish_time)

    # Output the result
    days_str = ", ".join([day.capitalize() for day in publish_days])
    print(f"Next available publish date ({days_str}):")
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
