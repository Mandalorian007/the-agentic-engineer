"""Newsletter issue measurements and checks.

`measure_issue` collects the facts; `analyze_issue` turns them into the
errors, warnings and informational lines that `tools/issue_check.py` prints
and `tools/verify_content.py` renders as rows.
"""

import re
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional, Tuple

from lib.frontmatter import parse_frontmatter, FrontmatterError

PROJECT_ROOT = Path(__file__).parent.parent

# Most email clients truncate subject lines past roughly this length.
SUBJECT_MAX = 50
DESCRIPTION_MIN = 150
DESCRIPTION_MAX = 160
# An issue is a TLDR, not an essay: the target is ~350 words. Shorter than the
# minimum and it is a note; longer than the maximum and a segment is restating
# itself, or the idea wants to be a blog post.
BODY_MIN_WORDS = 200
BODY_MAX_WORDS = 500

REQUIRED_FIELDS = ['title', 'subject', 'description', 'date']
LOCAL_IMAGE_MARKER = '](../../public/'


def parse_date(value) -> datetime:
    """Parse an ISO 8601 frontmatter date, tolerating the trailing Z."""
    if isinstance(value, datetime):
        return value.replace(tzinfo=None)
    text = str(value).strip().replace('Z', '+00:00')
    return datetime.fromisoformat(text).replace(tzinfo=None)


@dataclass
class IssueMetrics:
    path: Path
    frontmatter: dict
    body: str
    subject: str
    description: str
    send_date: Optional[datetime]
    send_date_error: Optional[str]
    archive_date: Optional[datetime]
    archive_date_error: Optional[str]
    word_count: int
    has_local_image: bool
    has_code_block: bool

    @property
    def missing_fields(self) -> List[str]:
        return [f for f in REQUIRED_FIELDS if not self.frontmatter.get(f)]


def measure_issue(issue_path: Path) -> IssueMetrics:
    """
    Parse an issue and collect every measurement the checks use.

    Raises:
        FileNotFoundError, ValueError (wrong suffix), FrontmatterError
    """
    if not issue_path.exists():
        raise FileNotFoundError(issue_path)
    if issue_path.suffix != '.mdx':
        raise ValueError(f"Expected a .mdx file, got {issue_path.suffix}")

    frontmatter, body = parse_frontmatter(issue_path.read_text(encoding='utf-8'))

    send_date = send_err = None
    if frontmatter.get('date'):
        try:
            send_date = parse_date(frontmatter['date'])
        except ValueError:
            send_err = f"Invalid date: {frontmatter['date']!r} (expected ISO 8601)"

    archive_date = archive_err = None
    if frontmatter.get('archive_date'):
        try:
            archive_date = parse_date(frontmatter['archive_date'])
        except ValueError:
            archive_err = f"Invalid archive_date: {frontmatter['archive_date']!r} (expected ISO 8601)"

    return IssueMetrics(
        path=issue_path,
        frontmatter=frontmatter,
        body=body,
        subject=str(frontmatter.get('subject', '') or ''),
        description=str(frontmatter.get('description', '') or ''),
        send_date=send_date,
        send_date_error=send_err,
        archive_date=archive_date,
        archive_date_error=archive_err,
        word_count=len(body.split()),
        has_local_image=LOCAL_IMAGE_MARKER in body,
        has_code_block='```' in body,
    )


