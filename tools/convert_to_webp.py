#!/usr/bin/env python3
"""
Convert images to WebP format for Next.js website

Usage:
    uv run tools/convert_to_webp.py <input-image> <output-image>
    uv run tools/convert_to_webp.py <directory>  # Convert all images in directory

Examples:
    uv run tools/convert_to_webp.py hero.png hero.webp
    uv run tools/convert_to_webp.py website/public/blog/2025-10-12-my-post/
"""

import sys
from pathlib import Path
from PIL import Image


def convert_image_to_webp(input_path: Path, output_path: Path, quality: int = 85) -> None:
    """
    Convert image to WebP format

    Args:
        input_path: Source image path
        output_path: Destination WebP path
        quality: WebP quality (0-100, default 85)
    """
    print(f"Converting {input_path.name} → {output_path.name}...")

    with Image.open(input_path) as img:
        # Preserve transparency if present
        if img.mode in ('RGBA', 'LA'):
            # Keep alpha channel
            pass
        elif img.mode == 'P':
            # Convert palette to RGBA to preserve transparency
            img = img.convert('RGBA')
        elif img.mode != 'RGB':
            # Convert other modes to RGB
            img = img.convert('RGB')

        # Save as WebP (WebP supports transparency)
        img.save(
            output_path,
            format='WEBP',
            quality=quality,
            method=6  # Slowest but best compression
        )

    # Print size comparison
    original_size = input_path.stat().st_size
    webp_size = output_path.stat().st_size
    reduction = (1 - webp_size / original_size) * 100

    print(f"  Original: {original_size:,} bytes")
    print(f"  WebP:     {webp_size:,} bytes")
    print(f"  Saved:    {reduction:.1f}%")


def convert_directory(directory: Path, quality: int = 85) -> None:
    """
    Convert all PNG/JPG images in directory to WebP

    Args:
        directory: Directory containing images
        quality: WebP quality (0-100, default 85)
    """
    image_extensions = {'.png', '.jpg', '.jpeg'}
    image_files = [
        f for f in directory.iterdir()
        if f.is_file() and f.suffix.lower() in image_extensions
    ]

    if not image_files:
        print(f"No images found in {directory}")
        return

    print(f"Found {len(image_files)} image(s) in {directory}")
    print()

    for img_file in image_files:
        output_file = img_file.with_suffix('.webp')

        # Skip if WebP already exists and is newer
        if output_file.exists() and output_file.stat().st_mtime > img_file.stat().st_mtime:
            print(f"Skipping {img_file.name} (WebP is up-to-date)")
            continue

        try:
            convert_image_to_webp(img_file, output_file, quality)
            print()
        except Exception as e:
            print(f"  ❌ Error: {e}")
            print()
            continue


def main():
    if len(sys.argv) < 2:
        print("Usage:", file=sys.stderr)
        print("  uv run tools/convert_to_webp.py <input-image> <output-image> [quality]", file=sys.stderr)
        print("  uv run tools/convert_to_webp.py <directory> [quality]", file=sys.stderr)
        print("\nExamples:", file=sys.stderr)
        print("  uv run tools/convert_to_webp.py hero.png hero.webp", file=sys.stderr)
        print("  uv run tools/convert_to_webp.py hero.png hero.webp 100  # Max quality", file=sys.stderr)
        print("  uv run tools/convert_to_webp.py website/public/blog/2025-10-12-my-post/", file=sys.stderr)
        sys.exit(1)

    input_arg = Path(sys.argv[1])

    # Parse quality parameter (default 85)
    quality = 85
    quality_arg_index = 3 if not input_arg.is_dir() else 2
    if len(sys.argv) > quality_arg_index:
        try:
            quality = int(sys.argv[quality_arg_index])
            if quality < 0 or quality > 100:
                print("Error: Quality must be between 0 and 100", file=sys.stderr)
                sys.exit(1)
        except ValueError:
            print("Error: Quality must be an integer", file=sys.stderr)
            sys.exit(1)

    # Directory mode
    if input_arg.is_dir():
        convert_directory(input_arg, quality)
        sys.exit(0)

    # Single file mode
    if len(sys.argv) < 3:
        print("Error: When converting a single file, provide both input and output paths", file=sys.stderr)
        print("Usage: uv run tools/convert_to_webp.py <input-image> <output-image> [quality]", file=sys.stderr)
        sys.exit(1)

    input_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])

    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    try:
        convert_image_to_webp(input_path, output_path, quality)
        print("✅ Conversion complete!")
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
