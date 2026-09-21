#!/usr/bin/env python3
"""
Quality checker for newsletter issues (MDX format).

The blog's seo_check.py cannot be reused here: it requires a `category` from the
blog's seven, and issues have none. This is the lighter sibling for issues.
The checks live in lib/issue_checks.py so tools/verify_content.py reports the
same numbers.

Usage:
    uv run tools/issue_check.py website/content/issues/2026-09-21-slug.mdx
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from lib.config import load_config, get_newsletter_config
from lib.issue_checks import analyze_issue, check_archive_delay_agreement


def main() -> int:
    parser = argparse.ArgumentParser(description="Quality check a newsletter issue")
    parser.add_argument("path", help="Path to the issue .mdx file")
    args = parser.parse_args()

    try:
        newsletter = get_newsletter_config(load_config())
    except Exception as e:
        print(f"❌ Error loading configuration: {e}", file=sys.stderr)
        return 1

    issue_path = Path(args.path)
    print(f"\n📋 Issue check: {issue_path.name}")
    print("=" * 60)

    errors, warnings, info = analyze_issue(issue_path, newsletter['archive_delay_days'])
    warnings.extend(check_archive_delay_agreement(newsletter['archive_delay_days']))

    for line in info:
        print(line)
    for error in errors:
        print(f"❌ {error}")
    for warning in warnings:
        print(f"⚠️  {warning}")

    if not errors and not warnings:
        print("✅ No issues found")

    print(f"\nTotal: {len(errors)} error(s), {len(warnings)} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
