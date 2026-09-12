#!/usr/bin/env python3
"""
Check the content buffer and report to Discord.

One `/ship` fills one Monday: a post and the issue derived from it. So the
buffer is a ledger of upcoming Mondays, each one shipped, half-shipped, or
empty. Half-shipped (a post with no issue, or the reverse) is called out
because under `/ship` it should not happen.

Usage:
    uv run tools/buffer_check.py                   # print the report
    uv run tools/buffer_check.py --notify          # print and post to Discord
    uv run tools/buffer_check.py --webhook-url URL

Environment Variables:
    LOW_CONTENT_WEBHOOK: Discord webhook URL
"""

import os
import sys
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

# How far ahead the ledger looks.
LOOKAHEAD_MONTHS = 2

project_root = Path(__file__).parent.parent
env_file = project_root / ".env.local"
if env_file.exists():
    load_dotenv(env_file)


def extract_field_from_mdx(mdx_file: Path, field: str) -> Optional[str]:
    """Read one frontmatter field, or None if the file has no usable frontmatter."""
    try:
        content = mdx_file.read_text(encoding='utf-8')
        if not content.startswith('---'):
            return None
        parts = content.split('---', 2)
        if len(parts) < 3:
            return None
        return yaml.safe_load(parts[1]).get(field)
    except Exception:
        return None


def get_scheduled(content_dir: Path, label_field: str) -> List[Dict]:
    """Every entry with a future publish date, labelled by the given field."""
    scheduled = []
    now = datetime.now(timezone.utc)

    for mdx_file in content_dir.glob("*.mdx"):
        date_str = mdx_file.name[:10]
        try:
            entry_date = datetime.strptime(date_str, "%Y-%m-%d").replace(
                hour=11, tzinfo=timezone.utc
            )
        except ValueError:
            continue
        if entry_date > now:
            label = (extract_field_from_mdx(mdx_file, label_field)
                     or extract_field_from_mdx(mdx_file, 'title')
                     or mdx_file.name)
            scheduled.append({
                "filename": mdx_file.name,
                "path": mdx_file,
                "label": label,
                "date": entry_date,
                "date_str": date_str,
            })

    scheduled.sort(key=lambda x: x["date"])
    return scheduled


def get_upcoming_slots(pub_config: Dict, count: int,
                       now: datetime = None) -> List[datetime]:
    """The next N publish days from the schedule."""
    if now is None:
        now = datetime.now(timezone.utc)
    slots = []
    cursor = now.replace(tzinfo=None)
    for _ in range(count):
        cursor = get_next_publish_date(cursor, pub_config)
        slots.append(cursor.replace(tzinfo=timezone.utc))
    return slots


def build_ledger(slots: List[datetime], posts: List[Dict],
                 issues: Optional[List[Dict]]) -> List[Dict]:
    """
    One row per upcoming publish day.

    `state` is what a glance needs: shipped (post and issue), half (one of
    them), or empty. When the newsletter is disabled, a post alone is shipped.
    """
    ledger = []
    for slot in slots:
        slot_str = slot.strftime("%Y-%m-%d")
        post = next((p for p in posts if p["date_str"] == slot_str), None)
        issue = (next((i for i in issues if i["date_str"] == slot_str), None)
                 if issues is not None else None)
        if issues is None:
            state = "shipped" if post else "empty"
        elif post and issue:
            state = "shipped"
        elif post or issue:
            state = "half"
        else:
            state = "empty"
        ledger.append({
            "date": slot, "date_str": slot_str,
            "post": post, "issue": issue, "state": state,
        })
    return ledger


