#!/usr/bin/env python3
"""Test Phase 1: Core Infrastructure"""

import sys
sys.path.insert(0, '.')

from lib.config import load_config, ConfigError
from lib.frontmatter import parse_frontmatter, validate_frontmatter, FrontmatterError
from lib.markdown_converter import create_converter

def test_config():
    """Test configuration loading"""
    print("=== Testing Configuration Loading ===\n")

    try:
        config = load_config()
        print(f"✅ Configuration loaded")
        print(f"   Blog: {config['blog_name']}")
        print(f"   Blog ID: {config['blogger_blog_id']}")
        print(f"   Cloudinary: {config['cloudinary']['cloud_name']}")
        return True
    except ConfigError as e:
        print(f"❌ Configuration error:\n{e}")
        return False


def test_frontmatter():
    """Test frontmatter parsing"""
    print("\n=== Testing Frontmatter Parser ===\n")

    test_markdown = """---
title: "Test Post"
date: 2025-10-12T10:00:00Z
tags: [python, tutorial]
status: draft
---

# Hello World

This is a test post.
"""

    try:
        frontmatter, body = parse_frontmatter(test_markdown)
        validate_frontmatter(frontmatter)

        print(f"✅ Frontmatter parsed")
        print(f"   Title: {frontmatter['title']}")
        print(f"   Date: {frontmatter['date']}")
        print(f"   Tags: {frontmatter['tags']}")
        print(f"   Body length: {len(body)} chars")
        return True
    except FrontmatterError as e:
        print(f"❌ Frontmatter error:\n{e}")
        return False


def test_markdown_converter():
    """Test markdown to HTML conversion"""
    print("\n=== Testing Markdown Converter ===\n")

    try:
        config = load_config()
        converter = create_converter(config)

        test_markdown = """# Hello World

This is **bold** and *italic*.

```python
def hello():
    print("Hello, world!")
```

- Item 1
- Item 2

| Column 1 | Column 2 |
|----------|----------|
| A        | B        |
"""

        html = converter.convert(test_markdown)

        print(f"✅ Markdown converted to HTML")
        print(f"   Input length: {len(test_markdown)} chars")
        print(f"   Output length: {len(html)} chars")
        print(f"   Has code highlighting: {'highlight' in html}")
        print(f"   Has table: {'<table>' in html}")
        return True
    except Exception as e:
        print(f"❌ Markdown conversion error:\n{e}")
        return False


def main():
    print("🧪 Phase 1: Core Infrastructure Tests\n")

    results = [
        test_config(),
        test_frontmatter(),
        test_markdown_converter()
    ]

    print("\n" + "="*50)
    if all(results):
        print("✅ All Phase 1 tests passed!")
    else:
        print("❌ Some tests failed")
    print("="*50 + "\n")

    return all(results)


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
