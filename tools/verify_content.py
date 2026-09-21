#!/usr/bin/env python3
"""
Verify that everything one /create-content run should have produced is
present, in the right place, and within limits.

Every check runs every time and prints one row, so the table has the same
shape on every run and a diff between two runs means something. A check whose
prerequisite is missing reports `skip` with the reason rather than vanishing.

Usage:
    uv run tools/verify_content.py 2026-10-05-my-post
    uv run tools/verify_content.py website/content/posts/2026-10-05-my-post.mdx
    uv run tools/verify_content.py <stem> --only post surface
    uv run tools/verify_content.py <stem> --skip transcript

Groups: transcript post issue surface qc

Exit codes:
    0  no row failed
    1  at least one row failed
    2  usage or configuration error
"""

import argparse
import json
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from functools import cached_property
from pathlib import Path
from typing import Callable, List, Optional, Tuple

sys.path.insert(0, str(Path(__file__).parent.parent))
from lib import surface
from lib.config import (
    load_config,
    get_newsletter_config,
    get_publishing_config,
    get_stream_config,
)
from lib.content import load_entries, parse_entry_date
from lib.frontmatter import FrontmatterError
from lib.issue_checks import (
    BODY_MAX_WORDS as ISSUE_MAX_WORDS,
    BODY_MIN_WORDS as ISSUE_MIN_WORDS,
    DESCRIPTION_MAX,
    DESCRIPTION_MIN,
    SUBJECT_MAX,
    measure_issue,
)
from lib.post_checks import (
    BODY_MIN_WORDS as POST_MIN_WORDS,
    TITLE_MAX,
    TITLE_MIN,
    measure_post,
    strip_all_code,
)
from lib.social_validator import (
    LINKEDIN_HOOK_MAX,
    build_url,
    tweet_length,
    validate_linkedin,
    validate_tweet,
)
from lib.validator import VALID_CATEGORIES

PROJECT_ROOT = Path(__file__).parent.parent
GROUPS = ["transcript", "post", "issue", "surface", "qc"]

PASS, FAIL, WARN, SKIP = "pass", "fail", "warn", "skip"
STATUS_GLYPH = {PASS: "✔ pass", FAIL: "✘ FAIL", WARN: "⚠ warn", SKIP: "– skip"}

STEM_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})-([a-z0-9]+(?:-[a-z0-9]+)*)$")
DASH_RE = re.compile(r"[—–]")
FILLER_RE = re.compile(r"\b(?:um+|uh+|erm+|umm+)\b", re.IGNORECASE)
EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
PHONE_RE = re.compile(r"(?<!\d)(?:\+?1[\s.-]?)?\(?\d{3}\)?[\s.-]\d{3}[\s.-]\d{4}(?!\d)")
URL_RE = re.compile(r"https?://\S+")
TENURE_RE = re.compile(
    r"\b\d{1,2}\+?\s*(?:years|yrs)\b(?:\s+(?:of|in)\b)?|\ba decade of\b|\bdecades of\b",
    re.IGNORECASE,
)
CONSULTING_RE = re.compile(
    r"\bon every engagement\b|\bmy clients?\b|\bteams I advise\b|\bclient engagements?\b"
    r"|\bconsulting (?:work|practice|clients?|engagements?)\b",
    re.IGNORECASE,
)
BANNED_OPENERS = ("every ai vendor", "your team has", "your vp")
SENTENCE_END_RE = re.compile(r"[.!?](?:\s|$)")
POST_KEYS = ["title", "description", "date", "category", "hashtags", "shape"]
ISSUE_KEYS = ["title", "subject", "description", "date"]
SUBREDDITS = {"r/ClaudeAI", "r/ClaudeCode"}
REDDIT_MIN_WORDS, REDDIT_MAX_WORDS = 150, 450
REDDIT_TITLE_MAX = 300
HN_MIN_SENTENCES, HN_MAX_SENTENCES = 2, 6


@dataclass
class Row:
    id: str
    group: str
    owner: str
    check: str
    status: str
    detail: str


