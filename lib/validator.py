"""Post validation logic"""

import re
import yaml
from pathlib import Path
from typing import List, Tuple, Dict, Any, Set
from .frontmatter import parse_frontmatter, validate_frontmatter, FrontmatterError


class ValidationError(Exception):
    """Validation errors"""
    pass


def load_tag_registry() -> Set[str]:
    """
    Load approved tags from tag-registry.yaml

    Returns:
        Set of approved tag strings

    Raises:
        ValidationError: If tag registry file is missing or invalid
    """
    registry_path = Path('tag-registry.yaml')

    if not registry_path.exists():
        raise ValidationError(
            "❌ tag-registry.yaml not found\n"
            "Create tag-registry.yaml with approved tags.\n"
            "See README for format."
        )

    try:
        with open(registry_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)

        if not isinstance(data, dict) or 'tags' not in data:
            raise ValidationError(
                "❌ Invalid tag-registry.yaml format\n"
                "File must contain a 'tags' list:\n"
                "tags:\n"
                "  - python\n"
                "  - tutorial"
            )

        tags = data['tags']
        if not isinstance(tags, list):
            raise ValidationError(
                "❌ 'tags' in tag-registry.yaml must be a list"
            )

        return set(str(tag).lower() for tag in tags)

    except yaml.YAMLError as e:
        raise ValidationError(f"❌ Invalid YAML in tag-registry.yaml: {e}")


def validate_post_directory(post_dir: Path) -> None:
    """
    Validate post directory structure and naming

    Args:
        post_dir: Path to post directory

    Raises:
        ValidationError: If directory structure is invalid
    """
    if not post_dir.exists():
        raise ValidationError(
            f"❌ Post directory not found: {post_dir}\n"
            f"Create directory: mkdir -p {post_dir}"
        )

    if not post_dir.is_dir():
        raise ValidationError(
            f"❌ Not a directory: {post_dir}\n"
            f"Provide a directory path containing post.md"
        )

    # Validate directory name format: YYYY-MM-DD-slug
    dir_name = post_dir.name
    pattern = r'^\d{4}-\d{2}-\d{2}-.+$'

    if not re.match(pattern, dir_name):
        raise ValidationError(
            f"❌ Invalid directory name: {dir_name}\n"
            f"Format: YYYY-MM-DD-slug\n"
            f"Example: 2025-10-12-my-first-post"
        )

    # Check for post.md
    post_file = post_dir / 'post.md'
    if not post_file.exists():
        raise ValidationError(
            f"❌ post.md not found in {post_dir}\n"
            f"Create file: {post_file}"
        )


def validate_post_content(markdown_content: str, post_dir: Path) -> Tuple[Dict[str, Any], str]:
    """
    Validate post markdown content

    Args:
        markdown_content: Raw markdown with frontmatter
        post_dir: Path to post directory (for image validation)

    Returns:
        Tuple of (frontmatter, body)

    Raises:
        ValidationError: If content is invalid
    """
    try:
        frontmatter, body = parse_frontmatter(markdown_content)
        validate_frontmatter(frontmatter)
    except FrontmatterError as e:
        raise ValidationError(str(e))

    # Validate tags against registry
    if 'tags' in frontmatter and frontmatter['tags']:
        validate_tags(frontmatter['tags'])

    # Validate referenced images exist
    image_refs = extract_image_references(body)
    missing_images = []

    for img_path in image_refs:
        # Resolve relative to post directory
        if img_path.startswith('./'):
            img_path = img_path[2:]

        full_path = post_dir / img_path
        if not full_path.exists():
            missing_images.append(img_path)

    if missing_images:
        raise ValidationError(
            f"❌ Referenced images not found:\n" +
            "\n".join(f"   - {img}" for img in missing_images) +
            f"\n\nPlace images in: {post_dir}/"
        )

    return frontmatter, body


def validate_tags(post_tags: List[str]) -> None:
    """
    Validate that post tags are in the approved registry

    Args:
        post_tags: List of tags from post frontmatter

    Raises:
        ValidationError: If tags are not in registry
    """
    if not post_tags:
        return

    approved_tags = load_tag_registry()

    # Normalize post tags to lowercase for comparison
    normalized_post_tags = [str(tag).lower() for tag in post_tags]

    # Find unapproved tags
    unapproved = [tag for tag in normalized_post_tags if tag not in approved_tags]

    if unapproved:
        # Show available tags that might be similar
        suggestions = []
        for bad_tag in unapproved:
            similar = [t for t in approved_tags if bad_tag in t or t in bad_tag]
            if similar:
                suggestions.append(f"   - '{bad_tag}' → try: {', '.join(similar[:3])}")
            else:
                suggestions.append(f"   - '{bad_tag}' → not found")

        raise ValidationError(
            f"❌ Unapproved tags used: {', '.join(unapproved)}\n\n"
            f"Suggestions:\n" + "\n".join(suggestions) + "\n\n"
            f"To use these tags:\n"
            f"  1. Add them to tag-registry.yaml\n"
            f"  2. Run build again\n\n"
            f"View approved tags: cat tag-registry.yaml"
        )


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


def derive_blogger_path(post_dir: Path) -> str:
    """
    Derive Blogger URL path from directory name

    Args:
        post_dir: Path to post directory

    Returns:
        Blogger URL path (e.g., /2025/10/my-post.html)

    Raises:
        ValidationError: If directory name doesn't match format
    """
    dir_name = post_dir.name
    match = re.match(r'(\d{4})-(\d{2})-(\d{2})-(.+)', dir_name)

    if not match:
        raise ValidationError(
            f"❌ Cannot derive URL path from: {dir_name}\n"
            f"Directory must match: YYYY-MM-DD-slug"
        )

    year, month, day, slug = match.groups()
    return f"/{year}/{month}/{slug}.html"
