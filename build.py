#!/usr/bin/env python3
"""
Build command: Validate and preview blog post

Usage:
    uv run build.py <post-directory>

Example:
    uv run build.py posts/2025-10-12-my-first-post/
"""

import sys
from pathlib import Path
from lib.config import load_config, ConfigError
from lib.validator import (
    validate_post_directory,
    validate_post_content,
    extract_image_references,
    derive_blogger_path,
    ValidationError
)
from lib.frontmatter import parse_frontmatter
from lib.markdown_converter import create_converter
from lib.image_processor import compute_image_hash, get_image_info


def build_post(post_dir_str: str) -> int:
    """
    Validate and preview a blog post

    Args:
        post_dir_str: Path to post directory

    Returns:
        Exit code (0 = success, 1 = error)
    """
    try:
        # Load configuration
        print("📋 Loading configuration...")
        config = load_config()

        # Validate post directory
        post_dir = Path(post_dir_str).resolve()
        print(f"🔍 Validating post directory: {post_dir.name}")
        validate_post_directory(post_dir)

        # Read post content
        post_file = post_dir / 'post.md'
        with open(post_file, 'r', encoding='utf-8') as f:
            markdown_content = f.read()

        # Validate content
        print("📝 Validating post content...")
        frontmatter, body = validate_post_content(markdown_content, post_dir)

        # Extract image references
        image_refs = extract_image_references(body)
        print(f"🖼️  Found {len(image_refs)} image(s)")

        # Compute image hashes
        image_info = {}
        for img_ref in image_refs:
            # Normalize path
            if img_ref.startswith('./'):
                img_ref = img_ref[2:]

            img_path = post_dir / img_ref
            hash_val = compute_image_hash(img_path)
            info = get_image_info(img_path)

            # Check if in frontmatter cache
            cached_images = frontmatter.get('images', {})
            cached_hash = cached_images.get(img_ref, {}).get('hash')

            status = "✓ cached" if cached_hash == hash_val else "→ needs upload"
            image_info[img_ref] = {
                'hash': hash_val,
                'info': info,
                'status': status
            }

            print(f"   {img_ref}: {status}")
            print(f"      {info['width']}x{info['height']} {info['format']}, {info['size_bytes']:,} bytes")

        # Derive Blogger path
        blogger_path = derive_blogger_path(post_dir)

        # Check if post exists
        blogger_id = frontmatter.get('blogger_id')
        post_status = "UPDATE" if blogger_id else "NEW"

        # Convert markdown to HTML
        print("📄 Converting markdown to HTML...")
        converter = create_converter(config)
        html_body = converter.convert(body)

        # Generate preview
        preview_file = post_dir / 'preview.html'
        with open(preview_file, 'w', encoding='utf-8') as f:
            f.write(generate_preview_html(frontmatter, html_body, converter))

        print(f"💾 Preview saved: {preview_file}")

        # Print summary
        print("\n" + "="*60)
        print("✅ Validation successful!")
        print("="*60)
        print(f"Title:        {frontmatter['title']}")
        print(f"Date:         {frontmatter['date']}")
        print(f"Status:       {frontmatter.get('status', 'published')}")
        print(f"Tags:         {', '.join(frontmatter.get('tags', []))}")
        print(f"Post type:    {post_status}")
        print(f"Blogger path: {blogger_path}")
        print(f"Images:       {len(image_refs)} ({'all cached' if all(info['status'] == '✓ cached' for info in image_info.values()) else 'some need upload'})")
        print("\n✅ Ready to publish!")
        print(f"   Run: uv run publish.py {post_dir_str}")
        print("="*60)

        return 0

    except (ConfigError, ValidationError) as e:
        print(f"\n{e}\n", file=sys.stderr)
        return 1
    except FileNotFoundError as e:
        print(f"\n❌ File not found: {e}\n", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}\n", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


def generate_preview_html(frontmatter: dict, body_html: str, converter) -> str:
    """Generate standalone HTML preview"""
    css = converter.get_css()

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{frontmatter['title']} - Preview</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
            line-height: 1.6;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background: #fff;
            color: #333;
        }}
        h1, h2, h3, h4, h5, h6 {{
            margin-top: 24px;
            margin-bottom: 16px;
            font-weight: 600;
            line-height: 1.25;
        }}
        h1 {{ font-size: 2em; border-bottom: 1px solid #eaecef; padding-bottom: 0.3em; }}
        h2 {{ font-size: 1.5em; border-bottom: 1px solid #eaecef; padding-bottom: 0.3em; }}
        code {{
            background: #f6f8fa;
            padding: 0.2em 0.4em;
            margin: 0;
            font-size: 85%;
            border-radius: 3px;
        }}
        pre {{
            background: #f6f8fa;
            padding: 16px;
            overflow: auto;
            line-height: 1.45;
            border-radius: 3px;
        }}
        pre code {{
            background: transparent;
            padding: 0;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 16px 0;
        }}
        table th, table td {{
            border: 1px solid #dfe2e5;
            padding: 6px 13px;
        }}
        table th {{
            background: #f6f8fa;
            font-weight: 600;
        }}
        img {{
            max-width: 100%;
            height: auto;
        }}
        .meta {{
            color: #666;
            font-size: 0.9em;
            margin-bottom: 30px;
            padding: 10px;
            background: #f6f8fa;
            border-radius: 3px;
        }}
        {css}
    </style>
</head>
<body>
    <div class="meta">
        <strong>Title:</strong> {frontmatter['title']}<br>
        <strong>Date:</strong> {frontmatter['date']}<br>
        <strong>Status:</strong> {frontmatter.get('status', 'published')}<br>
        <strong>Tags:</strong> {', '.join(frontmatter.get('tags', []))}
    </div>
    {body_html}
</body>
</html>
"""


def main():
    if len(sys.argv) != 2:
        print("Usage: uv run build.py <post-directory>", file=sys.stderr)
        print("\nExample:", file=sys.stderr)
        print("  uv run build.py posts/2025-10-12-my-first-post/", file=sys.stderr)
        sys.exit(1)

    post_dir = sys.argv[1]
    exit_code = build_post(post_dir)
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