class Context:
    """Everything the checks read, parsed once and cached."""

    def __init__(self, stem: str):
        self.stem = stem
        m = STEM_RE.match(stem)
        self.stem_date = datetime.strptime(m.group(1), "%Y-%m-%d").date() if m else None
        self.config = load_config()
        self.domain = self.config.get("domain", "agentic-engineer.com")
        self.url = build_url(stem, self.domain)
        self.posts_dir = PROJECT_ROOT / get_stream_config(self.config, "posts")["content_dir"]
        self.issues_dir = PROJECT_ROOT / get_stream_config(self.config, "newsletter")["content_dir"]
        self.images_dir = PROJECT_ROOT / get_stream_config(self.config, "posts")["images_dir"] / stem
        self.transcript_path = PROJECT_ROOT / "transcripts" / f"{stem}.md"
        self.post_path = self.posts_dir / f"{stem}.mdx"
        self.issue_path = self.issues_dir / f"{stem}.mdx"
        self.kit_dir = surface.kit_dir(stem)
        self.publishing = get_publishing_config(self.config, "posts")
        self.newsletter = get_newsletter_config(self.config)

    # --- transcript ---
    @cached_property
    def transcript(self) -> Optional[str]:
        if not self.transcript_path.is_file():
            return None
        return self.transcript_path.read_text(encoding="utf-8")

    # --- post ---
    @cached_property
    def post(self):
        """PostMetrics, or an Exception instance describing why not."""
        try:
            return measure_post(self.post_path)
        except (FileNotFoundError, FrontmatterError) as e:
            return e

    @property
    def post_ok(self) -> bool:
        return not isinstance(self.post, Exception)

    @property
    def shape(self) -> Optional[str]:
        if not self.post_ok:
            return None
        value = self.post.frontmatter.get("shape")
        return str(value) if value else None

    # --- issue ---
    @cached_property
    def issue(self):
        try:
            return measure_issue(self.issue_path)
        except (FileNotFoundError, ValueError, FrontmatterError) as e:
            return e

    @property
    def issue_ok(self) -> bool:
        return not isinstance(self.issue, Exception)

    # --- surface ---
    def kit(self, name: str) -> Optional[str]:
        return surface.read_file(self.stem, name)

    # --- vale ---
    @cached_property
    def vale_available(self) -> Tuple[bool, str]:
        if shutil.which("vale") is None:
            return False, "vale not on PATH"
        styles = PROJECT_ROOT / ".vale" / "styles"
        if not styles.is_dir() or not any(p.is_dir() for p in styles.iterdir()):
            return False, "run vale sync"
        return True, ""

    def vale(self, path: Path) -> Tuple[str, str]:
        """(status, detail) for one file's prose lint."""
        ok, why = self.vale_available
        if not ok:
            return SKIP, why
        if not path.is_file():
            return SKIP, "file missing"
        try:
            proc = subprocess.run(
                ["vale", "--ext=.md", "--output=JSON"],
                input=path.read_text(encoding="utf-8"),
                capture_output=True, text=True, cwd=PROJECT_ROOT, timeout=120,
            )
        except (OSError, subprocess.TimeoutExpired) as e:
            return SKIP, f"vale did not run: {e}"
        try:
            report = json.loads(proc.stdout or "{}")
        except json.JSONDecodeError:
            return SKIP, f"vale output unreadable: {(proc.stderr or proc.stdout).strip()[:80]}"
        alerts = [a for alerts in report.values() for a in alerts]
        errors = [a for a in alerts if a.get("Severity") == "error"]
        warnings = [a for a in alerts if a.get("Severity") == "warning"]
        if errors:
            first = errors[0]
            return FAIL, (f"{len(errors)} error(s); first at line {first.get('Line')}: "
                          f"{first.get('Message', '')[:70]}")
        if warnings:
            return WARN, f"0 errors, {len(warnings)} warning(s)"
        return PASS, f"0 errors, {len(alerts)} suggestion(s)"

    # --- send_issue dry run ---
    @cached_property
    def send_issue(self) -> Optional[subprocess.CompletedProcess]:
        if not self.issue_ok or self.issue.send_date is None:
            return None
        date = self.issue.send_date.strftime("%Y-%m-%d")
        try:
            return subprocess.run(
                [sys.executable, "tools/send_issue.py", "--dry-run", "--date", date],
                capture_output=True, text=True, cwd=PROJECT_ROOT, timeout=120,
            )
        except (OSError, subprocess.TimeoutExpired):
            return None


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _need_post(ctx: Context):
    """Skip detail when the post is unusable, else None."""
    if not ctx.post_ok:
        return SKIP, "post missing or unparseable"
    return None


def _need_issue(ctx: Context):
    if not ctx.issue_ok:
        return SKIP, "issue missing or unparseable"
    return None


def _need_transcript(ctx: Context):
    if ctx.transcript is None:
        return SKIP, "transcript missing"
    return None


def _need_kit(ctx: Context, name: str):
    text = ctx.kit(name)
    if text is None:
        return None, (SKIP, f"{name} missing")
    return text, None


def _dash_report(text: str) -> Tuple[str, str]:
    hits = [(n, line) for n, line in enumerate(text.splitlines(), 1) if DASH_RE.search(line)]
    if not hits:
        return PASS, "none"
    n, line = hits[0]
    return FAIL, f"{len(hits)} line(s); first at line {n}: {line.strip()[:60]}"


