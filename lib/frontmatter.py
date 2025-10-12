"""Frontmatter parsing and serialization"""

import yaml
import re
from typing import Dict, Any, Tuple
from datetime import datetime


class FrontmatterError(Exception):
    """Frontmatter parsing errors"""
    pass


def parse_frontmatter(markdown_content: str) -> Tuple[Dict[str, Any], str]:
    """
    Parse YAML frontmatter from markdown content

    Args:
        markdown_content: Raw markdown content with frontmatter

    Returns:
        Tuple of (frontmatter_dict, body_content)

    Raises:
        FrontmatterError: If frontmatter is invalid or missing
    """
    # Match frontmatter: --- at start, content, --- delimiter
    pattern = r'^---\s*\n(.*?)\n---\s*\n(.*)$'
    match = re.match(pattern, markdown_content, re.DOTALL)

    if not match:
        raise FrontmatterError(
            "❌ No frontmatter found\n"
            "Markdown must start with:\n"
            "---\n"
            "title: \"Your Title\"\n"
            "date: 2025-10-12T10:00:00Z\n"
            "---"
        )

    frontmatter_str, body = match.groups()

    try:
        frontmatter = yaml.safe_load(frontmatter_str)
        if not isinstance(frontmatter, dict):
            raise FrontmatterError("Frontmatter must be a YAML dictionary")
    except yaml.YAMLError as e:
        raise FrontmatterError(f"❌ Invalid YAML in frontmatter: {e}")

    return frontmatter, body


def validate_frontmatter(frontmatter: Dict[str, Any]) -> None:
    """
    Validate frontmatter has required fields

    Args:
        frontmatter: Parsed frontmatter dict

    Raises:
        FrontmatterError: If required fields are missing or invalid
    """
    # Required fields
    required = ['title', 'date']
    missing = [f for f in required if f not in frontmatter or not frontmatter[f]]

    if missing:
        raise FrontmatterError(
            f"❌ Missing required frontmatter fields: {', '.join(missing)}\n"
            f"Example:\n"
            f"  title: \"My Post Title\"\n"
            f"  date: 2025-10-12T10:00:00Z"
        )

    # Validate date format (ISO 8601)
    date_str = frontmatter['date']
    if isinstance(date_str, datetime):
        # Already parsed by YAML
        return

    try:
        datetime.fromisoformat(str(date_str).replace('Z', '+00:00'))
    except (ValueError, AttributeError):
        raise FrontmatterError(
            f"❌ Invalid date format: {date_str}\n"
            f"Use ISO 8601 format: 2025-10-12T10:00:00Z"
        )

    # Validate status if present
    if 'status' in frontmatter:
        valid_statuses = ['draft', 'published']
        status = frontmatter['status']
        if status not in valid_statuses:
            raise FrontmatterError(
                f"❌ Invalid status: {status}\n"
                f"Valid values: {', '.join(valid_statuses)}"
            )

    # Validate tags if present
    if 'tags' in frontmatter:
        tags = frontmatter['tags']
        if not isinstance(tags, list):
            raise FrontmatterError(
                f"❌ Tags must be a list\n"
                f"Example: tags: [python, tutorial]"
            )


def serialize_frontmatter(frontmatter: Dict[str, Any], body: str) -> str:
    """
    Serialize frontmatter and body back to markdown

    Args:
        frontmatter: Frontmatter dict to serialize
        body: Markdown body content

    Returns:
        Complete markdown with frontmatter
    """
    # Convert datetime objects to ISO format strings
    serializable = {}
    for key, value in frontmatter.items():
        if isinstance(value, datetime):
            serializable[key] = value.isoformat().replace('+00:00', 'Z')
        else:
            serializable[key] = value

    frontmatter_str = yaml.dump(
        serializable,
        default_flow_style=False,
        allow_unicode=True,
        sort_keys=False
    )

    return f"---\n{frontmatter_str}---\n{body}"


def update_frontmatter(
    markdown_content: str,
    updates: Dict[str, Any]
) -> str:
    """
    Update frontmatter fields in markdown content

    Args:
        markdown_content: Original markdown with frontmatter
        updates: Dict of fields to update/add

    Returns:
        Updated markdown content

    Raises:
        FrontmatterError: If parsing fails
    """
    frontmatter, body = parse_frontmatter(markdown_content)
    frontmatter.update(updates)
    return serialize_frontmatter(frontmatter, body)


def get_post_slug(frontmatter: Dict[str, Any]) -> str:
    """
    Generate a URL-friendly slug from title

    Args:
        frontmatter: Parsed frontmatter

    Returns:
        URL-friendly slug
    """
    title = frontmatter.get('title', 'untitled')

    # Convert to lowercase, replace spaces with hyphens
    slug = title.lower()
    slug = re.sub(r'[^\w\s-]', '', slug)  # Remove special chars
    slug = re.sub(r'[-\s]+', '-', slug)    # Replace spaces/multiple hyphens
    slug = slug.strip('-')                  # Remove leading/trailing hyphens

    return slug or 'untitled'
