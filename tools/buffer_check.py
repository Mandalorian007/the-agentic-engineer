#!/usr/bin/env python3
"""
Check content buffer across every content stream and report to Discord.

Usage:
    uv run tools/buffer_check.py                      # both streams
    uv run tools/buffer_check.py --stream posts       # just the blog
    uv run tools/buffer_check.py --webhook-url URL

Environment Variables:
    LOW_CONTENT_WEBHOOK: Discord webhook URL
"""

import os
import sys
import json
import argparse
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Optional
import requests
import yaml
from dotenv import load_dotenv

# Add parent directory to path to import lib modules
sys.path.insert(0, str(Path(__file__).parent.parent))
from lib.config import (
    load_config,
    get_publishing_config,
    get_publishing_rate,
    get_stream_config,
    get_newsletter_config,
)
from lib.scheduling import get_next_publish_date, format_schedule_label

# Auto-load .env.local if it exists (for local testing)
# How far ahead the slot ledger looks.
LOOKAHEAD_MONTHS = 2

project_root = Path(__file__).parent.parent
env_file = project_root / ".env.local"
if env_file.exists():
    load_dotenv(env_file)


def extract_title_from_mdx(mdx_file: Path) -> Optional[str]:
    """Extract title from MDX frontmatter."""
    try:
        content = mdx_file.read_text(encoding='utf-8')

        # Check if file starts with frontmatter
        if not content.startswith('---'):
            return None

        # Find the end of frontmatter
        parts = content.split('---', 2)
        if len(parts) < 3:
            return None

        # Parse YAML frontmatter
        frontmatter = yaml.safe_load(parts[1])
        return frontmatter.get('title', None)
    except Exception:
        return None


def get_scheduled_posts(content_dir: Path) -> List[Dict[str, any]]:
    """Get all posts with future publish dates."""
    scheduled_posts = []
    now = datetime.now(timezone.utc)

    for mdx_file in content_dir.glob("*.mdx"):
        # Extract date from filename (YYYY-MM-DD-slug.mdx)
        filename = mdx_file.name
        date_str = filename[:10]  # First 10 chars: YYYY-MM-DD

        try:
            # Parse date and set to 10am UTC (same as frontmatter)
            post_date = datetime.strptime(date_str, "%Y-%m-%d")
            post_date = post_date.replace(hour=10, minute=0, second=0, tzinfo=timezone.utc)

            # Only include future posts
            if post_date > now:
                title = extract_title_from_mdx(mdx_file) or filename
                scheduled_posts.append({
                    "filename": filename,
                    "title": title,
                    "date": post_date,
                    "date_str": date_str
                })
        except ValueError:
            # Skip files that don't match YYYY-MM-DD format
            continue

    # Sort by date
    scheduled_posts.sort(key=lambda x: x["date"])
    return scheduled_posts


def get_upcoming_slots(pub_config: Dict, count: int = 6,
                       now: datetime = None) -> List[datetime]:
    """Get the next N publish slots from the schedule."""
    if now is None:
        now = datetime.now(timezone.utc)

    slots = []
    cursor = now.replace(tzinfo=None)
    for _ in range(count):
        cursor = get_next_publish_date(cursor, pub_config)
        slots.append(cursor.replace(tzinfo=timezone.utc))
    return slots


def build_slot_ledger(slots: List[datetime],
                      items_by_stream: Dict[str, List[Dict]]) -> List[Dict]:
    """
    Pair up what is scheduled against each upcoming slot.

    Both streams share a cadence so a slot can hold a post, an issue, both, or
    nothing. Reporting them as two independent buffers would hide exactly the
    thing worth seeing.
    """
    ledger = []
    for slot in slots:
        slot_str = slot.strftime("%Y-%m-%d")
        row = {"date": slot, "date_str": slot_str}
        for stream, items in items_by_stream.items():
            row[stream] = next(
                (i for i in items if i["date_str"] == slot_str), None
            )
        ledger.append(row)
    return ledger


def find_off_cadence(slots: List[datetime],
                     items_by_stream: Dict[str, List[Dict]]) -> List[Dict]:
    """
    Scheduled items that do not land on any upcoming slot.

    Without this, an entry moved to a Tuesday silently disappears from the
    report and looks like missing content.
    """
    slot_strs = {s.strftime("%Y-%m-%d") for s in slots}
    horizon = max(slots).strftime("%Y-%m-%d") if slots else ""

    off = []
    for stream, items in items_by_stream.items():
        for item in items:
            if item["date_str"] not in slot_strs and item["date_str"] <= horizon:
                off.append({**item, "stream": stream})
    return sorted(off, key=lambda i: i["date_str"])