def _regex_report(text: str, pattern: re.Pattern, label: str) -> Tuple[str, str]:
    hits = pattern.findall(text)
    if not hits:
        return PASS, "none"
    first = hits[0] if isinstance(hits[0], str) else hits[0][0]
    return FAIL, f"{len(hits)} {label}; first: {str(first).strip()[:50]!r}"


def _expected_post_datetime(ctx: Context) -> Optional[datetime]:
    if ctx.stem_date is None:
        return None
    t = str(ctx.publishing.get("time", "11:00:00"))
    return datetime.combine(ctx.stem_date, datetime.strptime(t, "%H:%M:%S").time())


def _fm_datetime(value) -> Optional[datetime]:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.replace(tzinfo=None)
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00")).replace(tzinfo=None)
    except ValueError:
        return None


def _words(text: str) -> int:
    return len(re.findall(r"\b\w+\b", text))


# ---------------------------------------------------------------------------
# transcript
# ---------------------------------------------------------------------------

def t1(ctx):
    if ctx.transcript is None:
        return FAIL, f"{ctx.transcript_path.relative_to(PROJECT_ROOT)} missing"
    if not ctx.transcript.strip():
        return FAIL, "file is empty"
    return PASS, f"{_words(ctx.transcript):,} words"


def t2(ctx):
    if (skip := _need_transcript(ctx)):
        return skip
    n = _words(ctx.transcript)
    return (PASS if n >= 200 else FAIL), f"{n} words (min 200)"


def t3(ctx):
    if (skip := _need_transcript(ctx)):
        return skip
    return _regex_report(ctx.transcript, FILLER_RE, "filler word(s)")


def t4(ctx):
    if (skip := _need_transcript(ctx)):
        return skip
    return _dash_report(ctx.transcript)


def t5(ctx):
    if (skip := _need_transcript(ctx)):
        return skip
    emails = EMAIL_RE.findall(ctx.transcript)
    phones = PHONE_RE.findall(ctx.transcript)
    if not emails and not phones:
        return PASS, "no emails or phone numbers"
    sample = (emails or phones)[0]
    return FAIL, f"{len(emails)} email(s), {len(phones)} phone(s); first: {sample}"


# ---------------------------------------------------------------------------
# post
# ---------------------------------------------------------------------------

def p1(ctx):
    if not ctx.post_path.is_file():
        return FAIL, f"{ctx.post_path.relative_to(PROJECT_ROOT)} missing"
    if not ctx.post_ok:
        return FAIL, f"unparseable: {str(ctx.post).splitlines()[0][:70]}"
    return PASS, ctx.post_path.name


def p2(ctx):
    if (skip := _need_post(ctx)):
        return skip
    keys = list(ctx.post.frontmatter.keys())
    missing = [k for k in POST_KEYS if k not in keys]
    extra = [k for k in keys if k not in POST_KEYS]
    if not missing and not extra:
        return PASS, ", ".join(POST_KEYS)
    parts = []
    if missing:
        parts.append(f"missing {', '.join(missing)}")
    if extra:
        parts.append(f"unexpected {', '.join(extra)}")
    return FAIL, "; ".join(parts)


def p3(ctx):
    if (skip := _need_post(ctx)):
        return skip
    expected = _expected_post_datetime(ctx)
    if expected is None:
        return FAIL, "stem is not YYYY-MM-DD-slug"
    actual = _fm_datetime(ctx.post.frontmatter.get("date"))
    if actual is None:
        return FAIL, f"date unparseable: {ctx.post.frontmatter.get('date')!r}"
    if actual != expected:
        return FAIL, f"{actual.isoformat()} != {expected.isoformat()}"
    return PASS, f"{expected.isoformat()}Z"


def p4(ctx):
    if (skip := _need_post(ctx)):
        return skip
    cat = ctx.post.category
    return (PASS if cat in VALID_CATEGORIES else FAIL), cat or "missing"


def p5(ctx):
    if (skip := _need_post(ctx)):
        return skip
    shape = ctx.shape
    if shape in surface.SHAPES:
        return PASS, shape
    return FAIL, f"{shape!r}; expected one of {', '.join(surface.SHAPES)}"


def p6(ctx):
    if (skip := _need_post(ctx)):
        return skip
    if "social" in ctx.post.frontmatter:
        return FAIL, "social: block present; copy belongs in surface/<stem>/"
    return PASS, "no social: block"


def p7(ctx):
    if (skip := _need_post(ctx)):
        return skip
    n = ctx.post.title_len
    return (PASS if TITLE_MIN <= n <= TITLE_MAX else FAIL), f"{n} chars ({TITLE_MIN}-{TITLE_MAX})"


