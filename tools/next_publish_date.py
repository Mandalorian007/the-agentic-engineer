#!/usr/bin/env python3
"""
Get the next publish date based on configured schedule.

Usage:
    uv run tools/next_publish_date.py                       # next blog post slot
    uv run tools/next_publish_date.py --stream newsletter   # next issue slot
    uv run tools/next_publish_date.py --count 4             # plan a batch ahead
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Optional

# Add parent directory to path to import lib modules
sys.path.insert(0, str(Path(__file__).parent.parent))
from lib.config import load_config, get_publishing_config, get_stream_config
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


def get_all_post_dates(content_dir: Path) -> List[datetime]:
    """Get all entry dates from MDX filenames in a content directory."""
    dates = []

    if not content_dir.exists():
        return dates

    for item in content_dir.iterdir():
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
    parser = argparse.ArgumentParser(
        description="Get the next available publish date for a content stream"
    )
    parser.add_argument(
        "--stream",
        choices=["posts", "newsletter"],
        default="posts",
        help="Which content stream to schedule into (default: posts)",
    )
    parser.add_argument(
        "--count",
        type=int,
        default=1,
        help="How many upcoming slots to show (default: 1)",
    )
    args = parser.parse_args()

    if args.count < 1:
        print("❌ --count must be at least 1", file=sys.stderr)
        sys.exit(1)

    # Load configuration
    try:
        config = load_config()
        pub_config = get_publishing_config(config, args.stream)
        stream_cfg = get_stream_config(config, args.stream)
        other = "newsletter" if args.stream == "posts" else "posts"
        other_cfg = get_stream_config(config, other)
    except Exception as e:
        print(f"❌ Error loading configuration: {e}", file=sys.stderr)
        sys.exit(1)

    content_dir = stream_cfg["content_dir"]

    # Get all existing dates in this stream
    post_dates = get_all_post_dates(content_dir)

    # Dates taken in the OTHER stream are not collisions. A post and an issue
    # sharing a Monday is the intended pairing, so we only look them up to
    # report on it.
    paired_dates = {d.date() for d in get_all_post_dates(other_cfg["content_dir"])}

    # Determine starting date (latest entry or today)
    if post_dates:
        after_date = post_dates[-1]
    else:
        after_date = datetime.now()

    # Get next publish date based on configuration
    next_date = get_next_publish_date(after_date, pub_config)

    # Existing entries are stored at midnight (filename precision); candidates
    # carry the publish time. Compare by calendar date so collisions resolve
    # correctly even when the time-of-day differs.
    post_calendar_dates = {d.date() for d in post_dates}
    while next_date.date() in post_calendar_dates:
        print(f"⚠️  {format_date_for_dirname(next_date)} is already scheduled, trying next publish day...")
        next_date = get_next_publish_date(next_date, pub_config)

    # If the cadence has fallen behind real time, advance past today so the
    # answer is always a future slot you can actually publish into.
    today = datetime.now()
    while next_date < today:
        next_date = get_next_publish_date(next_date, pub_config)

    # Output the result
    schedule_label = format_schedule_label(pub_config)
    print(f"Next available {stream_cfg['noun']} date ({schedule_label}):")
    print("-" * 40)
    print(f"Directory name: {format_date_for_dirname(next_date)}-your-slug-here")
    print(f"Frontmatter date: {format_date_for_frontmatter(next_date)}")
    print(f"Day: {next_date.strftime('%A, %B %d, %Y')}")
    # "Same day" rather than "paired": an issue with no post on its own date can
    # still carry an earlier one, so absence here does not mean it ships alone.
    print(f"Same-day {other_cfg['noun']}: "
          f"{'yes' if next_date.date() in paired_dates else 'none'}")
    print("-" * 40)

    # Further slots, for planning a batch before travel
    if args.count > 1:
        print(f"\nNext {args.count} slots:")
        slot = next_date
        taken = set(post_calendar_dates)
        for _ in range(args.count):
            while slot.date() in taken:
                slot = get_next_publish_date(slot, pub_config)
            noun = other_cfg["noun"]
            pair = f"same-day {noun}" if slot.date() in paired_dates else f"no same-day {noun}"
            print(f"  {format_date_for_dirname(slot)}  {slot.strftime('%A')}  ({pair})")
            taken.add(slot.date())

    # Show context
    if post_dates:
        latest = post_dates[-1]
        print(f"\nLatest scheduled {stream_cfg['noun']}: "
              f"{format_date_for_dirname(latest)} ({latest.strftime('%A')})")
        days_diff = (next_date - latest).days
        print(f"Days until next {stream_cfg['noun']}: {days_diff}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
