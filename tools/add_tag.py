#!/usr/bin/env python3
"""
Add a new tag to the registry

Usage:
    uv run tools/add_tag.py <tag-name>

Example:
    uv run tools/add_tag.py docker
"""

import sys
import yaml
from pathlib import Path


def add_tag(tag_name: str) -> int:
    """
    Add a tag to the registry

    Args:
        tag_name: Tag to add

    Returns:
        Exit code
    """
    registry_path = Path('tag-registry.yaml')

    if not registry_path.exists():
        print("❌ tag-registry.yaml not found", file=sys.stderr)
        return 1

    # Load registry
    with open(registry_path, 'r') as f:
        data = yaml.safe_load(f)

    tags = data.get('tags', [])

    # Normalize tag name
    normalized_tag = tag_name.lower().strip()

    # Check if already exists
    if normalized_tag in [str(t).lower() for t in tags]:
        print(f"ℹ️  Tag '{normalized_tag}' already exists in registry")
        return 0

    # Add tag
    tags.append(normalized_tag)
    tags.sort()

    data['tags'] = tags

    # Write back
    with open(registry_path, 'w') as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False)

    print(f"✅ Added tag '{normalized_tag}' to registry")
    print(f"   Total tags: {len(tags)}")

    return 0


def main():
    if len(sys.argv) != 2:
        print("Usage: uv run tools/add_tag.py <tag-name>", file=sys.stderr)
        print("\nExample:", file=sys.stderr)
        print("  uv run tools/add_tag.py docker", file=sys.stderr)
        sys.exit(1)

    tag_name = sys.argv[1]
    exit_code = add_tag(tag_name)
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