def p8(ctx):
    if (skip := _need_post(ctx)):
        return skip
    n = ctx.post.description_len
    return (PASS if DESCRIPTION_MIN <= n <= DESCRIPTION_MAX else FAIL), f"{n} chars ({DESCRIPTION_MIN}-{DESCRIPTION_MAX})"


def p9(ctx):
    if not ctx.images_dir.is_dir():
        return FAIL, f"{ctx.images_dir.relative_to(PROJECT_ROOT)}/ missing"
    heroes = sorted(ctx.images_dir.glob("hero-*.webp"))
    if not heroes:
        return FAIL, "no hero-*.webp in the image directory"
    return PASS, heroes[0].name


def p10(ctx):
    if (skip := _need_post(ctx)):
        return skip
    refs = ctx.post.resolved_images
    if not refs:
        return FAIL, "no image references in the body"
    bad = [(src, path) for src, path, exists in refs if not exists]
    not_webp = [src for src, _, _ in refs if not src.lower().endswith(".webp")]
    if bad:
        return FAIL, f"{len(bad)} unresolved; first: {bad[0][0]}"
    if not_webp:
        return FAIL, f"{len(not_webp)} not .webp; first: {not_webp[0]}"
    return PASS, f"{len(refs)} image(s) resolve"


def p11(ctx):
    if (skip := _need_post(ctx)):
        return skip
    if not ctx.post.images:
        return SKIP, "no images"
    missing = ctx.post.images_missing_alt
    return (PASS if missing == 0 else FAIL), f"{missing} of {len(ctx.post.images)} missing alt text"


def p12(ctx):
    if (skip := _need_post(ctx)):
        return skip
    m = ctx.post
    if len(m.h1_headings) > 1:
        return FAIL, f"{len(m.h1_headings)} H1 headings"
    if m.heading_skip:
        a, b = m.heading_skip
        return FAIL, f"level skip H{a} → H{b}"
    return PASS, f"{len(m.headings)} headings, {len(m.h1_headings)} H1"


def p13(ctx):
    if (skip := _need_post(ctx)):
        return skip
    n = ctx.post.word_count
    return (PASS if n >= POST_MIN_WORDS else FAIL), f"{n:,} words (min {POST_MIN_WORDS})"


def p14(ctx):
    if (skip := _need_post(ctx)):
        return skip
    return _dash_report(strip_all_code(ctx.post.body))


def p15(ctx):
    if (skip := _need_post(ctx)):
        return skip
    return _regex_report(strip_all_code(ctx.post.body), TENURE_RE, "tenure claim(s)")


def p16(ctx):
    if (skip := _need_post(ctx)):
        return skip
    return _regex_report(strip_all_code(ctx.post.body), CONSULTING_RE, "consulting phrase(s)")


def p17(ctx):
    if (skip := _need_post(ctx)):
        return skip
    return ctx.vale(ctx.post_path)


def p18(ctx):
    if (skip := _need_post(ctx)):
        return skip
    m = ctx.post
    if not m.links:
        return WARN, "no links"
    return PASS, f"{len(m.internal_links)} internal, {len(m.external_links)} external"


# ---------------------------------------------------------------------------
# issue
# ---------------------------------------------------------------------------

def i1(ctx):
    if not ctx.issue_path.is_file():
        return FAIL, f"{ctx.issue_path.relative_to(PROJECT_ROOT)} missing"
    if not ctx.issue_ok:
        return FAIL, f"unparseable: {str(ctx.issue).splitlines()[0][:70]}"
    return PASS, ctx.issue_path.name


def i2(ctx):
    if (skip := _need_issue(ctx)):
        return skip
    fm = ctx.issue.frontmatter
    missing = [k for k in ISSUE_KEYS if not fm.get(k)]
    stray = [k for k in ("category", "hashtags", "social") if k in fm]
    if not missing and not stray:
        return PASS, ", ".join(ISSUE_KEYS) + (", archive_date" if "archive_date" in fm else "")
    parts = []
    if missing:
        parts.append(f"missing {', '.join(missing)}")
    if stray:
        parts.append(f"unexpected {', '.join(stray)}")
    return FAIL, "; ".join(parts)


def i3(ctx):
    if (skip := _need_issue(ctx)):
        return skip
    if ctx.issue.send_date is None:
        return FAIL, "issue date unparseable"
    if not ctx.post_ok:
        return SKIP, "post missing; cannot compare"
    post_date = _fm_datetime(ctx.post.frontmatter.get("date"))
    if post_date is None:
        return SKIP, "post date unparseable"
    if ctx.issue.send_date != post_date:
        return FAIL, f"issue {ctx.issue.send_date.isoformat()} != post {post_date.isoformat()}"
    return PASS, ctx.issue.send_date.isoformat() + "Z"


