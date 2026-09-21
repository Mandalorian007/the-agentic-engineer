#!/usr/bin/env python3
"""Post the day's tweet from its surface kit.

This script:
1. Finds the blog post scheduled for today (UTC)
2. Reads surface/<stem>/x.md
3. Appends the blog URL
4. Posts to Twitter via API v2

Posts are scheduled to go live at 6am EST (11am UTC) via ISR.
GitHub Actions runs at 6:30am EST (11:30am UTC) to tweet them.
This gives ISR 30 minutes to rebuild and make posts live.

Usage:
    python tools/post_to_twitter.py                      # Post today's tweet
    python tools/post_to_twitter.py --dry-run            # Preview today's tweet
    python tools/post_to_twitter.py --date 2025-10-20    # Post for specific date
    python tools/post_to_twitter.py --dry-run --date 2025-10-20  # Preview specific date

Exit codes:
- 0: Success (including no post scheduled)
- 1: Error (API failure, missing credentials, post with no x.md, tweet too long)
"""

import argparse
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from lib.config import load_config
from lib.content import get_entry_for_date
from lib.social_validator import TWITTER_TOTAL_MAX, build_url, tweet_length
from lib.surface import kit_dir, read_tweet_text


def get_twitter_client(dry_run: bool = False):
    """Get authenticated Twitter API client.

    Args:
        dry_run: If True, skip credential validation

    Returns:
        tweepy.Client instance or None if dry_run

    Raises:
        SystemExit: If credentials are missing (unless dry_run)
    """
    if dry_run:
        return None

    try:
        import tweepy
    except ImportError:
        print("❌ Error: tweepy package not installed")
        print("Run: uv sync")
        sys.exit(1)

    api_key = os.getenv("TWITTER_API_KEY")
    api_key_secret = os.getenv("TWITTER_API_KEY_SECRET")
    access_token = os.getenv("TWITTER_ACCESS_TOKEN")
    access_token_secret = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")

    if not all([api_key, api_key_secret, access_token, access_token_secret]):
        print("❌ Error: Missing Twitter credentials")
        print("Required environment variables:")
        print("  - TWITTER_API_KEY")
        print("  - TWITTER_API_KEY_SECRET")
        print("  - TWITTER_ACCESS_TOKEN")
        print("  - TWITTER_ACCESS_TOKEN_SECRET")
        sys.exit(1)

    return tweepy.Client(
        consumer_key=api_key,
        consumer_secret=api_key_secret,
        access_token=access_token,
        access_token_secret=access_token_secret,
    )


def build_tweet(stem: str, domain: str) -> str | None:
    """Tweet text plus URL from the post's surface kit, or None if there is no x.md."""
    text = read_tweet_text(stem)
    if not text:
        return None
    return f"{text}\n\n{build_url(stem, domain)}"


def post_tweet(client, tweet_text: str, dry_run: bool = False) -> bool:
    """Post tweet to Twitter.

    Args:
        client: tweepy.Client instance (or None if dry_run)
        tweet_text: Full tweet text
        dry_run: If True, skip actual posting

    Returns:
        True if successful, False otherwise
    """
    if dry_run:
        print(f"🔍 [DRY RUN] Would post tweet:")
        print(f"   {'-' * 60}")
        for line in tweet_text.split('\n'):
            print(f"   {line}")
        print(f"   {'-' * 60}")
        return True

    try:
        response = client.create_tweet(text=tweet_text)
        tweet_id = response.data["id"]
        print(f"✅ Tweet posted successfully (ID: {tweet_id})")
        return True
    except Exception as e:
        print(f"❌ Error posting tweet: {e}")
        return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Post the day's tweet from its surface kit"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview tweets without posting to Twitter",
    )
    parser.add_argument(
        "--date",
        type=str,
        help="Target date in YYYY-MM-DD format (defaults to today UTC)",
    )
    args = parser.parse_args()

    target_date = None
    if args.date:
        try:
            target_date = datetime.strptime(args.date, "%Y-%m-%d").date()
        except ValueError:
            print(f"❌ Error: Invalid date format '{args.date}'. Use YYYY-MM-DD")
            sys.exit(1)

    if args.dry_run:
        print("🔍 DRY RUN MODE - No tweets will be posted\n")

    try:
        config = load_config()
    except Exception as e:
        print(f"❌ Error loading blog config: {e}")
        sys.exit(1)

    domain = config.get("domain", "agentic-engineer.com")
    date_str = target_date.strftime("%Y-%m-%d") if target_date else "today"

    entry = get_entry_for_date(Path(config["content_dir"]), target_date)
    if not entry:
        print(f"ℹ️  No posts scheduled for {date_str}")
        sys.exit(0)

    post_file = entry[0]
    stem = post_file.stem
    print(f"📅 Found 1 post(s) scheduled for {date_str}")

    client = get_twitter_client(dry_run=args.dry_run)

    print(f"\n📄 Processing: {stem}")

    error_count = 0
    posted_count = 0

    tweet_text = build_tweet(stem, domain)
    if not tweet_text:
        # Loud on purpose: a Monday with no tweet is a Monday nobody notices.
        print(f"  ❌ Error: No tweet text at {kit_dir(stem).relative_to(Path.cwd())}/x.md")
        error_count += 1
    else:
        # X charges a flat t.co width for the link rather than its literal
        # characters. lib/social_validator uses the same model at authoring
        # time, so a tweet that passes review cannot fail to send.
        billed_length = tweet_length(tweet_text)
        if billed_length > TWITTER_TOTAL_MAX:
            print(
                f"  ❌ Error: Tweet is {billed_length} chars as X counts it "
                f"(max {TWITTER_TOTAL_MAX}). Skipping."
            )
            error_count += 1
        else:
            if not args.dry_run:
                print(f"  📝 Tweet ({len(tweet_text)} chars):")
                print(f"     {tweet_text[:100]}{'...' if len(tweet_text) > 100 else ''}")

            if post_tweet(client, tweet_text, dry_run=args.dry_run):
                posted_count += 1
            else:
                error_count += 1

    print(f"\n{'='*60}")
    if args.dry_run:
        print(f"🔍 Would post: {posted_count}")
    else:
        print(f"✅ Posted: {posted_count}")
    print(f"❌ Errors: {error_count}")
    print(f"{'='*60}")

    if error_count > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
