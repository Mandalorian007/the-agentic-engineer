#!/usr/bin/env python3
"""
Sync publish status from Blogger API to local frontmatter

This tool fetches the current status of all posts from Blogger and updates
local frontmatter to match the actual published state.

Usage:
    uv run tools/sync_publish_status.py [--post-dir <directory>]

Examples:
    # Sync all posts
    uv run tools/sync_publish_status.py

    # Sync specific post
    uv run tools/sync_publish_status.py --post-dir posts/2025-10-12-my-post/
"""

import sys
import os
import argparse
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.config import load_config, ConfigError
from lib.blogger_client import BloggerClient, BloggerError
from lib.frontmatter import parse_frontmatter, update_frontmatter, FrontmatterError


def find_post_directories(posts_root: Path) -> List[Path]:
    """
    Find all post directories in posts/ folder

    Args:
        posts_root: Path to posts directory

    Returns:
        List of post directory paths
    """
    if not posts_root.exists():
        return []

    post_dirs = []
    for item in posts_root.iterdir():
        if item.is_dir() and (item / 'post.md').exists():
            post_dirs.append(item)

    return sorted(post_dirs)


def sync_post_status(post_dir: Path, blogger_client: BloggerClient, blog_id: str) -> Dict[str, Any]:
    """
    Sync a single post's status from Blogger

    Args:
        post_dir: Path to post directory
        blogger_client: Blogger API client
        blog_id: Blogger blog ID

    Returns:
        Dict with sync results
    """
    result = {
        'post_dir': post_dir.name,
        'synced': False,
        'changes': [],
        'error': None
    }

    try:
        # Read current frontmatter
        post_file = post_dir / 'post.md'
        with open(post_file, 'r', encoding='utf-8') as f:
            markdown_content = f.read()

        frontmatter, body = parse_frontmatter(markdown_content)
        blogger_id = frontmatter.get('blogger_id')

        if not blogger_id:
            result['error'] = 'No blogger_id found (post not published yet)'
            return result

        # Fetch post from Blogger (use AUTHOR view to include drafts and scheduled)
        blogger_post = blogger_client.get_post_by_id(blog_id, blogger_id, view='AUTHOR')

        if not blogger_post:
            result['error'] = f'Post not found on Blogger (ID: {blogger_id})'
            return result

        # Compare and update status
        updates = {}
        changes = []

        # Check status (draft vs published)
        blogger_status = blogger_post.get('status', 'DRAFT')
        local_status = frontmatter.get('status', 'draft')

        if blogger_status == 'LIVE' and local_status == 'draft':
            updates['status'] = 'published'
            changes.append('status: draft → published')
        elif blogger_status == 'DRAFT' and local_status == 'published':
            updates['status'] = 'draft'
            changes.append('status: published → draft')

        # Check published date
        if 'published' in blogger_post:
            blogger_published = blogger_post['published']
            local_date = frontmatter.get('date')

            if blogger_published != local_date:
                updates['date'] = blogger_published
                changes.append(f'date: {local_date} → {blogger_published}')

        # Check updated timestamp
        if 'updated' in blogger_post:
            blogger_updated = blogger_post['updated']
            local_updated = frontmatter.get('updated')

            if blogger_updated != local_updated:
                updates['updated'] = blogger_updated
                changes.append(f'updated timestamp refreshed')

        # Apply updates if any
        if updates:
            updated_markdown = update_frontmatter(markdown_content, updates)

            # Write atomically using temp file
            temp_fd, temp_path = tempfile.mkstemp(dir=post_dir, suffix='.md')
            try:
                with os.fdopen(temp_fd, 'w', encoding='utf-8') as f:
                    f.write(updated_markdown)
                shutil.move(temp_path, post_file)
                result['synced'] = True
                result['changes'] = changes
            except Exception as e:
                if Path(temp_path).exists():
                    Path(temp_path).unlink()
                raise
        else:
            result['synced'] = True
            result['changes'] = ['No changes needed - already in sync']

    except (FrontmatterError, BloggerError) as e:
        result['error'] = str(e)
    except Exception as e:
        result['error'] = f'Unexpected error: {e}'

    return result


def sync_all_posts(posts_root: Path, blogger_client: BloggerClient, blog_id: str) -> None:
    """
    Sync all posts in the posts directory

    Args:
        posts_root: Path to posts directory
        blogger_client: Blogger API client
        blog_id: Blogger blog ID
    """
    print("="*60)
    print("🔄 SYNCING PUBLISH STATUS FROM BLOGGER")
    print("="*60)

    post_dirs = find_post_directories(posts_root)

    if not post_dirs:
        print("\n⚠️  No posts found in posts/ directory")
        return

    print(f"\n📁 Found {len(post_dirs)} post(s) to check\n")

    synced_count = 0
    changed_count = 0
    error_count = 0

    for post_dir in post_dirs:
        print(f"🔍 {post_dir.name}")
        result = sync_post_status(post_dir, blogger_client, blog_id)

        if result['error']:
            print(f"   ⚠️  {result['error']}")
            error_count += 1
        elif result['synced']:
            synced_count += 1
            if result['changes'] and result['changes'][0] != 'No changes needed - already in sync':
                changed_count += 1
                for change in result['changes']:
                    print(f"   ✅ {change}")
            else:
                print(f"   ✓ Already in sync")
        print()

    # Summary
    print("="*60)
    print("📊 SYNC SUMMARY")
    print("="*60)
    print(f"Total posts:     {len(post_dirs)}")
    print(f"Synced:          {synced_count}")
    print(f"Updated:         {changed_count}")
    print(f"Errors/Skipped:  {error_count}")
    print("="*60)


def main():
    parser = argparse.ArgumentParser(
        description='Sync publish status from Blogger to local frontmatter'
    )
    parser.add_argument(
        '--post-dir',
        type=str,
        help='Sync specific post directory (default: sync all posts)'
    )

    args = parser.parse_args()

    try:
        # Load configuration
        config = load_config()
        blogger_client = BloggerClient(config['blogger_credentials'])
        blog_id = config['blogger_blog_id']

        if args.post_dir:
            # Sync single post
            post_dir = Path(args.post_dir).resolve()
            if not post_dir.exists():
                print(f"❌ Post directory not found: {post_dir}", file=sys.stderr)
                sys.exit(1)

            result = sync_post_status(post_dir, blogger_client, blog_id)

            if result['error']:
                print(f"❌ Error: {result['error']}", file=sys.stderr)
                sys.exit(1)
            else:
                print(f"✅ Synced: {post_dir.name}")
                for change in result['changes']:
                    print(f"   {change}")
        else:
            # Sync all posts
            posts_root = Path.cwd() / 'posts'
            sync_all_posts(posts_root, blogger_client, blog_id)

    except ConfigError as e:
        print(f"\n❌ Configuration error: {e}\n", file=sys.stderr)
        sys.exit(1)
    except BloggerError as e:
        print(f"\n❌ Blogger API error: {e}\n", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}\n", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