def find_off_cadence(slots: List[datetime], posts: List[Dict],
                     issues: Optional[List[Dict]]) -> List[Dict]:
    """
    Scheduled files that do not land on any upcoming publish day.

    Without this, an entry moved to a Tuesday silently disappears from the
    report and looks like missing content.
    """
    slot_strs = {s.strftime("%Y-%m-%d") for s in slots}
    horizon = max(slots).strftime("%Y-%m-%d") if slots else ""
    off = []
    for kind, items in (("post", posts), ("issue", issues or [])):
        for item in items:
            if item["date_str"] not in slot_strs and item["date_str"] <= horizon:
                off.append({**item, "kind": kind})
    return sorted(off, key=lambda i: i["date_str"])


# Status is rated on how many upcoming Mondays are fully shipped before the
# first one that isn't. Counting slots keeps the rating readable straight off
# the ledger and keeps its meaning if the cadence changes.
LOW_MAX_RUN = 0      # the very next Monday needs a /ship
WARN_MAX_RUN = 2     # a gap inside the next two or three


def rate(ledger: List[Dict]) -> Dict:
    run = 0
    for row in ledger:
        if row["state"] != "shipped":
            break
        run += 1
    if run <= LOW_MAX_RUN:
        status, color = "🚨 LOW", 0xE74C3C
    elif run <= WARN_MAX_RUN:
        status, color = "⚠️ WARN", 0xF1C40F
    else:
        status, color = "✅ GOOD", 0x2ECC71
    next_gap = next((r["date"] for r in ledger if r["state"] != "shipped"), None)
    return {
        "status": status,
        "color": color,
        "shipped": sum(1 for r in ledger if r["state"] == "shipped"),
        "total": len(ledger),
        "next_gap": next_gap,
    }


def format_row(row: Dict, has_issues: bool) -> str:
    """`Mon Sep 14   Post title   ✉ Issue subject`, or a dash for an empty slot."""
    day = row["date"].strftime("%a %b %d")
    if row["state"] == "empty":
        return f"{day}   —"
    post = row["post"]["label"] if row["post"] else "⚠️ no post"
    if not has_issues:
        return f"{day}   {post}"
    issue = f"✉ {row['issue']['label']}" if row["issue"] else "⚠️ no issue"
    return f"{day}   {post}   {issue}"


def half_shipped_fixes(ledger: List[Dict]) -> List[str]:
    """What to run for each half-shipped Monday."""
    fixes = []
    for row in ledger:
        if row["state"] != "half":
            continue
        if row["post"] and not row["issue"]:
            fixes.append(f"{row['date_str']}   post without issue → "
                         f"/create-issue --from-post {row['post']['path']}")
        else:
            fixes.append(f"{row['date_str']}   issue without post → "
                         f"/ship for that Monday, or move the issue")
    return fixes


