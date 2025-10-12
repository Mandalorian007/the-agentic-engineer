#!/usr/bin/env python3
"""
Publish command: Upload images and create/update blog post on Blogger

Usage:
    uv run tools/publish.py <post-directory>

Example:
    uv run tools/publish.py posts/2025-10-12-my-first-post/
"""

import sys
import os
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
from lib.config import load_config, ConfigError
from lib.validator import (
    validate_post_directory,
    validate_post_content,
    extract_image_references,
    derive_blogger_path,
    ValidationError
)
from lib.frontmatter import parse_frontmatter, update_frontmatter, FrontmatterError
from lib.markdown_converter import create_converter
from lib.image_processor import compute_image_hash
from lib.blogger_client import BloggerClient, BloggerError
from lib.cloudinary_uploader import CloudinaryUploader, CloudinaryError


def publish_post(post_dir_str: str) -> int:
    """
    Publish a blog post to Blogger

    Args:
        post_dir_str: Path to post directory

    Returns:
        Exit code (0 = success, 1 = error)
    """
    try:
        print("="*60)
        print("📤 PUBLISHING TO BLOGGER")
        print("="*60)

        # Step 1: Load configuration
        print("\n📋 Loading configuration...")
        config = load_config()

        # Step 2: Validate post
        post_dir = Path(post_dir_str).resolve()
        print(f"🔍 Validating post: {post_dir.name}")
        validate_post_directory(post_dir)

        # Read post content
        post_file = post_dir / 'post.md'
        with open(post_file, 'r', encoding='utf-8') as f:
            markdown_content = f.read()

        frontmatter, body = validate_post_content(markdown_content, post_dir)

        # Step 3: Detect post status (CREATE or UPDATE)
        print("\n🔎 Checking post status...")
        blogger_client = BloggerClient(config['blogger_credentials'])
        blog_id = config['blogger_blog_id']
        blogger_path = derive_blogger_path(post_dir)

        cached_blogger_id = frontmatter.get('blogger_id')
        post_status, post_id = blogger_client.detect_post_status(
            blog_id,
            blogger_path,
            cached_blogger_id
        )

        print(f"   Status: {post_status}")
        if post_status == 'UPDATE':
            print(f"   Existing post ID: {post_id}")
            print(f"   URL path: {blogger_path}")

        # Step 4: Process images
        print("\n🖼️  Processing images...")
        image_refs = extract_image_references(body)

        if image_refs:
            print(f"   Found {len(image_refs)} image(s)")

            # Compute hashes
            image_hashes = {}
            for img_ref in image_refs:
                if img_ref.startswith('./'):
                    img_ref = img_ref[2:]
                img_path = post_dir / img_ref
                image_hashes[img_ref] = compute_image_hash(img_path)

            # Upload images
            cloudinary_uploader = CloudinaryUploader(config['cloudinary'])
            post_slug = post_dir.name.split('-', 3)[-1]  # Extract slug from directory name

            cached_images = frontmatter.get('images', {})
            image_mappings = cloudinary_uploader.upload_post_images(
                post_dir=post_dir,
                image_refs=image_refs,
                post_slug=post_slug,
                cached_images=cached_images,
                image_hashes=image_hashes
            )

            # Replace image URLs in markdown
            body_with_cdn_urls = cloudinary_uploader.replace_image_urls(body, image_mappings)
        else:
            print("   No images to process")
            body_with_cdn_urls = body
            image_mappings = {}

        # Step 5: Convert markdown to HTML
        print("\n📄 Converting markdown to HTML...")
        converter = create_converter(config)
        html_content = converter.convert(body_with_cdn_urls)

        # Step 6: Publish to Blogger
        print(f"\n📡 {post_status}ing post on Blogger...")

        title = frontmatter['title']
        labels = frontmatter.get('tags', [])
        is_draft = frontmatter.get('status', 'draft') == 'draft'

        # Check if post should be scheduled
        post_date = frontmatter.get('date')
        published_date = None
        is_scheduled = False

        if post_date:
            # post_date can be either a datetime object (parsed by YAML) or a string
            if isinstance(post_date, str):
                from dateutil import parser as date_parser
                post_date = date_parser.isoparse(post_date)

            now = datetime.now(post_date.tzinfo) if post_date.tzinfo else datetime.utcnow()

            if post_date > now:
                # Future date - schedule the post
                published_date = post_date.isoformat().replace('+00:00', 'Z')
                is_scheduled = True
                print(f"   📅 Scheduling post for: {published_date}")

        if post_status == 'CREATE':
            result = blogger_client.create_post(
                blog_id=blog_id,
                title=title,
                content=html_content,
                labels=labels,
                is_draft=is_draft,
                published=published_date
            )
            post_id = result['id']
            post_url = result['url']
            if is_scheduled:
                print(f"   ✅ Post created and scheduled!")
            else:
                print(f"   ✅ Post created successfully!")

        else:  # UPDATE
            result = blogger_client.update_post(
                blog_id=blog_id,
                post_id=post_id,
                title=title,
                content=html_content,
                labels=labels,
                is_draft=is_draft,
                published=published_date
            )
            post_url = result['url']
            if is_scheduled:
                print(f"   ✅ Post updated and rescheduled!")
            else:
                print(f"   ✅ Post updated successfully!")

        # Step 7: Update frontmatter
        print("\n💾 Updating frontmatter...")

        frontmatter_updates = {
            'blogger_id': post_id,
            'updated': datetime.utcnow().isoformat().replace('+00:00', 'Z')
        }

        if image_mappings:
            frontmatter_updates['images'] = image_mappings

        updated_markdown = update_frontmatter(markdown_content, frontmatter_updates)

        # Write atomically using temp file
        temp_fd, temp_path = tempfile.mkstemp(dir=post_dir, suffix='.md')
        try:
            with os.fdopen(temp_fd, 'w', encoding='utf-8') as f:
                f.write(updated_markdown)
            shutil.move(temp_path, post_file)
            print("   ✅ Frontmatter updated")
        except Exception as e:
            if Path(temp_path).exists():
                Path(temp_path).unlink()
            raise

        # Success summary
        print("\n" + "="*60)
        print("✅ PUBLISH SUCCESSFUL!")
        print("="*60)
        print(f"Title:        {title}")
        if is_scheduled:
            print(f"Status:       SCHEDULED for {published_date}")
        else:
            print(f"Status:       {'DRAFT' if is_draft else 'PUBLISHED'}")
        print(f"Post ID:      {post_id}")
        print(f"URL:          {post_url}")
        print(f"Images:       {len(image_mappings)} uploaded")
        print(f"Operation:    {post_status}")
        print("="*60)

        return 0

    except (ConfigError, ValidationError, FrontmatterError) as e:
        print(f"\n❌ {e}\n", file=sys.stderr)
        return 1
    except (BloggerError, CloudinaryError) as e:
        print(f"\n❌ API Error: {e}\n", file=sys.stderr)
        return 1
    except FileNotFoundError as e:
        print(f"\n❌ File not found: {e}\n", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}\n", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


def main():
    if len(sys.argv) != 2:
        print("Usage: uv run tools/publish.py <post-directory>", file=sys.stderr)
        print("\nExample:", file=sys.stderr)
        print("  uv run tools/publish.py posts/2025-10-12-my-first-post/", file=sys.stderr)
        sys.exit(1)

    post_dir = sys.argv[1]
    exit_code = publish_post(post_dir)
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