def analyze_issue(issue_path: Path, archive_delay_days: int) -> Tuple[List[str], List[str], List[str]]:
    """
    Check one issue file.

    Returns:
        (errors, warnings, info) as lists of strings. `info` holds the
        measurement lines the CLI prints before the verdicts.
    """
    errors: List[str] = []
    warnings: List[str] = []
    info: List[str] = []

    try:
        m = measure_issue(issue_path)
    except FileNotFoundError:
        return [f"File not found: {issue_path}"], [], []
    except ValueError as e:
        return [str(e)], [], []
    except (OSError, FrontmatterError) as e:
        return [f"Could not parse frontmatter: {e}"], [], []

    for field in m.missing_fields:
        errors.append(f"Missing required frontmatter field: {field}")

    if m.subject:
        if len(m.subject) > SUBJECT_MAX:
            warnings.append(
                f"Subject is {len(m.subject)} chars, over {SUBJECT_MAX}. "
                f"Most clients will truncate it."
            )
        else:
            info.append(f"  Subject: {len(m.subject)}/{SUBJECT_MAX} chars")

    if m.description:
        d = len(m.description)
        if d < DESCRIPTION_MIN:
            warnings.append(
                f"Description is {d} chars, under {DESCRIPTION_MIN}. "
                f"Aim for {DESCRIPTION_MIN}-{DESCRIPTION_MAX}."
            )
        elif d > DESCRIPTION_MAX:
            warnings.append(
                f"Description is {d} chars, over {DESCRIPTION_MAX}. "
                f"Search results will cut it off."
            )
        else:
            info.append(f"  Description: {d}/{DESCRIPTION_MAX} chars")

    if m.send_date_error:
        errors.append(m.send_date_error)

    if m.archive_date_error:
        errors.append(m.archive_date_error)
    elif m.archive_date is not None:
        if m.send_date and m.archive_date <= m.send_date:
            errors.append(
                f"archive_date ({m.archive_date:%Y-%m-%d}) must be after "
                f"date ({m.send_date:%Y-%m-%d}). Otherwise the archive page "
                f"goes public before subscribers get the email."
            )
        elif m.send_date:
            info.append(f"  Archive delay: {(m.archive_date - m.send_date).days} days")
    elif m.send_date:
        default = m.send_date + timedelta(days=archive_delay_days)
        info.append(f"  Archive delay: {archive_delay_days} days (default) "
                    f"-> {default:%Y-%m-%d}")

    if m.word_count < BODY_MIN_WORDS:
        warnings.append(
            f"Body is {m.word_count} words, under {BODY_MIN_WORDS}. "
            f"Thin for an issue. Target is ~350."
        )
    elif m.word_count > BODY_MAX_WORDS:
        warnings.append(
            f"Body is {m.word_count} words, over {BODY_MAX_WORDS}. "
            f"Target is ~350. Look for a segment that restates itself."
        )
    else:
        info.append(f"  Body: {m.word_count} words")

    if m.has_local_image:
        errors.append(
            "Issue references a local image. Issues carry no image directory; "
            "images belong in the blog post."
        )

    if not m.has_code_block:
        warnings.append(
            "No code block found. Every issue should carry one pasteable artifact."
        )

    if 'category' in m.frontmatter:
        warnings.append(
            "`category` is set but issues are not part of the blog taxonomy. Remove it."
        )

    return errors, warnings, info


# The website cannot read blog-config.yaml at build time, so the archive delay
# is stated in two places. Nothing links them, and a change to one silently
# leaves the site holding issues back for a different number of days than the
# tooling reports.
ISSUES_TS = PROJECT_ROOT / "website" / "lib" / "issues.ts"
_DELAY_RE = re.compile(r"DEFAULT_ARCHIVE_DELAY_DAYS\s*=\s*(\d+)")


def check_archive_delay_agreement(config_delay: int) -> List[str]:
    """Warn when blog-config.yaml and website/lib/issues.ts disagree."""
    if not ISSUES_TS.exists():
        return []

    match = _DELAY_RE.search(ISSUES_TS.read_text())
    if not match:
        return [f"Could not find DEFAULT_ARCHIVE_DELAY_DAYS in {ISSUES_TS}"]

    site_delay = int(match.group(1))
    if site_delay != config_delay:
        return [
            f"Archive delay mismatch: blog-config.yaml says {config_delay} days, "
            f"{ISSUES_TS} says {site_delay}. The site is what readers get."
        ]
    return []
