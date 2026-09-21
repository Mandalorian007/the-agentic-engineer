#!/usr/bin/env python3
"""
One-time migration: move `social:` frontmatter into `surface/<stem>/` and
convert the single-file surface kits to the directory layout.

For every post in website/content/posts:
  1. Read `social.twitter.text` and `social.linkedin.text` through the YAML
     parser (that is what handles the multi-line quoted scalars correctly).
  2. Write surface/<stem>/x.md and surface/<stem>/linkedin.md.
  3. Remove the `social:` block from the raw file text by line range, from the
     `social:` line through the line before the closing `---`. No YAML
     round-trip, so nothing else in the file moves.
  4. Re-parse and assert the rest of the frontmatter and the body are unchanged.

For every legacy kit surface/<stem>.md:
  1. The `## LinkedIn` section replaces linkedin.md (the kit holds the copy
     that was actually pasted; the frontmatter copy of the newest post was
     reflowed by a YAML rewrite).
  2. The `## Reddit` or `## Hacker News` section becomes reddit.md / hn.md.
  3. `shape:` is added to the post's frontmatter from the kit's `Shape:` line.
  4. The single file is deleted.

Usage:
    uv run tools/migrate_social_to_surface.py --dry-run
    uv run tools/migrate_social_to_surface.py
"""

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from lib.config import load_config, get_stream_config
from lib.frontmatter import parse_frontmatter
from lib import surface

PROJECT_ROOT = Path(__file__).parent.parent
TOP_LEVEL_KEY_RE = re.compile(r'^[A-Za-z_][A-Za-z0-9_-]*:')


class MigrationError(Exception):
    pass


def frontmatter_bounds(lines: list) -> int:
    """Index of the closing `---` line. The opening one is line 0."""
    if not lines or lines[0].strip() != '---':
        raise MigrationError("file does not start with ---")
    for i in range(1, len(lines)):
        if lines[i].strip() == '---':
            return i
    raise MigrationError("no closing --- found")


def remove_social_block(content: str) -> str:
    """Delete `social:` and everything under it, up to the closing delimiter."""
    lines = content.split('\n')
    close = frontmatter_bounds(lines)

    starts = [i for i in range(1, close) if lines[i].startswith('social:')]
    if len(starts) != 1:
        raise MigrationError(f"expected one social: line, found {len(starts)}")
    start = starts[0]

    trailing_keys = [
        lines[i] for i in range(start + 1, close) if TOP_LEVEL_KEY_RE.match(lines[i])
    ]
    if trailing_keys:
        raise MigrationError(
            f"social: is not the last key; found after it: {trailing_keys[0]!r}"
        )

    del lines[start:close]
    return '\n'.join(lines)


def insert_frontmatter_line(content: str, line: str) -> str:
    """Add one top-level line just before the closing delimiter."""
    lines = content.split('\n')
    close = frontmatter_bounds(lines)
    lines.insert(close, line)
    return '\n'.join(lines)


def migrate_post(path: Path, dry_run: bool) -> str:
    content = path.read_text(encoding='utf-8')
    fm, body = parse_frontmatter(content)
    stem = path.stem

    if 'social' not in fm:
        return f"{stem}: no social: block, skipped"

    social = fm.get('social') or {}
    tweet = str((social.get('twitter') or {}).get('text') or '').strip()
    linkedin = str((social.get('linkedin') or {}).get('text') or '').strip()

    new_content = remove_social_block(content)

    fm2, body2 = parse_frontmatter(new_content)
    if 'social' in fm2:
        raise MigrationError(f"{stem}: social: survived removal")
    expected = {k: v for k, v in fm.items() if k != 'social'}
    if fm2 != expected:
        raise MigrationError(f"{stem}: other frontmatter keys changed during removal")
    if body2 != body:
        raise MigrationError(f"{stem}: body changed during removal")

    removed = content.count('\n') - new_content.count('\n')
    note = []
    if not tweet:
        note.append("no tweet text")
    if not linkedin:
        note.append("no linkedin text")

    if not dry_run:
        if tweet:
            surface.write_file(stem, 'x.md', tweet)
        if linkedin:
            surface.write_file(stem, 'linkedin.md', linkedin)
        path.write_text(new_content, encoding='utf-8')

    extra = f"  ({'; '.join(note)})" if note else ''
    return f"{stem}: x {len(tweet)} chars, linkedin {len(linkedin)} chars, {removed} lines removed{extra}"


