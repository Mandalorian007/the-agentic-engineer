#!/usr/bin/env python3
"""
Drop the day's surface kit into Discord.

Runs from the publish-day workflow right after the tweet goes out. Finds the
post scheduled for today, reads `surface/<date>-<slug>.md`, and posts it to
the Discord webhook so the manual part of distribution (LinkedIn, Hacker
News, Reddit) is a copy-paste from a phone.

Usage:
    uv run tools/notify_surface.py                       # today's post
    uv run tools/notify_surface.py --date 2026-10-12     # a specific date
    uv run tools/notify_surface.py --dry-run             # print, don't post

Environment Variables:
    LOW_CONTENT_WEBHOOK: Discord webhook URL (same channel as the buffer check)

Exit codes:
    0  posted, or nothing scheduled today, or no kit for today's post
    1  webhook missing or Discord rejected the message
"""

import argparse
import os
import sys
from datetime import datetime, timezone, date as date_type
from pathlib import Path

import requests
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent.parent))
from lib.config import load_config
from lib.content import get_entry_for_date

project_root = Path(__file__).parent.parent
env_file = project_root / ".env.local"
if env_file.exists():
    load_dotenv(env_file)

SURFACE_DIR = project_root / "surface"
# Discord caps a message at 2000 characters. Leave room for the code fence.
CHUNK = 1900


def chunks(text: str, size: int = CHUNK):
    """Split on line boundaries so a paste never lands mid-sentence."""
    buf = ""
    for line in text.splitlines(keepends=True):
        if len(buf) + len(line) > size and buf:
            yield buf
            buf = ""
        buf += line
    if buf:
        yield buf


def main() -> int:
    parser = argparse.ArgumentParser(description="Post today's surface kit to Discord")
    parser.add_argument("--date", help="Target date YYYY-MM-DD (default: today UTC)")
    parser.add_argument("--dry-run", action="store_true", help="Print instead of posting")
    args = parser.parse_args()

    target = (
        date_type.fromisoformat(args.date) if args.date
        else datetime.now(timezone.utc).date()
    )

    config = load_config()
    entry = get_entry_for_date(Path(config["content_dir"]), target)
    if not entry:
        print(f"ℹ️  No post scheduled for {target}; nothing to surface.")
        return 0

    post_path = entry[0]
    kit = SURFACE_DIR / f"{post_path.stem}.md"
    if not kit.exists():
        print(f"⚠️  {post_path.name} publishes today but surface/{kit.name} does not exist.")
        print("   Run /ship next time, or write the kit by hand before the next publish day.")
        return 0

    text = kit.read_text(encoding="utf-8")
    header = f"📣 **Surface kit for today's post** (`{kit.name}`)\n"
    messages = [header] + [f"```markdown\n{c}```" for c in chunks(text)]

    if args.dry_run:
        print("📋 Dry run. Would post to Discord:\n")
        print(header)
        print(text)
        return 0

    webhook = os.environ.get("LOW_CONTENT_WEBHOOK")
    if not webhook:
        print("❌ LOW_CONTENT_WEBHOOK is not set", file=sys.stderr)
        return 1

    for msg in messages:
        try:
            resp = requests.post(webhook, json={"content": msg}, timeout=15)
            resp.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"❌ Discord rejected the surface kit: {e}", file=sys.stderr)
            return 1

    print(f"✅ Surface kit posted to Discord in {len(messages)} message(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
