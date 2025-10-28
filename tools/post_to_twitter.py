#!/usr/bin/env python3
"""Post Twitter content from blog post frontmatter.

This script:
1. Finds blog posts scheduled for today (UTC)
2. Reads social.twitter.text from frontmatter
3. Appends blog URL
4. Posts to Twitter via API v2

Posts are scheduled to go live at 6am EST (11am UTC) via ISR.
GitHub Actions runs at 6:30am EST (11:30am UTC) to tweet them.
This gives ISR 30 minutes to rebuild and make posts live.

Usage:
    python tools/post_to_twitter.py                      # Post tweets for today
    python tools/post_to_twitter.py --dry-run            # Preview today's tweets
    python tools/post_to_twitter.py --date 2025-10-20    # Post for specific date
    python tools/post_to_twitter.py --dry-run --date 2025-10-20  # Preview specific date

Exit codes:
- 0: Success (including no posts to tweet)
- 1: Error (API failure, missing credentials, etc.)
"""

import argparse
import os
import sys
from datetime import datetime, timezone, date as date_type
from pathlib import Path

from lib.config import load_config
from lib.frontmatter import parse_frontmatter


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

    # Load credentials from environment
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


def get_posts_for_today(config: dict, target_date: date_type | None = None) -> list[tuple[Path, dict]]:
    """Get all blog posts scheduled for today (UTC).

    Posts are scheduled to go live at 6am EST (11am UTC).
    This script runs at 6:30am EST to tweet them after ISR has rebuilt.

    Args:
        config: Blog configuration
        target_date: Date to check for posts (defaults to today UTC)

    Returns:
        List of (file_path, frontmatter) tuples
    """
    content_dir = Path(config["content_dir"])
    if target_date is None:
        target_date = datetime.now(timezone.utc).date()

    posts_for_today = []

    for mdx_file in content_dir.glob("*.mdx"):
        try:
            # Read file content and parse frontmatter
            content = mdx_file.read_text(encoding="utf-8")
            frontmatter, _ = parse_frontmatter(content)

            # Parse post date
            date_str = frontmatter.get("date")
            if not date_str:
                continue

            post_date = datetime.fromisoformat(date_str.replace("Z", "+00:00")).date()

            # Check if post is scheduled for today
            if post_date == target_date:
                posts_for_today.append((mdx_file, frontmatter))

        except Exception as e:
            print(f"⚠️  Warning: Failed to parse {mdx_file.name}: {e}")
            continue

    return posts_for_today


def build_tweet(frontmatter: dict, slug: str, domain: str) -> str | None:
    """Build tweet text from frontmatter.

    Args:
        frontmatter: Parsed frontmatter
        slug: Post slug (YYYY-MM-DD-title)
        domain: Blog domain

    Returns:
        Tweet text or None if no Twitter content
    """
    # Check if social.twitter.text exists
    social = frontmatter.get("social", {})
    twitter = social.get("twitter", {})
    text = twitter.get("text", "").strip()

    if not text:
        return None

    # Build full URL
    url = f"https://{domain}/blog/{slug}"

    # Combine text and URL
    return f"{text}\n\n{url}"


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
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description="Post Twitter content from blog post frontmatter"
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

    # Parse target date
    target_date = None
    if args.date:
        try:
            target_date = datetime.strptime(args.date, "%Y-%m-%d").date()
        except ValueError:
            print(f"❌ Error: Invalid date format '{args.date}'. Use YYYY-MM-DD")
            sys.exit(1)

    if args.dry_run:
        print("🔍 DRY RUN MODE - No tweets will be posted\n")

    # Load blog configuration
    try:
        config = load_config()
    except Exception as e:
        print(f"❌ Error loading blog config: {e}")
        sys.exit(1)

    domain = config.get("domain", "agentic-engineer.com")

    # Get posts scheduled for today
    posts_today = get_posts_for_today(config, target_date)

    if not posts_today:
        date_str = target_date.strftime("%Y-%m-%d") if target_date else "today"
        print(f"ℹ️  No posts scheduled for {date_str}")
        sys.exit(0)

    date_str = target_date.strftime("%Y-%m-%d") if target_date else "today"
    print(f"📅 Found {len(posts_today)} post(s) scheduled for {date_str}")

    # Get Twitter client (skip if dry run)
    client = get_twitter_client(dry_run=args.dry_run)

    # Process each post
    posted_count = 0
    error_count = 0

    for post_file, post_frontmatter in posts_today:
        # Extract slug from filename (remove .mdx extension)
        slug = post_file.stem

        print(f"\n📄 Processing: {slug}")

        # Build tweet
        tweet_text = build_tweet(post_frontmatter, slug, domain)

        if not tweet_text:
            print("  ⚠️  No Twitter content found in frontmatter")
            continue

        # Validate length (280 char limit)
        if len(tweet_text) > 280:
            print(
                f"  ❌ Error: Tweet is {len(tweet_text)} chars (max 280). Skipping."
            )
            error_count += 1
            continue

        if not args.dry_run:
            print(f"  📝 Tweet ({len(tweet_text)} chars):")
            print(f"     {tweet_text[:100]}{'...' if len(tweet_text) > 100 else ''}")

        # Post tweet (or preview if dry run)
        if post_tweet(client, tweet_text, dry_run=args.dry_run):
            posted_count += 1
        else:
            error_count += 1

    # Summary
    print(f"\n{'='*60}")
    if args.dry_run:
        print(f"🔍 Would post: {posted_count}")
    else:
        print(f"✅ Posted: {posted_count}")
    print(f"❌ Errors: {error_count}")
    print(f"{'='*60}")

    # Exit with error if any posts failed
    if error_count > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
