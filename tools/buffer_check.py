#!/usr/bin/env python3
"""
Check content buffer and send Discord notification if low.

Usage:
    uv run tools/buffer_check.py [--webhook-url URL] [--threshold-weeks N]

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
from lib.config import load_config, get_posts_per_week

# Auto-load .env.local if it exists (for local testing)
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


def calculate_buffer_stats(scheduled_posts: List[Dict], posts_per_week: int) -> Dict[str, any]:
    """
    Calculate buffer statistics.

    Args:
        scheduled_posts: List of scheduled post dicts
        posts_per_week: Number of posts published per week (from config)

    Returns:
        Dict with buffer statistics
    """
    now = datetime.now(timezone.utc)

    if not scheduled_posts:
        return {
            "weeks_of_buffer": 0,
            "posts_scheduled": 0,
            "posts_per_week": posts_per_week,
            "last_post_date": None,
            "content_runs_out": now,
            "need_content_by": now
        }

    last_post = scheduled_posts[-1]
    last_post_date = last_post["date"]

    # Calculate weeks of buffer based on actual time span
    # This is more accurate than just dividing posts by posts_per_week
    posts_scheduled = len(scheduled_posts)
    time_until_last_post = last_post_date - now
    days_of_buffer = time_until_last_post.days
    weeks_of_buffer = days_of_buffer / 7.0

    # Calculate when content runs out (the last post date)
    content_runs_out = last_post_date

    # Need new content by the last post date (to maintain buffer)
    need_content_by = content_runs_out

    return {
        "weeks_of_buffer": weeks_of_buffer,
        "posts_scheduled": posts_scheduled,
        "posts_per_week": posts_per_week,
        "last_post_date": last_post_date,
        "content_runs_out": content_runs_out,
        "need_content_by": need_content_by
    }


def create_discord_message(stats: Dict[str, any], scheduled_posts: List[Dict]) -> Dict:
    """Create Discord webhook payload with embed."""
    weeks = stats["weeks_of_buffer"]
    posts_count = stats["posts_scheduled"]
    posts_per_week = stats["posts_per_week"]

    # Determine color and urgency with three levels
    if weeks < 2:
        color = 0xFF0000  # Red - urgent/low
        urgency = "🚨 LOW"
    elif weeks < 4:
        color = 0xFFA500  # Orange - moderate
        urgency = "⚠️ MODERATE"
    else:
        color = 0x00FF00  # Green - good
        urgency = "✅ GOOD"

    # Format dates
    if stats["last_post_date"]:
        runs_out_str = stats["content_runs_out"].strftime("%A, %B %d, %Y")
        need_by_str = stats["need_content_by"].strftime("%A, %B %d, %Y")
    else:
        runs_out_str = "No posts scheduled!"
        need_by_str = "ASAP"

    # Build post list
    post_list = []
    for post in scheduled_posts:
        post_list.append(f"• **{post['date_str']}** - {post['title']}")
    post_list_str = "\n".join(post_list) if post_list else "No posts scheduled"

    # Create embed
    embed = {
        "title": f"{urgency} - Content Buffer Check",
        "description": f"You have **{weeks:.1f} weeks** of scheduled content ({posts_count} posts @ {posts_per_week}/week)",
        "color": color,
        "fields": [
            {
                "name": "📅 Last Scheduled Post",
                "value": runs_out_str,
                "inline": True
            },
            {
                "name": "✍️ Need New Content By",
                "value": need_by_str,
                "inline": True
            },
            {
                "name": "📝 Scheduled Posts",
                "value": post_list_str[:1024],  # Discord field limit
                "inline": False
            }
        ],
        "footer": {
            "text": "The Agentic Engineer - Buffer Check"
        },
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    return {
        "embeds": [embed]
    }


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
    parser = argparse.ArgumentParser(description="Check content buffer and notify if low")
    parser.add_argument(
        "--webhook-url",
        help="Discord webhook URL (or set LOW_CONTENT_WEBHOOK env var)"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Send notification (default behavior for weekly updates)"
    )
    args = parser.parse_args()

    # Load configuration to get posts per week
    try:
        config = load_config()
        posts_per_week = get_posts_per_week(config)
    except Exception as e:
        print(f"❌ Error loading configuration: {e}", file=sys.stderr)
        sys.exit(1)

    # Get webhook URL (optional for dry-run)
    webhook_url = args.webhook_url or os.environ.get("LOW_CONTENT_WEBHOOK")

    # Find content directory
    project_root = Path(__file__).parent.parent
    content_dir = project_root / "website" / "content" / "posts"

    if not content_dir.exists():
        print(f"❌ Error: Content directory not found: {content_dir}", file=sys.stderr)
        sys.exit(1)

    # Get scheduled posts
    scheduled_posts = get_scheduled_posts(content_dir)

    # Calculate stats
    stats = calculate_buffer_stats(scheduled_posts, posts_per_week)

    # Print summary
    print(f"\n📊 Content Buffer Status")
    print(f"{'='*50}")
    print(f"Posts scheduled: {stats['posts_scheduled']}")
    print(f"Posts per week: {posts_per_week}")
    print(f"Weeks of buffer: {stats['weeks_of_buffer']:.1f}")

    if stats['last_post_date']:
        print(f"Last post date: {stats['last_post_date'].strftime('%Y-%m-%d')}")
        print(f"Content runs out: {stats['content_runs_out'].strftime('%A, %B %d, %Y')}")
        print(f"Need content by: {stats['need_content_by'].strftime('%A, %B %d, %Y')}")
    else:
        print("⚠️ No posts scheduled!")

    # Send notification
    if webhook_url:
        print(f"\nSending Discord notification...")
        message = create_discord_message(stats, scheduled_posts)
        success = send_discord_notification(webhook_url, message)
        sys.exit(0 if success else 1)
    else:
        print(f"\n⚠️ No webhook URL configured (set LOW_CONTENT_WEBHOOK to enable notifications)")
        sys.exit(0)


if __name__ == "__main__":
    main()
