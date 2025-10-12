#!/usr/bin/env python3
"""
List all approved tags from tag registry

Usage:
    uv run tools/list_tags.py
"""

import sys
import yaml
from pathlib import Path


def main():
    registry_path = Path('tag-registry.yaml')

    if not registry_path.exists():
        print("❌ tag-registry.yaml not found", file=sys.stderr)
        sys.exit(1)

    with open(registry_path, 'r') as f:
        data = yaml.safe_load(f)

    tags = data.get('tags', [])

    print("📋 Approved Tags\n")
    print(f"Total: {len(tags)} tags\n")

    # Group tags by category (based on comments in file)
    for tag in sorted(tags):
        print(f"  - {tag}")

    print(f"\nEdit tag-registry.yaml to add new tags")


if __name__ == '__main__':
    main()