def i4(ctx):
    if (skip := _need_issue(ctx)):
        return skip
    n = len(ctx.issue.subject)
    if n == 0:
        return FAIL, "missing"
    return (PASS if n <= SUBJECT_MAX else FAIL), f"{n} chars (max {SUBJECT_MAX})"


def i5(ctx):
    if (skip := _need_issue(ctx)):
        return skip
    n = len(ctx.issue.description)
    return (PASS if DESCRIPTION_MIN <= n <= DESCRIPTION_MAX else FAIL), f"{n} chars ({DESCRIPTION_MIN}-{DESCRIPTION_MAX})"


def i6(ctx):
    if (skip := _need_issue(ctx)):
        return skip
    m = ctx.issue
    if m.archive_date_error:
        return FAIL, m.archive_date_error
    if m.archive_date is None:
        return PASS, f"defaults to +{ctx.newsletter['archive_delay_days']} days"
    if m.send_date and m.archive_date <= m.send_date:
        return FAIL, f"archive {m.archive_date:%Y-%m-%d} not after send {m.send_date:%Y-%m-%d}"
    gap = (m.archive_date - m.send_date).days if m.send_date else None
    return PASS, f"+{gap} days" if gap is not None else m.archive_date.isoformat()


def i7(ctx):
    if (skip := _need_issue(ctx)):
        return skip
    n = ctx.issue.word_count
    ok = ISSUE_MIN_WORDS <= n <= ISSUE_MAX_WORDS
    return (PASS if ok else FAIL), f"{n} words ({ISSUE_MIN_WORDS}-{ISSUE_MAX_WORDS})"


def i8(ctx):
    if (skip := _need_issue(ctx)):
        return skip
    return (PASS if ctx.issue.has_code_block else FAIL), ("present" if ctx.issue.has_code_block else "no fenced code block")


def i9(ctx):
    if (skip := _need_issue(ctx)):
        return skip
    return (FAIL if ctx.issue.has_local_image else PASS), ("local image reference" if ctx.issue.has_local_image else "none")


def i10(ctx):
    if (skip := _need_issue(ctx)):
        return skip
    return _dash_report(strip_all_code(ctx.issue.body))


def i11(ctx):
    if (skip := _need_issue(ctx)):
        return skip
    text = strip_all_code(ctx.issue.body)
    status, detail = _regex_report(text, TENURE_RE, "tenure claim(s)")
    if status == FAIL:
        return status, detail
    return _regex_report(text, CONSULTING_RE, "consulting phrase(s)")


def i12(ctx):
    if (skip := _need_issue(ctx)):
        return skip
    return ctx.vale(ctx.issue_path)


def i13(ctx):
    if (skip := _need_issue(ctx)):
        return skip
    proc = ctx.send_issue
    if proc is None:
        return SKIP, "send_issue.py did not run"
    if proc.returncode != 0:
        tail = (proc.stderr or proc.stdout).strip().splitlines()
        return FAIL, f"exit {proc.returncode}: {tail[-1][:70] if tail else ''}"
    out = proc.stdout
    if ctx.post_ok and ctx.post.title and ctx.post.title not in out:
        return FAIL, "post title not in the composed email"
    relative = re.findall(r"\]\((?:/|\.\./)[^)]*\)", out)
    if relative:
        return FAIL, f"{len(relative)} relative link(s); first {relative[0][:50]}"
    return PASS, "composes; post attached; links absolute"


# ---------------------------------------------------------------------------
# surface
# ---------------------------------------------------------------------------

def s1(ctx):
    if not ctx.kit_dir.is_dir():
        return FAIL, f"{ctx.kit_dir.relative_to(PROJECT_ROOT)}/ missing"
    files = sorted(p.name for p in ctx.kit_dir.iterdir() if p.is_file())
    return PASS, ", ".join(files) or "empty"


def s2(ctx):
    text, skip = _need_kit(ctx, "x.md")
    if skip:
        return skip
    issues = validate_tweet(text)
    errors = [i for i in issues if i.severity == "error"]
    if errors:
        return FAIL, errors[0].message
    status, detail = _dash_report(text)
    if status == FAIL:
        return FAIL, f"em dash: {detail}"
    lowered = text.lower()
    if lowered.startswith(BANNED_OPENERS) or (not text[0].isalnum() and "?" in text.splitlines()[0]):
        return FAIL, f"banned opener: {text.splitlines()[0][:50]!r}"
    billed = tweet_length(text) + 25
    return PASS, f"text {tweet_length(text)} + 25 = {billed} / 280"


