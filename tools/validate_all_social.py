#!/usr/bin/env python3
"""Validate all social media posts in blog content.

Quick script to check all posts have valid social content.
"""

from pathlib import Path
from lib.config import load_config
from lib.frontmatter import parse_frontmatter
from lib.social_validator import validate_social_posts, print_validation_results


def main():
    """Validate all posts."""
    config = load_config()
    content_dir = Path(config["content_dir"])

    posts = sorted(content_dir.glob("*.mdx"))

    print(f"Validating {len(posts)} posts...\n")

    total_errors = 0
    total_warnings = 0

    for post_file in posts:
        slug = post_file.stem
        content = post_file.read_text(encoding="utf-8")
        fm, _ = parse_frontmatter(content)

        issues = validate_social_posts(fm, slug)

        errors = [i for i in issues if i.severity == "error"]
        warnings = [i for i in issues if i.severity == "warning"]

        if issues:
            print(f"📄 {slug}")
            print_validation_results(issues)
            print()
            total_errors += len(errors)
            total_warnings += len(warnings)

    print(f"{'='*60}")
    print(f"Total: {total_errors} error(s), {total_warnings} warning(s)")
    print(f"{'='*60}")

    if total_errors > 0:
        exit(1)


if __name__ == "__main__":
    main()
