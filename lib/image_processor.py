"""Image hashing and optimization"""

import hashlib
from pathlib import Path
from typing import Dict, Any
from PIL import Image


def compute_image_hash(image_path: Path) -> str:
    """
    Compute SHA-256 hash of image file

    Args:
        image_path: Path to image file

    Returns:
        Hash string in format "sha256:hexdigest"
    """
    sha256 = hashlib.sha256()

    with open(image_path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            sha256.update(chunk)

    return f"sha256:{sha256.hexdigest()}"


def get_image_info(image_path: Path) -> Dict[str, Any]:
    """
    Get image metadata

    Args:
        image_path: Path to image file

    Returns:
        Dict with width, height, format, size
    """
    with Image.open(image_path) as img:
        return {
            'width': img.width,
            'height': img.height,
            'format': img.format,
            'size_bytes': image_path.stat().st_size,
            'mode': img.mode
        }


def check_image_needs_upload(
    image_path: Path,
    cached_images: Dict[str, Any]
) -> bool:
    """
    Check if image needs to be uploaded

    Args:
        image_path: Path to image file (relative to post dir)
        cached_images: Cached image mappings from frontmatter

    Returns:
        True if image needs upload (new or changed), False otherwise
    """
    image_key = str(image_path)

    # Not in cache - needs upload
    if image_key not in cached_images:
        return True

    # Check if hash matches
    cached_hash = cached_images[image_key].get('hash')
    if not cached_hash:
        return True

    current_hash = compute_image_hash(image_path)
    return current_hash != cached_hash


def optimize_image(
    image_path: Path,
    config: Dict[str, Any],
    output_path: Path = None
) -> Path:
    """
    Optimize image (resize, compress) before upload

    Args:
        image_path: Path to source image
        config: Image optimization config
        output_path: Optional output path (defaults to overwrite)

    Returns:
        Path to optimized image
    """
    if output_path is None:
        output_path = image_path

    max_width = config.get('max_width', 1200)
    max_height = config.get('max_height', 1200)
    quality = config.get('quality', 85)
    output_format = config.get('format', 'JPEG')

    with Image.open(image_path) as img:
        # Convert RGBA to RGB if saving as JPEG
        if img.mode == 'RGBA' and output_format == 'JPEG':
            # Create white background
            background = Image.new('RGB', img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[3])  # Use alpha as mask
            img = background

        # Resize if needed
        if img.width > max_width or img.height > max_height:
            img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)

        # Save optimized
        save_kwargs = {'quality': quality, 'optimize': True}
        if output_format == 'JPEG':
            save_kwargs['progressive'] = True

        img.save(output_path, format=output_format, **save_kwargs)

    return output_path
