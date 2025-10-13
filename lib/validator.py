"""Post validation logic for Next.js MDX blog"""

import re
from pathlib import Path
from typing import List, Tuple, Dict, Any
from .frontmatter import parse_frontmatter, FrontmatterError

# Valid categories (hardcoded)
VALID_CATEGORIES = [
    'tutorials',
    'case-studies',
    'guides',
    'lists',
    'comparisons',
    'problem-solution',
    'opinions'
]


class ValidationError(Exception):
    """Validation errors"""
    pass


def validate_mdx_file(mdx_path: Path) -> Tuple[Dict[str, Any], str]:
    """
    Validate MDX file for Next.js blog

    Args:
        mdx_path: Path to .mdx file

    Returns:
        Tuple of (frontmatter, body)

    Raises:
        ValidationError: If MDX file is invalid
    """
    if not mdx_path.exists():
        raise ValidationError(f"❌ MDX file not found: {mdx_path}")

    if not mdx_path.suffix == '.mdx':
        raise ValidationError(f"❌ Not an MDX file: {mdx_path}")

    # Read and parse MDX content
    content = mdx_path.read_text()

    try:
        frontmatter, body = parse_frontmatter(content)
    except FrontmatterError as e:
        raise ValidationError(str(e))

    # Validate required frontmatter fields
    required_fields = ['title', 'description', 'date', 'category']
    missing_fields = [f for f in required_fields if f not in frontmatter]

    if missing_fields:
        raise ValidationError(
            f"❌ Missing required frontmatter fields: {', '.join(missing_fields)}\n"
            f"Required fields: title, description, date, category"
        )

    # Validate category
    category = frontmatter.get('category')
    if category not in VALID_CATEGORIES:
        raise ValidationError(
            f"❌ Invalid category: '{category}'\n"
            f"Valid categories: {', '.join(VALID_CATEGORIES)}"
        )

    # Validate description length (SEO recommendation)
    description = frontmatter.get('description', '')
    if len(description) < 100:
        raise ValidationError(
            f"❌ Description too short: {len(description)} chars (recommend 150-160)"
        )
    elif len(description) > 170:
        raise ValidationError(
            f"❌ Description too long: {len(description)} chars (recommend 150-160)"
        )

    # Validate image references
    slug = mdx_path.stem  # e.g., "2025-10-12-my-post"
    image_dir = Path(f"website/public/blog/{slug}")
    image_refs = extract_image_references(body)
    missing_images = []

    for img_ref in image_refs:
        # Handle relative paths
        if img_ref.startswith('./'):
            img_path = image_dir / img_ref[2:]
            if not img_path.exists():
                missing_images.append(img_ref)

    if missing_images:
        raise ValidationError(
            f"❌ Referenced images not found:\n" +
            "\n".join(f"   - {img}" for img in missing_images) +
            f"\n\nPlace images in: {image_dir}/"
        )

    return frontmatter, body


def extract_image_references(markdown_body: str) -> List[str]:
    """
    Extract all image references from markdown

    Args:
        markdown_body: Markdown content

    Returns:
        List of image paths referenced in markdown
    """
    image_refs = []

    # Pattern 1: ![alt](path)
    markdown_pattern = r'!\[.*?\]\(([^)]+)\)'
    image_refs.extend(re.findall(markdown_pattern, markdown_body))

    # Pattern 2: <img src="path">
    html_pattern = r'<img[^>]+src=["\']([^"\']+)["\']'
    image_refs.extend(re.findall(html_pattern, markdown_body))

    # Filter out external URLs (http://, https://)
    local_images = [
        img for img in image_refs
        if not img.startswith(('http://', 'https://'))
    ]

    return local_images