def create_discord_message(ledger: List[Dict], rating: Dict,
                           off_cadence: List[Dict], schedule_label: str,
                           has_issues: bool) -> Dict:
    """The Discord webhook payload: one embed, one ledger."""
    if rating["next_gap"]:
        days = (rating["next_gap"] - datetime.now(timezone.utc)).days
        deadline = (f"**Next /ship needed for {rating['next_gap'].strftime('%a %b %d')}**"
                    f" · {days} days")
    else:
        deadline = f"**No gaps in the next {rating['total']} Mondays**"

    fields = [{
        "name": f"{rating['shipped']} of {rating['total']} Mondays shipped",
        "value": "\n".join(format_row(r, has_issues) for r in ledger)[:1024]
                 or "No upcoming slots",
        "inline": False,
    }]

    fixes = half_shipped_fixes(ledger)
    if fixes:
        fields.append({
            "name": "⚠️ Half-shipped",
            "value": "\n".join(fixes)[:1024],
            "inline": False,
        })

    if off_cadence:
        fields.append({
            "name": "⚠️ Off-cadence (not on a publish day)",
            "value": "\n".join(
                f"{i['date_str']}   {i['kind']}: {i['label']}" for i in off_cadence
            )[:1024],
            "inline": False,
        })

    embed = {
        "title": f"{rating['status']} · Content Buffer",
        "description": f"{deadline}\n{schedule_label}",
        "color": rating["color"],
        "fields": fields,
        "footer": {"text": "The Agentic Engineer · Buffer Check"},
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    return {"embeds": [embed]}


def send_discord_notification(webhook_url: str, message: Dict) -> bool:
    try:
        response = requests.post(webhook_url, json=message,
                                 headers={"Content-Type": "application/json"})
        response.raise_for_status()
        print("✅ Discord notification sent successfully")
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to send Discord notification: {e}", file=sys.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Check the content buffer and notify if low"
    )
    parser.add_argument(
        "--webhook-url",
        help="Discord webhook URL (or set LOW_CONTENT_WEBHOOK env var)"
    )
    parser.add_argument(
        "--notify", "--force", dest="notify", action="store_true",
        help="Actually post to Discord. Without it the report only prints, so a "
             "local run never touches the channel."
    )
    args = parser.parse_args()

    try:
        config = load_config()
    except Exception as e:
        print(f"❌ Error loading configuration: {e}", file=sys.stderr)
        sys.exit(1)

    webhook_url = args.webhook_url or os.environ.get("LOW_CONTENT_WEBHOOK")

    posts_dir = project_root / get_stream_config(config, "posts")["content_dir"]
    if not posts_dir.exists():
        print(f"❌ Error: Content directory not found: {posts_dir}", file=sys.stderr)
        sys.exit(1)
    posts = get_scheduled(posts_dir, "title")

    issues = None
    if get_newsletter_config(config)["enabled"]:
        issues_dir = project_root / get_stream_config(config, "newsletter")["content_dir"]
        issues = get_scheduled(issues_dir, "subject") if issues_dir.exists() else []
    has_issues = issues is not None

    # Posts and issues share the schedule, so the ledger is built once.
    pub_config = get_publishing_config(config, "posts")
    schedule_label = format_schedule_label(pub_config)
    rate_info = get_publishing_rate(config, "posts")
    slot_count = max(2, round(LOOKAHEAD_MONTHS * rate_info["posts_per_month"]))
    slots = get_upcoming_slots(pub_config, count=slot_count)
    ledger = build_ledger(slots, posts, issues)
    off_cadence = find_off_cadence(slots, posts, issues)
    rating = rate(ledger)

    # Terminal report. Same values as the embed.
    rule = "─" * 54
    print(f"\n{rating['status']} · Content Buffer")
    if rating["next_gap"]:
        days = (rating["next_gap"] - datetime.now(timezone.utc)).days
        print(f"Next /ship needed for  {rating['next_gap'].strftime('%a %b %d')}  ·  {days} days")
    else:
        print(f"No gaps in the next {rating['total']} Mondays")
    print(schedule_label)
    print(rule)
    print(f"{rating['shipped']} of {rating['total']} Mondays shipped")
    for row in ledger:
        print(f"   {format_row(row, has_issues)}")
    print()

    fixes = half_shipped_fixes(ledger)
    if fixes:
        print("⚠️ Half-shipped")
        for line in fixes:
            print(f"   {line}")
        print()

    if off_cadence:
        print("⚠️ Off-cadence (not on a publish day)")
        for item in off_cadence:
            print(f"   {item['date_str']}   {item['kind']}: {item['label']}")
        print()

    # Posting is opt-in. Only the scheduled workflow passes --notify.
    if not args.notify:
        print("📋 Report only. Pass --notify to post this to Discord.")
        sys.exit(0)

    if not webhook_url:
        print("❌ --notify given but no webhook configured "
              "(set LOW_CONTENT_WEBHOOK or pass --webhook-url)", file=sys.stderr)
        sys.exit(1)

    print("Sending Discord notification...")
    message = create_discord_message(ledger, rating, off_cadence,
                                     schedule_label, has_issues)
    sys.exit(0 if send_discord_notification(webhook_url, message) else 1)


if __name__ == "__main__":
    main()
