"""Blog post measurements and the SEO analysis built on them.

`measure_post` gathers every fact the checks need in one pass so that
`tools/seo_check.py` (human report) and `tools/verify_content.py` (row table)
agree on the numbers. `analyze_post` reproduces the seo_check report as a list
of printable findings plus an exit code.
"""

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Tuple

from lib.frontmatter import parse_frontmatter, FrontmatterError
from lib.validator import VALID_CATEGORIES

TITLE_MIN, TITLE_MAX = 30, 60
DESCRIPTION_MIN, DESCRIPTION_MAX = 150, 160
BODY_MIN_WORDS = 300

_CODE_BLOCK_RE = re.compile(r'```.*?```', re.DOTALL)
_INLINE_CODE_RE = re.compile(r'`[^`\n]*`')
_IMAGE_RE = re.compile(r'!\[(.*?)\]\((.+?)\)')
_LINK_RE = re.compile(r'\[([^\]]+)\]\(([^\)]+)\)')
_HEADING_RE = re.compile(r'^(#{1,6}) (.+)$', re.MULTILINE)
_H1_RE = re.compile(r'^# (.+)$', re.MULTILINE)
_STEM_RE = re.compile(r'\d{4}-\d{2}-\d{2}-(.+)')


@dataclass
class PostMetrics:
    path: Path
    frontmatter: dict
    body: str
    title: str
    description: str
    category: str
    h1_headings: List[str]
    headings: List[Tuple[int, str]]
    heading_skip: Optional[Tuple[int, int]]
    word_count: int
    images: List[Tuple[str, str]]              # (alt, src)
    image_dir: Optional[Path]
    hero_images: List[Path]
    resolved_images: List[Tuple[str, Path, bool]]   # (src, resolved path, exists)
    links: List[Tuple[str, str]]
    internal_links: List[Tuple[str, str]] = field(default_factory=list)
    external_links: List[Tuple[str, str]] = field(default_factory=list)

    @property
    def title_len(self) -> int:
        return len(self.title)

    @property
    def description_len(self) -> int:
        return len(self.description)

    @property
    def images_missing_alt(self) -> int:
        return sum(1 for alt, _ in self.images if not alt)

    @property
    def stem_is_dated(self) -> bool:
        return bool(_STEM_RE.match(self.path.stem))


def strip_code(body: str) -> str:
    """Body without fenced code blocks."""
    return _CODE_BLOCK_RE.sub('', body)


def strip_all_code(body: str) -> str:
    """Body without fenced blocks or inline code, for prose-only checks."""
    return _INLINE_CODE_RE.sub('', strip_code(body))


def image_dir_for(post_path: Path) -> Optional[Path]:
    """`website/public/blog/<stem>` for a post under `website/content/posts`."""
    if not _STEM_RE.match(post_path.stem):
        return None
    website_root = post_path.resolve().parent.parent.parent
    return website_root / "public" / "blog" / post_path.stem


def measure_post(post_path: Path) -> PostMetrics:
    """
    Parse a post and collect every measurement the checks use.

    Raises:
        FileNotFoundError: the file does not exist
        FrontmatterError: the frontmatter does not parse
    """
    if not post_path.exists():
        raise FileNotFoundError(post_path)

    content = post_path.read_text(encoding='utf-8')
    frontmatter, body = parse_frontmatter(content)

    body_no_code = strip_code(body)

    h1_headings = _H1_RE.findall(body_no_code)
    headings = [(len(h), text) for h, text in _HEADING_RE.findall(body_no_code)]
    heading_skip = None
    levels = [level for level, _ in headings]
    for i in range(1, len(levels)):
        if levels[i] - levels[i - 1] > 1:
            heading_skip = (levels[i - 1], levels[i])
            break

    word_count = len(re.findall(r'\b\w+\b', body_no_code))

    images = _IMAGE_RE.findall(body)
    image_dir = image_dir_for(post_path)
    hero_images = sorted(image_dir.glob("hero-*.webp")) if image_dir and image_dir.exists() else []

    resolved = []
    for _, src in images:
        if src.startswith(('http://', 'https://')):
            continue
        target = (post_path.resolve().parent / src).resolve()
        resolved.append((src, target, target.is_file()))

    links = [l for l in _LINK_RE.findall(body) if not l[1].startswith('!')]
    internal = [l for l in links if not l[1].startswith('http')]
    external = [l for l in links if l[1].startswith('http')]

    return PostMetrics(
        path=post_path,
        frontmatter=frontmatter,
        body=body,
        title=str(frontmatter.get('title', '') or ''),
        description=str(frontmatter.get('description', '') or ''),
        category=str(frontmatter.get('category', '') or ''),
        h1_headings=h1_headings,
        headings=headings,
        heading_skip=heading_skip,
        word_count=word_count,
        images=images,
        image_dir=image_dir,
        hero_images=hero_images,
        resolved_images=resolved,
        links=links,
        internal_links=internal,
        external_links=external,
    )


@dataclass
class Finding:
    level: str      # success | error | warning | info
    text: str


