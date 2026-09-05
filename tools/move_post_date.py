#!/usr/bin/env python3
"""
Move a blog post or newsletter issue to a new date.

This script handles all necessary updates:
- Renames MDX file with new date
- Updates frontmatter date field
- Renames image directory
- Updates all image references in MDX content

Usage:
    # Preview changes without making them
    uv run tools/move_post_date.py 2025-10-27 2025-10-23 --dry-run

    # Actually perform the move
    uv run tools/move_post_date.py 2025-10-27 2025-10-23

    # Move to a specific date/time
    uv run tools/move_post_date.py 2025-10-27 "2025-10-23T10:00:00Z"

    # Move a newsletter issue (also shifts archive_date by the same delta)
    uv run tools/move_post_date.py 2026-09-07 2026-09-21 --stream newsletter
"""

import sys
import re
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple

# Add parent directory to path to import lib modules
sys.path.insert(0, str(Path(__file__).parent.parent))
from lib.config import load_config, get_stream_config
from lib.frontmatter import parse_frontmatter, serialize_frontmatter, FrontmatterError


class MoveError(Exception):
    """Error during post move operation"""
    pass


def parse_date_input(date_str: str) -> Tuple[str, str]:
    """
    Parse date input and return (date_prefix, frontmatter_date).

    Args:
        date_str: Either "YYYY-MM-DD" or "YYYY-MM-DDTHH:MM:SSZ"

    Returns:
        Tuple of (date_prefix for filename, ISO datetime for frontmatter)
    """
    # If it's just a date (YYYY-MM-DD), add default time
    if re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
        date_prefix = date_str
        frontmatter_date = f"{date_str}T10:00:00Z"
    # If it's a full ISO datetime
    elif re.match(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z?$', date_str):
        date_prefix = date_str[:10]  # Extract YYYY-MM-DD part
        frontmatter_date = date_str if date_str.endswith('Z') else f"{date_str}Z"
    else:
        raise MoveError(
            f"Invalid date format: {date_str}\n"
            f"Use either:\n"
            f"  - YYYY-MM-DD (e.g., 2025-10-23)\n"
            f"  - YYYY-MM-DDTHH:MM:SSZ (e.g., 2025-10-23T10:00:00Z)"
        )

    # Validate the date is actually valid
    try:
        datetime.fromisoformat(frontmatter_date.replace('Z', '+00:00'))
    except ValueError:
        raise MoveError(f"Invalid date: {date_str}")

    return date_prefix, frontmatter_date


def find_post_by_date(posts_dir: Path, date_prefix: str) -> Optional[Path]:
    """
    Find a post file that starts with the given date prefix.

    Args:
        posts_dir: Directory containing MDX posts
        date_prefix: Date prefix to search for (YYYY-MM-DD)

    Returns:
        Path to the post file, or None if not found
    """
    pattern = f"{date_prefix}-*.mdx"
    matches = list(posts_dir.glob(pattern))

    if not matches:
        return None
    if len(matches) > 1:
        raise MoveError(
            f"Multiple posts found for date {date_prefix}:\n" +
            "\n".join(f"  - {m.name}" for m in matches)
        )

    return matches[0]


def extract_slug_from_filename(filename: str) -> str:
    """
    Extract slug from post filename (YYYY-MM-DD-slug.mdx).

    Args:
        filename: Post filename

    Returns:
        The slug portion of the filename
    """
    # Remove .mdx extension
    name = filename.replace('.mdx', '')
    # Split on first three dashes (YYYY-MM-DD)
    parts = name.split('-', 3)
    if len(parts) < 4:
        raise MoveError(f"Invalid filename format: {filename}")
    return parts[3]


def update_image_paths_in_content(content: str, old_date: str, new_date: str) -> str:
    """
    Update all image paths in MDX content to reference new date directory.

    Args:
        content: MDX content
        old_date: Old date prefix (YYYY-MM-DD)
        new_date: New date prefix (YYYY-MM-DD)

    Returns:
        Updated content with new image paths
    """
    # Pattern: ../../public/blog/YYYY-MM-DD-slug/image.webp
    # This regex handles various slug formats
    pattern = re.compile(
        r'\(\.\.\/\.\.\/public\/blog\/' + re.escape(old_date) + r'-([^/]+)/([^)]+)\)'
    )

    def replace_path(match):
        slug = match.group(1)
        image_name = match.group(2)
        return f'(../../public/blog/{new_date}-{slug}/{image_name})'

    updated = pattern.sub(replace_path, content)

    # Count replacements to report to user
    count = len(pattern.findall(content))

    return updated, count


def move_post(
    old_date: str,
    new_date: str,
    dry_run: bool = False,
    verbose: bool = True,
    stream: str = 'posts'
) -> None:
    """
    Move a blog post or newsletter issue from one date to another.

    Args:
        old_date: Current date (YYYY-MM-DD or ISO datetime)
        new_date: New date (YYYY-MM-DD or ISO datetime)
        dry_run: If True, only show what would be done
        verbose: If True, print detailed progress
        stream: 'posts' or 'newsletter'
    """
    # Parse dates
    old_date_prefix, _ = parse_date_input(old_date)
    new_date_prefix, new_frontmatter_date = parse_date_input(new_date)

    # Load config for paths
    config = load_config()
    stream_cfg = get_stream_config(config, stream)
    content_dir = stream_cfg['content_dir']
    images_dir = stream_cfg['images_dir']   # None for streams without images
    noun = stream_cfg['noun']

    # The other stream shares these dates by design; warn if the move breaks a pair.
    other = 'newsletter' if stream == 'posts' else 'posts'
    other_cfg = get_stream_config(config, other)

    if not content_dir.exists():
        raise MoveError(f"Content directory not found: {content_dir}")

    # Find the post file
    old_post_path = find_post_by_date(content_dir, old_date_prefix)
    if not old_post_path:
        raise MoveError(
            f"No {noun} found for date {old_date_prefix}\n"
            f"Searched in: {content_dir}"
        )

    if verbose:
        print(f"📄 Found {noun}: {old_post_path.name}")

    # Extract slug
    slug = extract_slug_from_filename(old_post_path.name)
    new_post_filename = f"{new_date_prefix}-{slug}.mdx"
    new_post_path = content_dir / new_post_filename

    # Check if target already exists
    if new_post_path.exists() and new_post_path != old_post_path:
        raise MoveError(
            f"Target post already exists: {new_post_path.name}\n"
            f"Cannot move to a date that already has a post."
        )

    # Read and parse the post
    try:
        old_content = old_post_path.read_text(encoding='utf-8')
        frontmatter, body = parse_frontmatter(old_content)
    except (OSError, FrontmatterError) as e:
        raise MoveError(f"Failed to read post: {e}")

    # Update frontmatter date
    old_fm_date = frontmatter.get('date', 'unknown')
    frontmatter['date'] = new_frontmatter_date

    # An issue's archive_date is relative to its send date, so it has to travel
    # the same distance. Leaving it put would publish the archive page early.
    old_archive_date = frontmatter.get('archive_date')
    new_archive_date = None
    if old_archive_date:
        delta = (datetime.strptime(new_date_prefix, '%Y-%m-%d')
                 - datetime.strptime(old_date_prefix, '%Y-%m-%d'))
        parsed = datetime.strptime(str(old_archive_date)[:10], '%Y-%m-%d')
        shifted = parsed + delta
        new_archive_date = (shifted.strftime('%Y-%m-%d')
                            + str(old_archive_date)[10:])
        frontmatter['archive_date'] = new_archive_date

    # Update image paths in body (streams without images have nothing to rewrite)
    if images_dir is not None:
        updated_body, image_count = update_image_paths_in_content(
            body, old_date_prefix, new_date_prefix
        )
    else:
        updated_body, image_count = body, 0

    # Serialize back to markdown
    new_content = serialize_frontmatter(frontmatter, updated_body)

    # Determine image directories
    old_image_dir = images_dir / f"{old_date_prefix}-{slug}" if images_dir else None
    new_image_dir = images_dir / f"{new_date_prefix}-{slug}" if images_dir else None

    # Print plan
    if verbose:
        print("\n" + "=" * 60)
        print("📋 MOVE PLAN")
        print("=" * 60)
        print(f"\n1. Rename MDX file:")
        print(f"   {old_post_path.name}")
        print(f"   → {new_post_filename}")

        print(f"\n2. Update frontmatter date:")
        print(f"   {old_fm_date}")
        print(f"   → {new_frontmatter_date}")

        if new_archive_date:
            print(f"\n3. Update archive_date:")
            print(f"   {old_archive_date}")
            print(f"   → {new_archive_date}")

        if image_count > 0:
            print(f"\n3. Update {image_count} image reference(s) in content")

        if old_image_dir is None:
            print(f"\n4. No image directory for the {stream} stream")
        elif old_image_dir.exists():
            print(f"\n4. Rename image directory:")
            print(f"   {old_image_dir.name}/")
            print(f"   → {new_image_dir.name}/")
        else:
            print(f"\n4. No image directory found at:")
            print(f"   {old_image_dir}")

        print("\n" + "=" * 60)

    # Execute or dry-run
    if dry_run:
        print("\n🔍 DRY RUN MODE - No changes made")
        print("   Run without --dry-run to apply changes")
        return

    # Perform the move
    try:
        # 1. Write updated content to new file
        if verbose:
            print("\n✏️  Writing updated content...")
        new_post_path.write_text(new_content, encoding='utf-8')

        # 2. Delete old file if different
        if old_post_path != new_post_path:
            if verbose:
                print("🗑️  Removing old post file...")
            old_post_path.unlink()

        # 3. Move image directory if this stream has one
        if old_image_dir and old_image_dir.exists() and old_image_dir != new_image_dir:
            if verbose:
                print("📁 Moving image directory...")

            # Check if target exists
            if new_image_dir.exists():
                raise MoveError(
                    f"Target image directory already exists: {new_image_dir}\n"
                    f"Please manually resolve this conflict."
                )

            shutil.move(str(old_image_dir), str(new_image_dir))

        print("\n✅ Move completed successfully!")
        print(f"   {noun.capitalize()} moved from {old_date_prefix} to {new_date_prefix}")

        if find_post_by_date(other_cfg['content_dir'], old_date_prefix):
            print(f"\n⚠️  A {other_cfg['noun']} is still dated {old_date_prefix}. "
                  f"That pairing is now broken.")

    except Exception as e:
        # Try to rollback if possible
        print(f"\n❌ Error during move: {e}", file=sys.stderr)
        print("⚠️  Manual cleanup may be required", file=sys.stderr)
        raise MoveError(f"Move failed: {e}")


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description='Move a blog post or newsletter issue to a new date',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Preview the move (dry run)
  %(prog)s 2025-10-27 2025-10-23 --dry-run

  # Move the post
  %(prog)s 2025-10-27 2025-10-23

  # Move with specific time
  %(prog)s 2025-10-27 "2025-10-23T14:30:00Z"

  # Move a newsletter issue
  %(prog)s 2026-09-07 2026-09-21 --stream newsletter
        """
    )

    parser.add_argument(
        'old_date',
        help='Current date of the post (YYYY-MM-DD or ISO datetime)'
    )
    parser.add_argument(
        'new_date',
        help='New date for the post (YYYY-MM-DD or ISO datetime)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be done without making changes'
    )
    parser.add_argument(
        '-q', '--quiet',
        action='store_true',
        help='Minimal output (only errors)'
    )
    parser.add_argument(
        '--stream',
        choices=['posts', 'newsletter'],
        default='posts',
        help='Which content stream the entry belongs to (default: posts)'
    )

    args = parser.parse_args()

    try:
        move_post(
            old_date=args.old_date,
            new_date=args.new_date,
            dry_run=args.dry_run,
            verbose=not args.quiet,
            stream=args.stream
        )
        return 0

    except MoveError as e:
        print(f"\n❌ {e}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\n\n⚠️  Operation cancelled by user", file=sys.stderr)
        return 130
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