def split_sections(text: str) -> tuple:
    """(header, {heading: body}) split on `## ` lines."""
    header, sections, current = [], {}, None
    for line in text.split('\n'):
        if line.startswith('## '):
            current = line[3:].strip()
            sections[current] = []
        elif current is None:
            header.append(line)
        else:
            sections[current].append(line)
    return '\n'.join(header), {k: '\n'.join(v).strip() for k, v in sections.items()}


def convert_legacy_kit(kit: Path, posts_dir: Path, dry_run: bool) -> str:
    stem = kit.stem
    post_path = posts_dir / f"{stem}.mdx"
    if not post_path.exists():
        raise MigrationError(f"{kit.name}: no post at {post_path}")

    header, sections = split_sections(kit.read_text(encoding='utf-8'))
    shape_match = re.search(r'^Shape:\s*(\w+)', header, re.MULTILINE)
    if not shape_match or shape_match.group(1) not in surface.SHAPES:
        raise MigrationError(f"{kit.name}: no usable Shape: line")
    shape = shape_match.group(1)

    written = []

    linkedin = sections.get('LinkedIn', '')
    li_lines = [l for l in linkedin.split('\n')]
    if li_lines and li_lines[0].startswith('Paste as a text post'):
        li_lines = li_lines[1:]
    if li_lines and li_lines[-1].startswith('First comment:'):
        li_lines = li_lines[:-1]
    linkedin = '\n'.join(li_lines).strip()
    if not linkedin:
        raise MigrationError(f"{kit.name}: empty LinkedIn section")
    written.append(('linkedin.md', linkedin))

    if shape == 'tutorial':
        reddit = sections.get('Reddit', '')
        sub = re.search(r'\b(r/\w+)', reddit)
        title = re.search(r'^Title:\s*(.+)$', reddit, re.MULTILINE)
        body_idx = reddit.find('Body:')
        if not (sub and title and body_idx >= 0):
            raise MigrationError(f"{kit.name}: Reddit section missing subreddit, title or body")
        body = reddit[body_idx + len('Body:'):].strip()
        written.append(('reddit.md', f"Subreddit: {sub.group(1)}\nTitle: {title.group(1).strip()}\n\n{body}"))
    else:
        hn = sections.get('Hacker News', '')
        title = re.search(r'^Title:\s*(.+)$', hn, re.MULTILINE)
        comment_idx = hn.find('First comment')
        if not (title and comment_idx >= 0):
            raise MigrationError(f"{kit.name}: Hacker News section missing title or comment")
        comment = hn[comment_idx:].split(':', 1)[1].strip()
        written.append(('hn.md', f"Title: {title.group(1).strip()}\n\n{comment}"))

    content = post_path.read_text(encoding='utf-8')
    fm, _ = parse_frontmatter(content)
    add_shape = 'shape' not in fm

    if not dry_run:
        for name, text in written:
            surface.write_file(stem, name, text)
        if add_shape:
            post_path.write_text(insert_frontmatter_line(content, f"shape: {shape}"), encoding='utf-8')
        kit.unlink()

    names = ', '.join(n for n, _ in written)
    shape_note = f", shape: {shape} added to post" if add_shape else ''
    return f"{stem}: kit → {names}{shape_note}, {kit.name} removed"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[1])
    parser.add_argument('--dry-run', action='store_true', help='Report without writing')
    args = parser.parse_args()

    config = load_config()
    posts_dir = PROJECT_ROOT / get_stream_config(config, 'posts')['content_dir']

    if args.dry_run:
        print("🔍 DRY RUN - nothing will be written\n")

    failures = 0
    print("Posts")
    for path in sorted(posts_dir.glob('*.mdx')):
        try:
            print(f"  {migrate_post(path, args.dry_run)}")
        except MigrationError as e:
            failures += 1
            print(f"  ❌ {e}")

    print("\nLegacy kits")
    kits = sorted(p for p in surface.SURFACE_ROOT.glob('*.md') if p.name != 'README.md')
    if not kits:
        print("  none")
    for kit in kits:
        try:
            print(f"  {convert_legacy_kit(kit, posts_dir, args.dry_run)}")
        except MigrationError as e:
            failures += 1
            print(f"  ❌ {e}")

    print(f"\n{'Would fail' if args.dry_run else 'Failed'}: {failures}")
    return 1 if failures else 0


if __name__ == '__main__':
    sys.exit(main())
