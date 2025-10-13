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
- Links

Usage:
    uv run tools/seo_check.py website/content/posts/2025-10-12-hello-world.mdx
"""

import re
import sys
from pathlib import Path
from lib.frontmatter import parse_frontmatter

# Hardcoded valid categories
VALID_CATEGORIES = [
    'tutorials',
    'case-studies',
    'guides',
    'lists',
    'comparisons',
    'problem-solution',
    'opinions'
]


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


def analyze_seo(post_path: Path):
    """Analyze post for SEO best practices."""

    if not post_path.exists():
        print_error(f"File not found: {post_path}")
        return 1

    content = post_path.read_text()

    # Parse frontmatter
    try:
        frontmatter, body = parse_frontmatter(content)
    except Exception as e:
        print_error(f"Failed to parse frontmatter: {e}")
        return 1

    print(f"{Color.BOLD}📊 SEO Analysis for {post_path.name}{Color.END}\n")

    issues = []
    warnings = []

    # 1. Title length check
    title = frontmatter.get('title', '')
    title_len = len(title)

    if 30 <= title_len <= 60:
        print_success(f"Title length: {title_len} characters (optimal: 30-60)")
    elif title_len < 30:
        print_warning(f"Title length: {title_len} characters (too short, recommend 30-60)")
        warnings.append(f"Title is only {title_len} chars - consider making it more descriptive")
    elif title_len > 60:
        print_error(f"Title length: {title_len} characters (too long, recommend 30-60)")
        issues.append(f"Title is {title_len} chars - Google may truncate it in search results")
    else:
        print_error("No title found in frontmatter")
        issues.append("Missing title in frontmatter")

    # 2. Meta description check (REQUIRED for Next.js)
    description = frontmatter.get('description', '')
    if description:
        desc_len = len(description)
        if 150 <= desc_len <= 160:
            print_success(f"Meta description: {desc_len} characters (optimal: 150-160)")
        elif desc_len < 150:
            print_warning(f"Meta description: {desc_len} characters (short, recommend 150-160)")
            warnings.append(f"Description could be more detailed ({desc_len} chars)")
        else:
            print_error(f"Meta description: {desc_len} characters (too long, recommend 150-160)")
            issues.append(f"Description is {desc_len} chars - Google may truncate it")
    else:
        print_error("No meta description in frontmatter")
        issues.append("REQUIRED: Add 'description' field to frontmatter (150-160 chars)")

    # 3. Category validation (REQUIRED for Next.js)
    category = frontmatter.get('category', '')
    if category:
        if category in VALID_CATEGORIES:
            print_success(f"Category: '{category}' (valid)")
        else:
            print_error(f"Category: '{category}' (invalid)")
            issues.append(f"Invalid category '{category}'. Must be one of: {', '.join(VALID_CATEGORIES)}")
    else:
        print_error("No category in frontmatter")
        issues.append(f"REQUIRED: Add 'category' field. Valid options: {', '.join(VALID_CATEGORIES)}")

    # 4. Heading structure
    # Remove code blocks first to avoid counting comments as headings
    body_no_code_blocks = re.sub(r'```.*?```', '', body, flags=re.DOTALL)

    h1_headings = re.findall(r'^# (.+)$', body_no_code_blocks, re.MULTILINE)
    if len(h1_headings) == 1:
        print_success(f"Single H1 heading: '{h1_headings[0][:50]}...'")
    elif len(h1_headings) == 0:
        # For blog posts with frontmatter, the title serves as H1
        if title:
            print_success("H1 heading: Using frontmatter title (recommended for blog posts)")
        else:
            print_error("No H1 heading found in content")
            issues.append("Add a single H1 (#) heading to your content or a title in frontmatter")
    else:
        print_error(f"Multiple H1 headings found: {len(h1_headings)}")
        issues.append("Use only one H1 heading per page")

    # Check for heading hierarchy
    headings = re.findall(r'^(#{1,6}) (.+)$', body_no_code_blocks, re.MULTILINE)
    if headings:
        print_success(f"Total headings: {len(headings)}")
        # Check if headings skip levels
        levels = [len(h[0]) for h in headings]
        for i in range(1, len(levels)):
            if levels[i] - levels[i-1] > 1:
                print_warning(f"Heading hierarchy skip detected (H{levels[i-1]} → H{levels[i]})")
                warnings.append("Maintain proper heading hierarchy (don't skip levels)")
                break

    # 5. Content length
    # Remove code blocks and count words
    body_no_code = re.sub(r'```.*?```', '', body, flags=re.DOTALL)
    words = re.findall(r'\b\w+\b', body_no_code)
    word_count = len(words)

    if word_count >= 300:
        print_success(f"Word count: {word_count} words (minimum 300 recommended)")
    else:
        print_warning(f"Word count: {word_count} words (below 300 minimum)")
        warnings.append(f"Content is short ({word_count} words) - aim for 300+ for better SEO")

    # 6. Image alt text check
    images = re.findall(r'!\[(.*?)\]\((.+?)\)', body)
    if images:
        images_with_alt = [img for img in images if img[0]]
        if len(images_with_alt) == len(images):
            print_success(f"All {len(images)} images have alt text")
        else:
            missing = len(images) - len(images_with_alt)
            print_warning(f"{missing}/{len(images)} images missing alt text")
            warnings.append(f"Add descriptive alt text to {missing} image(s)")
    else:
        print_info("No images found")

    # 7. Internal/external links
    links = re.findall(r'\[([^\]]+)\]\(([^\)]+)\)', body)
    links = [l for l in links if not l[1].startswith('!')]  # Exclude images

    if links:
        internal_links = [l for l in links if not l[1].startswith('http')]
        external_links = [l for l in links if l[1].startswith('http')]
        print_success(f"Links: {len(internal_links)} internal, {len(external_links)} external")
    else:
        print_warning("No links found")
        warnings.append("Consider adding relevant internal/external links")

    # Summary
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

    return 1 if issues else 0


def main():
    if len(sys.argv) < 2:
        print("Usage: uv run tools/seo_check.py <path-to-post.mdx>")
        sys.exit(1)

    post_path = Path(sys.argv[1])

    # Handle MDX files
    if post_path.is_dir():
        # Look for .mdx file in directory
        mdx_files = list(post_path.glob("*.mdx"))
        if mdx_files:
            post_path = mdx_files[0]
        else:
            print(f"Error: No .mdx file found in {post_path}")
            sys.exit(1)

    sys.exit(analyze_seo(post_path))


if __name__ == "__main__":
    main()
