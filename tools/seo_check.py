#!/usr/bin/env python3
"""
SEO checker for blog posts (MDX format).

Analyzes MDX content for SEO best practices:
- Title length (30-60 characters optimal for Google)
- Meta description (150-160 characters, required)
- Category validation (must be one of 7 hardcoded options)
- Heading structure (single H1, proper hierarchy)
- Content length (minimum 300 words recommended)
- Image alt text
- Hero image presence (hero-*.webp required for OG/Twitter cards)
- Links

The checks live in lib/post_checks.py so tools/verify_content.py reports the
same numbers. This file is the human-readable report.

Usage:
    uv run tools/seo_check.py website/content/posts/2025-10-12-hello-world.mdx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from lib.frontmatter import FrontmatterError
from lib.post_checks import analyze_post, measure_post


class Color:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'


def print_success(text):
    print(f"{Color.GREEN}✅ {text}{Color.END}")


def print_error(text):
    print(f"{Color.RED}❌ {text}{Color.END}")


def print_warning(text):
    print(f"{Color.YELLOW}⚠️  {text}{Color.END}")


def print_info(text):
    print(f"{Color.BLUE}ℹ️  {text}{Color.END}")


PRINTERS = {
    'success': print_success,
    'error': print_error,
    'warning': print_warning,
    'info': print_info,
}


def analyze_seo(post_path: Path):
    """Print the SEO report for one post. Returns the exit code."""
    try:
        measure_post(post_path)
    except FileNotFoundError:
        print_error(f"File not found: {post_path}")
        return 1
    except FrontmatterError as e:
        print_error(f"Failed to parse frontmatter: {e}")
        return 1

    print(f"{Color.BOLD}📊 SEO Analysis for {post_path.name}{Color.END}\n")

    findings, issues, warnings, exit_code = analyze_post(post_path)
    for finding in findings:
        PRINTERS[finding.level](finding.text)

    print(f"\n{Color.BOLD}Summary{Color.END}")

    if not issues and not warnings:
        print_success("Excellent! All SEO checks passed 🎉")
        return 0

    if issues:
        print(f"\n{Color.RED}Issues to fix:{Color.END}")
        for issue in issues:
            print(f"  • {issue}")

    if warnings:
        print(f"\n{Color.YELLOW}Recommendations:{Color.END}")
        for warning in warnings:
            print(f"  • {warning}")

    return exit_code


def main():
    if len(sys.argv) < 2:
        print("Usage: uv run tools/seo_check.py <path-to-post.mdx>")
        sys.exit(1)

    post_path = Path(sys.argv[1])

    if post_path.is_dir():
        mdx_files = list(post_path.glob("*.mdx"))
        if mdx_files:
            post_path = mdx_files[0]
        else:
            print(f"Error: No .mdx file found in {post_path}")
            sys.exit(1)

    sys.exit(analyze_seo(post_path))


if __name__ == "__main__":
    main()