# Status is rated on how many upcoming slots are filled before the first gap.
# Counting slots rather than converting to fractional months keeps the rating
# readable straight off the ledger, and keeps its meaning if the cadence changes.
LOW_MAX_RUN = 0      # the very next slot has a gap
WARN_MAX_RUN = 2     # a gap inside the next two or three slots


def slot_status(filled_run: int) -> tuple:
    """Rate one stream. Returns (label, color, rank); a higher rank is worse."""
    if filled_run <= LOW_MAX_RUN:
        return "🚨 LOW", 0xE74C3C, 2
    if filled_run <= WARN_MAX_RUN:
        return "⚠️ WARN", 0xF1C40F, 1
    return "✅ GOOD", 0x2ECC71, 0


def stream_view(stream: str, stats: Dict, ledger: List[Dict]) -> Dict:
    """
    One stream's slot picture over the lookahead window.

    Single source of truth for both renderers: the terminal report and the
    Discord embed previously formatted the same numbers independently and had
    drifted on labels, precision and the empty case.
    """
    rows = [(row["date"], row.get(stream)) for row in ledger]

    filled_run = 0
    for _, item in rows:
        if not item:
            break
        filled_run += 1

    status, color, rank = slot_status(filled_run)

    return {
        "stream": stream,
        "emoji": stats["emoji"],
        "label": stats["label"],
        "rows": rows,
        "filled": sum(1 for _, item in rows if item),
        "total": len(rows),
        "first_gap": next((d for d, item in rows if not item), None),
        "status": status,
        "color": color,
        "rank": rank,
    }


def format_view_header(view: Dict) -> str:
    """`📝 Posts  ⚠️ WARN · 2 of 4 · next gap Oct 05`"""
    parts = [view["status"], f"{view['filled']} of {view['total']}"]
    if view["first_gap"]:
        parts.append(f"next gap {view['first_gap'].strftime('%b %d')}")
    else:
        parts.append("no gaps")
    return f"{view['emoji']} {view['label']}  " + " · ".join(parts)


def format_view_rows(view: Dict, max_chars: int = 1024) -> str:
    """The slot list for one stream. An unfilled slot renders as a dash."""
    lines = [
        f"{date.strftime('%a %b %d')}   {item['title'] if item else '—'}"
        for date, item in view["rows"]
    ]
    return "\n".join(lines)[:max_chars] or "No upcoming slots"


def overall_status(views: List[Dict]) -> tuple:
    """
    Worst of any stream, so a healthy blog buffer cannot mask an empty
    newsletter buffer. A post scheduled without an issue needs no special rule
    any more: it simply shows up as a gap in the issues stream.
    """
    worst = max(views, key=lambda v: v["rank"])
    return worst["status"], worst["color"]


def unified_need_by(views: List[Dict]) -> Optional[datetime]:
    """The earliest slot missing anything, across every stream."""
    gaps = [v["first_gap"] for v in views if v["first_gap"]]
    return min(gaps) if gaps else None