def s3(ctx):
    text, skip = _need_kit(ctx, "linkedin.md")
    if skip:
        return skip
    issues = validate_linkedin(text)
    errors = [i for i in issues if i.severity == "error"]
    if errors:
        return FAIL, errors[0].message
    status, detail = _dash_report(text)
    if status == FAIL:
        return FAIL, f"em dash: {detail}"
    warnings = [i for i in issues if i.severity == "warning"]
    hook = len(text.splitlines()[0])
    if warnings:
        return WARN, warnings[0].message
    return PASS, f"{len(text)} / 3000 chars, hook {hook} / {LINKEDIN_HOOK_MAX}"


def s4(ctx):
    shape = ctx.shape
    if shape not in surface.SHAPES:
        return SKIP, "post shape unknown"
    wanted = surface.platform_file(shape)
    other = surface.platform_file("claim" if shape == "tutorial" else "tutorial")
    have = ctx.kit(wanted) is not None
    stray = (ctx.kit_dir / other).is_file()
    if have and not stray:
        return PASS, f"{wanted} for {shape}"
    parts = []
    if not have:
        parts.append(f"{wanted} missing")
    if stray:
        parts.append(f"{other} present but shape is {shape}")
    return FAIL, "; ".join(parts)


def _parse_hn(text: str):
    lines = text.splitlines()
    title = lines[0][len("Title:"):].strip() if lines and lines[0].startswith("Title:") else None
    comment = "\n".join(lines[1:]).strip()
    return title, comment


def s5(ctx):
    if ctx.shape == "tutorial":
        return SKIP, "tutorial post; no hn.md expected"
    text, skip = _need_kit(ctx, "hn.md")
    if skip:
        return skip
    title, comment = _parse_hn(text)
    if title is None:
        return FAIL, "first line must be `Title: <post title>`"
    if ctx.post_ok and title != ctx.post.title:
        return FAIL, f"title differs from post: {title[:50]!r}"
    if not comment:
        return FAIL, "author comment missing"
    if "upvote" in comment.lower():
        return FAIL, "comment asks for votes"
    sentences = len(SENTENCE_END_RE.findall(comment))
    if not HN_MIN_SENTENCES <= sentences <= HN_MAX_SENTENCES:
        return FAIL, f"comment is {sentences} sentence(s) ({HN_MIN_SENTENCES}-{HN_MAX_SENTENCES})"
    return PASS, f"title matches, {sentences}-sentence comment"


def _parse_reddit(text: str):
    lines = text.splitlines()
    sub = title = None
    idx = 0
    for idx, line in enumerate(lines[:3]):
        if line.startswith("Subreddit:"):
            sub = line[len("Subreddit:"):].strip()
        elif line.startswith("Title:"):
            title = line[len("Title:"):].strip()
        else:
            break
    else:
        idx += 1
    body = "\n".join(lines[idx:]).strip()
    return sub, title, body


def s6(ctx):
    if ctx.shape == "claim":
        return SKIP, "claim post; no reddit.md expected"
    text, skip = _need_kit(ctx, "reddit.md")
    if skip:
        return skip
    sub, title, body = _parse_reddit(text)
    if sub not in SUBREDDITS:
        return FAIL, f"Subreddit: {sub!r}; expected one of {', '.join(sorted(SUBREDDITS))}"
    if not title:
        return FAIL, "Title: line missing"
    if len(title) > REDDIT_TITLE_MAX:
        return FAIL, f"title {len(title)} chars (max {REDDIT_TITLE_MAX})"
    words = _words(body)
    if not REDDIT_MIN_WORDS <= words <= REDDIT_MAX_WORDS:
        return FAIL, f"body {words} words ({REDDIT_MIN_WORDS}-{REDDIT_MAX_WORDS})"
    if not body.rstrip().endswith(ctx.url):
        return FAIL, "body does not end with the post URL"
    return PASS, f"{sub}, body {words} words, ends with URL"


def s7(ctx):
    if not ctx.kit_dir.is_dir():
        return SKIP, "kit directory missing"
    stray = surface.unexpected_files(ctx.stem, ctx.shape)
    if stray:
        return FAIL, f"unexpected: {', '.join(stray)}"
    return PASS, "only expected files"


def s8(ctx):
    if not ctx.kit_dir.is_dir():
        return SKIP, "kit directory missing"
    for name in surface.KNOWN_FILES:
        text = ctx.kit(name)
        if text is None:
            continue
        for pattern, label in ((TENURE_RE, "tenure claim"), (CONSULTING_RE, "consulting phrase")):
            hit = pattern.search(text)
            if hit:
                return FAIL, f"{name}: {label} {hit.group(0)!r}"
    return PASS, "none"


# ---------------------------------------------------------------------------
# qc
# ---------------------------------------------------------------------------

