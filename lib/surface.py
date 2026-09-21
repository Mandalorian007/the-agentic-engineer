"""Surface kit layout: one directory per post holding paste-ready distribution copy.

    surface/<stem>/
      x.md         tweet text only, no URL. post_to_twitter.py appends the link.
      linkedin.md  post text only, no URL. The link goes in the first comment.
      hn.md        `Title: <post title>`, blank line, author comment. Claim posts.
      reddit.md    `Subreddit: r/...`, `Title: ...`, blank line, body ending
                   with the post URL. Tutorial posts.

`<stem>` is the post filename without `.mdx` (`YYYY-MM-DD-slug`). There are
no header lines inside the files; anything a reader needs (title, URL,
shape) comes from the post's frontmatter at notify time.

Posts written before the layout existed carry no `shape` in frontmatter. For
those, only `x.md` and `linkedin.md` are expected.
"""

import shutil
from pathlib import Path
from typing import Optional

PROJECT_ROOT = Path(__file__).parent.parent
SURFACE_ROOT = PROJECT_ROOT / "surface"

BASE_FILES = ["x.md", "linkedin.md"]
PLATFORM_FILES = {"claim": "hn.md", "tutorial": "reddit.md"}
SHAPES = tuple(PLATFORM_FILES)
KNOWN_FILES = BASE_FILES + list(PLATFORM_FILES.values())


def kit_dir(stem: str) -> Path:
    """The directory holding one post's distribution copy."""
    return SURFACE_ROOT / stem


def platform_file(shape: Optional[str]) -> Optional[str]:
    """The outlet file a shape calls for, or None for legacy posts."""
    if shape is None:
        return None
    return PLATFORM_FILES.get(str(shape))


def expected_files(shape: Optional[str]) -> list:
    """Every file a complete kit holds for this shape."""
    files = list(BASE_FILES)
    extra = platform_file(shape)
    if extra:
        files.append(extra)
    return files


def missing_files(stem: str, shape: Optional[str]) -> list:
    """Expected files that are absent or empty."""
    return [
        name for name in expected_files(shape)
        if read_file(stem, name) is None
    ]


def unexpected_files(stem: str, shape: Optional[str]) -> list:
    """Files in the kit that no shape calls for, or that belong to the other shape."""
    directory = kit_dir(stem)
    if not directory.is_dir():
        return []
    allowed = set(expected_files(shape)) if shape else set(KNOWN_FILES)
    return sorted(
        p.name for p in directory.iterdir()
        if p.is_file() and p.name not in allowed
    )


def read_file(stem: str, name: str) -> Optional[str]:
    """Stripped contents of one kit file, or None if absent or empty."""
    path = kit_dir(stem) / name
    if not path.is_file():
        return None
    text = path.read_text(encoding="utf-8").strip()
    return text or None


def read_tweet_text(stem: str) -> Optional[str]:
    return read_file(stem, "x.md")


def write_file(stem: str, name: str, text: str) -> Path:
    """Write one kit file, creating the directory. Normalises to a single trailing newline."""
    directory = kit_dir(stem)
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / name
    path.write_text(text.strip() + "\n", encoding="utf-8")
    return path


def rename_kit(
    old_stem: str,
    new_stem: str,
    old_url: str,
    new_url: str,
    dry_run: bool = False,
) -> list:
    """
    Move a kit to a new stem and rewrite the post URL where the kit carries it.

    Only `reddit.md` embeds the URL (its body ends with the link); the other
    files never contain one. Returns human-readable lines describing what was
    (or would be) done, so callers can print a plan.
    """
    old_dir = kit_dir(old_stem)
    new_dir = kit_dir(new_stem)
    lines = []

    if not old_dir.is_dir():
        return lines

    if new_dir.exists():
        raise FileExistsError(f"Target surface kit already exists: {new_dir}")

    lines.append(f"Rename surface kit: {old_dir.name}/ → {new_dir.name}/")

    reddit = old_dir / "reddit.md"
    rewrite = reddit.is_file() and old_url in reddit.read_text(encoding="utf-8")
    if rewrite:
        lines.append(f"Rewrite URL in {new_dir.name}/reddit.md")

    if dry_run:
        return lines

    shutil.move(str(old_dir), str(new_dir))
    if rewrite:
        target = new_dir / "reddit.md"
        target.write_text(
            target.read_text(encoding="utf-8").replace(old_url, new_url),
            encoding="utf-8",
        )
    return lines