def create_discord_message(stream_stats: Dict[str, Dict], ledger: List[Dict],
                           off_cadence: List[Dict], schedule_label: str) -> Dict:
    """Create the Discord webhook payload: one embed covering every stream."""
    views = [stream_view(s, st, ledger) for s, st in stream_stats.items()]
    status, color = overall_status(views)
    need_by = unified_need_by(views)

    if need_by:
        days = (need_by - datetime.now(timezone.utc)).days
        deadline = f"**Need content by {need_by.strftime('%a %b %d')}** · {days} days"
    else:
        deadline = f"**No gaps in the next {len(ledger)} slots**"

    fields = [
        {
            "name": format_view_header(view),
            "value": format_view_rows(view),
            "inline": False,
        }
        for view in views
    ]

    if off_cadence:
        fields.append({
            "name": "⚠️ Off-cadence (not on a publish day)",
            "value": "\n".join(
                f"{i['date_str']}   {i['title']}" for i in off_cadence
            )[:1024],
            "inline": False,
        })

    embed = {
        "title": f"{status} · Content Buffer",
        "description": f"{deadline}\n{schedule_label}",
        "color": color,
        "fields": fields,
        "footer": {"text": "The Agentic Engineer · Buffer Check"},
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    return {"embeds": [embed]}


def send_discord_notification(webhook_url: str, message: Dict) -> bool:
    """Send notification to Discord webhook."""
    try:
        response = requests.post(
            webhook_url,
            json=message,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        print(f"✅ Discord notification sent successfully")
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to send Discord notification: {e}", file=sys.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Check content buffer across streams and notify if low"
    )
    parser.add_argument(
        "--webhook-url",
        help="Discord webhook URL (or set LOW_CONTENT_WEBHOOK env var)"
    )
    parser.add_argument(
        "--stream",
        choices=["posts", "newsletter", "both"],
        default="both",
        help="Which stream(s) to report on (default: both)"
    )
    parser.add_argument(
        "--notify",
        "--force",
        dest="notify",
        action="store_true",
        help="Actually post to Discord. Without it the report only prints, so a "
             "local run never touches the channel."
    )
    args = parser.parse_args()

    # Load configuration
    try:
        config = load_config()
    except Exception as e:
        print(f"❌ Error loading configuration: {e}", file=sys.stderr)
        sys.exit(1)

    # Get webhook URL (optional for dry-run)
    webhook_url = args.webhook_url or os.environ.get("LOW_CONTENT_WEBHOOK")

    # Decide which streams to report on
    if args.stream == "both":
        streams = ["posts"]
        if get_newsletter_config(config)["enabled"]:
            streams.append("newsletter")
    else:
        streams = [args.stream]

    project_root = Path(__file__).parent.parent

    stream_stats = {}
    items_by_stream = {}

    for stream in streams:
        content_dir = project_root / get_stream_config(config, stream)["content_dir"]

        if not content_dir.exists():
            if stream == "posts":
                print(f"❌ Error: Content directory not found: {content_dir}",
                      file=sys.stderr)
                sys.exit(1)
            # A stream that has not been started yet is a warning, not a failure
            print(f"⚠️  {stream} directory not found: {content_dir}")
            items_by_stream[stream] = []
        else:
            items_by_stream[stream] = get_scheduled_posts(content_dir)

        # Only display metadata is needed now; the ledger carries the rest.
        stream_stats[stream] = get_stream_config(config, stream)

    # Both streams share the top-level schedule unless one overrides it, so the
    # ledger is built from the posts cadence.
    pub_config = get_publishing_config(config, streams[0])
    schedule_label = format_schedule_label(pub_config)
    # Two months of lookahead. Derived from the cadence rather than hardcoded so
    # the horizon stays two months if the schedule ever changes: at 1st-and-3rd
    # Monday that is 4 slots, weekly would be ~9.
    rate = get_publishing_rate(config, streams[0])
    slot_count = max(2, round(LOOKAHEAD_MONTHS * rate["posts_per_month"]))
    slots = get_upcoming_slots(pub_config, count=slot_count)
    ledger = build_slot_ledger(slots, items_by_stream)
    off_cadence = find_off_cadence(slots, items_by_stream)

    # Terminal report. Same headline, same labels, same values as the embed:
    # both render from stream_view() and overall_status().
    views = [stream_view(st, stream_stats[st], ledger) for st in streams]
    status, _color = overall_status(views)
    need_by = unified_need_by(views)
    rule = "─" * 54

    print(f"\n{status} · Content Buffer")
    if need_by:
        days = (need_by - datetime.now(timezone.utc)).days
        print(f"Need content by  {need_by.strftime('%a %b %d')}  ·  {days} days")
    else:
        print(f"No gaps in the next {len(ledger)} slots")
    print(schedule_label)
    print(rule)

    for view in views:
        print(format_view_header(view))
        for line in format_view_rows(view).splitlines():
            print(f"   {line}")
        print()

    if off_cadence:
        print("⚠️ Off-cadence (not on a publish day)")
        for item in off_cadence:
            print(f"   {item['date_str']}   {item['title']}")
        print()

    # Posting is opt-in. The webhook lives in .env.local so local runs can send
    # deliberately, but a bare `buffer_check.py` while writing must never put a
    # message in the channel. Only the scheduled workflow passes --notify.
    if not args.notify:
        print("📋 Report only. Pass --notify to post this to Discord.")
        sys.exit(0)

    if not webhook_url:
        print(f"❌ --notify given but no webhook configured "
              f"(set LOW_CONTENT_WEBHOOK or pass --webhook-url)", file=sys.stderr)
        sys.exit(1)

    print("Sending Discord notification...")
    message = create_discord_message(
        stream_stats, ledger, off_cadence, schedule_label
    )
    success = send_discord_notification(webhook_url, message)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