def q1(ctx):
    if ctx.images_dir.is_dir():
        n = sum(1 for p in ctx.images_dir.iterdir() if p.is_file())
        return PASS, f"{ctx.images_dir.relative_to(PROJECT_ROOT)}/ ({n} file(s))"
    return FAIL, f"{ctx.images_dir.relative_to(PROJECT_ROOT)}/ missing"


def q2(ctx):
    if ctx.stem_date is None:
        return SKIP, "stem is not dated"
    clashes = []
    for directory, label in ((ctx.posts_dir, "post"), (ctx.issues_dir, "issue")):
        for path, _, _, entry_date in load_entries(directory):
            if entry_date == ctx.stem_date and path.stem != ctx.stem:
                clashes.append(f"{label} {path.name}")
    if clashes:
        return FAIL, "; ".join(clashes)
    return PASS, f"only this post and issue on {ctx.stem_date}"


def q3(ctx):
    if ctx.stem_date is None:
        return SKIP, "stem is not dated"
    pub = ctx.publishing
    if pub.get("frequency") != "weekly":
        return SKIP, f"{pub.get('frequency')} cadence not checked"
    day = ctx.stem_date.strftime("%A").lower()
    days = [d.lower() for d in pub.get("days", [])]
    if day in days:
        return PASS, f"{ctx.stem_date} is a {day.capitalize()}"
    return FAIL, f"{ctx.stem_date} is a {day.capitalize()}; publish days: {', '.join(days)}"


def q4(ctx):
    try:
        proc = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True, text=True, cwd=PROJECT_ROOT, timeout=30,
        )
    except (OSError, subprocess.TimeoutExpired) as e:
        return SKIP, f"git not available: {e}"
    if proc.returncode != 0:
        return SKIP, "not a git repository"
    expected = (
        f"transcripts/{ctx.stem}.md",
        str(ctx.post_path.relative_to(PROJECT_ROOT)),
        str(ctx.images_dir.relative_to(PROJECT_ROOT)) + "/",
        str(ctx.issue_path.relative_to(PROJECT_ROOT)),
        str(ctx.kit_dir.relative_to(PROJECT_ROOT)) + "/",
    )
    other = []
    for line in proc.stdout.splitlines():
        path = line[3:].strip().strip('"')
        if not path.startswith(expected):
            other.append(path)
    if other:
        return WARN, f"{len(other)} other change(s); first: {other[0]}"
    return PASS, "only this post's files are modified"


# ---------------------------------------------------------------------------
# registry
# ---------------------------------------------------------------------------

CHECKS: List[Tuple[str, str, str, str, Callable]] = [
    # id, group, owner, label, fn
    ("T1", "transcript", "orchestrator", "transcript exists", t1),
    ("T2", "transcript", "orchestrator", "transcript length", t2),
    ("T3", "transcript", "orchestrator", "no filler words", t3),
    ("T4", "transcript", "orchestrator", "no em or en dashes", t4),
    ("T5", "transcript", "orchestrator", "no emails or phone numbers", t5),
    ("P1", "post", "blog-writer", "post exists and parses", p1),
    ("P2", "post", "blog-writer", "frontmatter keys exact", p2),
    ("P3", "post", "blog-writer", "date matches stem and publish time", p3),
    ("P4", "post", "blog-writer", "category valid", p4),
    ("P5", "post", "blog-writer", "shape is tutorial or claim", p5),
    ("P6", "post", "blog-writer", "no social: block", p6),
    ("P7", "post", "blog-writer", "title length", p7),
    ("P8", "post", "blog-writer", "description length", p8),
    ("P9", "post", "blog-writer", "hero-*.webp present", p9),
    ("P10", "post", "blog-writer", "image references resolve", p10),
    ("P11", "post", "blog-writer", "images have alt text", p11),
    ("P12", "post", "blog-writer", "heading structure", p12),
    ("P13", "post", "blog-writer", "body length", p13),
    ("P14", "post", "blog-writer", "no em or en dashes in prose", p14),
    ("P15", "post", "blog-writer", "no tenure claims", p15),
    ("P16", "post", "blog-writer", "no consulting language", p16),
    ("P17", "post", "blog-writer", "vale prose lint", p17),
    ("P18", "post", "blog-writer", "links present", p18),
    ("I1", "issue", "newsletter-writer", "issue exists and parses", i1),
    ("I2", "issue", "newsletter-writer", "frontmatter keys", i2),
    ("I3", "issue", "newsletter-writer", "date matches post", i3),
    ("I4", "issue", "newsletter-writer", "subject length", i4),
    ("I5", "issue", "newsletter-writer", "description length", i5),
    ("I6", "issue", "newsletter-writer", "archive_date after date", i6),
    ("I7", "issue", "newsletter-writer", "body length", i7),
    ("I8", "issue", "newsletter-writer", "pasteable code block", i8),
    ("I9", "issue", "newsletter-writer", "no local images", i9),
    ("I10", "issue", "newsletter-writer", "no em or en dashes in prose", i10),
    ("I11", "issue", "newsletter-writer", "no tenure or consulting language", i11),
    ("I12", "issue", "newsletter-writer", "vale prose lint", i12),
    ("I13", "issue", "newsletter-writer", "email composes (send_issue --dry-run)", i13),
    ("S1", "surface", "orchestrator", "kit directory exists", s1),
    ("S2", "surface", "x-writer", "x.md within budget, no URL", s2),
    ("S3", "surface", "linkedin-writer", "linkedin.md within limits, hook line", s3),
    ("S4", "surface", "linkedin-writer", "platform file matches shape", s4),
    ("S5", "surface", "linkedin-writer", "hn.md title and comment", s5),
    ("S6", "surface", "linkedin-writer", "reddit.md subreddit, title, body, URL", s6),
    ("S7", "surface", "social-qc", "no unexpected files", s7),
    ("S8", "surface", "linkedin-writer", "no tenure or consulting language", s8),
    ("Q1", "qc", "orchestrator", "image directory for stem", q1),
    ("Q2", "qc", "orchestrator", "no other entry on that date", q2),
    ("Q3", "qc", "orchestrator", "date is a publish day", q3),
    ("Q4", "qc", "orchestrator", "working tree holds only this post", q4),
]