def analyze_post(post_path: Path) -> Tuple[List[Finding], List[str], List[str], int]:
    """
    The seo_check report, as data.

    Returns:
        (findings, issues, warnings, exit_code). `findings` are the lines the
        report prints in order; `issues` and `warnings` are the summary lists.
    """
    findings: List[Finding] = []
    issues: List[str] = []
    warnings: List[str] = []

    try:
        m = measure_post(post_path)
    except FileNotFoundError:
        return [Finding('error', f"File not found: {post_path}")], [], [], 1
    except FrontmatterError as e:
        return [Finding('error', f"Failed to parse frontmatter: {e}")], [], [], 1

    # 1. Title length
    if TITLE_MIN <= m.title_len <= TITLE_MAX:
        findings.append(Finding('success', f"Title length: {m.title_len} characters (optimal: {TITLE_MIN}-{TITLE_MAX})"))
    elif m.title_len < TITLE_MIN:
        findings.append(Finding('warning', f"Title length: {m.title_len} characters (too short, recommend {TITLE_MIN}-{TITLE_MAX})"))
        warnings.append(f"Title is only {m.title_len} chars - consider making it more descriptive")
    else:
        findings.append(Finding('error', f"Title length: {m.title_len} characters (too long, recommend {TITLE_MIN}-{TITLE_MAX})"))
        issues.append(f"Title is {m.title_len} chars - Google may truncate it in search results")

    # 2. Meta description
    if m.description:
        d = m.description_len
        if DESCRIPTION_MIN <= d <= DESCRIPTION_MAX:
            findings.append(Finding('success', f"Meta description: {d} characters (optimal: {DESCRIPTION_MIN}-{DESCRIPTION_MAX})"))
        elif d < DESCRIPTION_MIN:
            findings.append(Finding('warning', f"Meta description: {d} characters (short, recommend {DESCRIPTION_MIN}-{DESCRIPTION_MAX})"))
            warnings.append(f"Description could be more detailed ({d} chars)")
        else:
            findings.append(Finding('error', f"Meta description: {d} characters (too long, recommend {DESCRIPTION_MIN}-{DESCRIPTION_MAX})"))
            issues.append(f"Description is {d} chars - Google may truncate it")
    else:
        findings.append(Finding('error', "No meta description in frontmatter"))
        issues.append(f"REQUIRED: Add 'description' field to frontmatter ({DESCRIPTION_MIN}-{DESCRIPTION_MAX} chars)")

    # 3. Category
    if m.category:
        if m.category in VALID_CATEGORIES:
            findings.append(Finding('success', f"Category: '{m.category}' (valid)"))
        else:
            findings.append(Finding('error', f"Category: '{m.category}' (invalid)"))
            issues.append(f"Invalid category '{m.category}'. Must be one of: {', '.join(VALID_CATEGORIES)}")
    else:
        findings.append(Finding('error', "No category in frontmatter"))
        issues.append(f"REQUIRED: Add 'category' field. Valid options: {', '.join(VALID_CATEGORIES)}")

    # 4. Heading structure
    if len(m.h1_headings) == 1:
        findings.append(Finding('success', f"Single H1 heading: '{m.h1_headings[0][:50]}...'"))
    elif len(m.h1_headings) == 0:
        if m.title:
            findings.append(Finding('success', "H1 heading: Using frontmatter title (recommended for blog posts)"))
        else:
            findings.append(Finding('error', "No H1 heading found in content"))
            issues.append("Add a single H1 (#) heading to your content or a title in frontmatter")
    else:
        findings.append(Finding('error', f"Multiple H1 headings found: {len(m.h1_headings)}"))
        issues.append("Use only one H1 heading per page")

    if m.headings:
        findings.append(Finding('success', f"Total headings: {len(m.headings)}"))
        if m.heading_skip:
            a, b = m.heading_skip
            findings.append(Finding('warning', f"Heading hierarchy skip detected (H{a} → H{b})"))
            warnings.append("Maintain proper heading hierarchy (don't skip levels)")

    # 5. Content length
    if m.word_count >= BODY_MIN_WORDS:
        findings.append(Finding('success', f"Word count: {m.word_count} words (minimum {BODY_MIN_WORDS} recommended)"))
    else:
        findings.append(Finding('warning', f"Word count: {m.word_count} words (below {BODY_MIN_WORDS} minimum)"))
        warnings.append(f"Content is short ({m.word_count} words) - aim for {BODY_MIN_WORDS}+ for better SEO")

    # 6. Image alt text
    if m.images:
        missing = m.images_missing_alt
        if missing == 0:
            findings.append(Finding('success', f"All {len(m.images)} images have alt text"))
        else:
            findings.append(Finding('warning', f"{missing}/{len(m.images)} images missing alt text"))
            warnings.append(f"Add descriptive alt text to {missing} image(s)")
    else:
        findings.append(Finding('info', "No images found"))

    # 7. Hero image
    if m.image_dir is not None:
        if m.image_dir.exists():
            if m.hero_images:
                findings.append(Finding('success', f"Hero image found: {m.hero_images[0].name} (for social media previews)"))
            else:
                findings.append(Finding('error', "No hero image found (hero-*.webp)"))
                issues.append(f"REQUIRED: Add hero-*.webp image to public/blog/{m.path.stem}/ for Open Graph/Twitter Card previews")
        else:
            findings.append(Finding('error', f"Image directory not found: public/blog/{m.path.stem}"))
            issues.append(f"Create image directory: public/blog/{m.path.stem}")
    else:
        findings.append(Finding('warning', "Cannot validate hero image - filename doesn't match YYYY-MM-DD-slug.mdx format"))

    # 8. Links
    if m.links:
        findings.append(Finding('success', f"Links: {len(m.internal_links)} internal, {len(m.external_links)} external"))
    else:
        findings.append(Finding('warning', "No links found"))
        warnings.append("Consider adding relevant internal/external links")

    return findings, issues, warnings, (1 if issues else 0)