def run(stem: str, groups: List[str]) -> List[Row]:
    ctx = Context(stem)
    rows = []
    for check_id, group, owner, label, fn in CHECKS:
        if group not in groups:
            rows.append(Row(check_id, group, owner, label, SKIP, "not selected"))
            continue
        try:
            status, detail = fn(ctx)
        except Exception as e:  # one broken check must not hide the rest
            status, detail = FAIL, f"check crashed: {type(e).__name__}: {str(e)[:60]}"
        rows.append(Row(check_id, group, owner, label, status, detail))
    return rows


def render(stem: str, rows: List[Row]) -> str:
    widths = (4, 8, 11, 18, 40)
    header = f"{'ID':<{widths[0]}} {'Status':<{widths[1]}} {'Group':<{widths[2]}} {'Owner':<{widths[3]}} {'Check':<{widths[4]}} Detail"
    out = [f"verify_content  {stem}", header]
    for r in rows:
        out.append(
            f"{r.id:<{widths[0]}} {STATUS_GLYPH[r.status]:<{widths[1]}} {r.group:<{widths[2]}} "
            f"{r.owner:<{widths[3]}} {r.check:<{widths[4]}} {r.detail}"
        )
    out.append("─" * 100)
    counts = {s: sum(1 for r in rows if r.status == s) for s in (PASS, FAIL, WARN, SKIP)}
    out.append(
        f"{len(rows)} checks: {counts[PASS]} passed, {counts[FAIL]} failed, "
        f"{counts[WARN]} warned, {counts[SKIP]} skipped"
    )
    failed_by_owner = {}
    for r in rows:
        if r.status == FAIL:
            failed_by_owner.setdefault(r.owner, []).append(r.id)
    if failed_by_owner:
        out.append("RE-RUN: " + ", ".join(
            f"{owner} ({', '.join(ids)})" for owner, ids in failed_by_owner.items()
        ))
    else:
        out.append("RE-RUN: none")
    return "\n".join(out)


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify one post's full artifact set")
    parser.add_argument("stem", help="YYYY-MM-DD-slug, or a path to the post .mdx")
    parser.add_argument("--only", nargs="+", choices=GROUPS, metavar="GROUP",
                        help="run only these groups")
    parser.add_argument("--skip", nargs="+", choices=GROUPS, metavar="GROUP",
                        help="skip these groups")
    args = parser.parse_args()

    stem = Path(args.stem).stem if args.stem.endswith(".mdx") or "/" in args.stem else args.stem
    if not STEM_RE.match(stem):
        print(f"❌ {stem!r} is not a YYYY-MM-DD-slug stem", file=sys.stderr)
        return 2

    groups = list(args.only) if args.only else list(GROUPS)
    for g in args.skip or []:
        if g in groups:
            groups.remove(g)

    try:
        rows = run(stem, groups)
    except Exception as e:
        print(f"❌ Could not start verification: {e}", file=sys.stderr)
        return 2

    print(render(stem, rows))
    return 1 if any(r.status == FAIL for r in rows) else 0


if __name__ == "__main__":
    sys.exit(main())
