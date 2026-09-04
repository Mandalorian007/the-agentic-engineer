#!/usr/bin/env python3
"""Push newsletter settings from the repo to Buttondown.

The repo is the source of truth for anything with copy in it. Buttondown's
web UI is the only other place these strings live, and drift between the two
is invisible until a subscriber gets the wrong email, so this pushes rather
than compares.

Currently syncs the welcome email (`newsletter/welcome-email.md`), which
Buttondown calls the "subscription confirmed" transactional email. It fires
once, after someone clicks the link in the double opt-in confirmation.

Requires BUTTONDOWN_NEWSLETTER_KEY, which is *not* the same key the website
uses. The site's key only needs to create subscribers; writing newsletter
settings needs the newsletter-scoped key, which the narrower key cannot do
(it returns 403 on every PATCH). Keeping them separate is deliberate: a leak
of the public-facing key cannot rewrite your transactional emails.

Note this currently fails on the free plan:

    403 custom_transactional_emails, required_plan: standard

That is a billing gate, not a bug, and the failure is loud on purpose. The
tool is committed anyway so the copy has a home and one command to ship it if
the add-on is ever bought.

Usage:
    uv run tools/sync_newsletter_settings.py --dry-run
    uv run tools/sync_newsletter_settings.py
"""

import argparse
import os
import re
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parent.parent
WELCOME_PATH = REPO_ROOT / "newsletter" / "welcome-email.md"
API_BASE = "https://api.buttondown.com/v1"


def parse_welcome_email(path: Path) -> tuple[str, str]:
    """Pull subject and body out of the human-readable markdown file.

    The file is written to be read by a person first, so the machine-readable
    parts are marked rather than positional: a line starting with `**Subject:**`
    for the subject, and everything after the last horizontal rule for the body.

    Both markers are anchored to the start of a line. The notes above the copy
    talk *about* those markers, and an unanchored match happily picks the prose
    up instead of the real thing.
    """
    raw = path.read_text()

    match = re.search(r"^\*\*Subject:\*\*[ \t]*(.+)$", raw, re.MULTILINE)
    if not match:
        raise SystemExit(f"{path.name}: no line starting with '**Subject:**'")

    rules = list(re.finditer(r"^---[ \t]*$", raw, re.MULTILINE))
    if len(rules) < 2:
        raise SystemExit(f"{path.name}: expected two '---' rules around the subject")

    body = raw[rules[-1].end():].strip()
    if not body:
        raise SystemExit(f"{path.name}: body is empty")

    return match.group(1).strip(), body


def get_newsletter(session: requests.Session) -> dict:
    response = session.get(f"{API_BASE}/newsletters", timeout=15)
    response.raise_for_status()
    results = response.json().get("results", [])
    if not results:
        raise SystemExit("No newsletter found on this account")
    return results[0]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would change without writing",
    )
    args = parser.parse_args()

    load_dotenv(REPO_ROOT / ".env.local")
    key = os.environ.get("BUTTONDOWN_NEWSLETTER_KEY")
    if not key:
        raise SystemExit(
            "BUTTONDOWN_NEWSLETTER_KEY not set.\n"
            "Find it in the Buttondown API settings, or in the `api_key` field of\n"
            "GET /v1/newsletters. It is not the key the website uses."
        )

    subject, body = parse_welcome_email(WELCOME_PATH)

    session = requests.Session()
    session.headers.update(
        {"Authorization": f"Token {key}", "Content-Type": "application/json"}
    )

    newsletter = get_newsletter(session)
    current_subject = newsletter.get("custom_subscription_confirmed_email_subject", "")
    current_body = newsletter.get("custom_subscription_confirmed_email_text", "")

    unchanged = current_subject == subject and current_body == body

    print(f"Newsletter: {newsletter['name']}")
    print(f"Welcome subject: {subject!r}")
    print(f"Welcome body:    {len(body)} chars")
    print(f"Remote state:    {'already in sync' if unchanged else 'differs'}")

    if args.dry_run:
        print("\nDry run, nothing written.")
        return 0

    if unchanged:
        print("\nNothing to do.")
        return 0

    response = session.patch(
        f"{API_BASE}/newsletters/{newsletter['id']}",
        json={
            "custom_subscription_confirmed_email_subject": subject,
            "custom_subscription_confirmed_email_text": body,
        },
        timeout=15,
    )

    if not response.ok:
        print(f"\nFailed: {response.status_code} {response.text[:500]}", file=sys.stderr)
        return 1

    updated = response.json()
    stored_subject = updated.get("custom_subscription_confirmed_email_subject", "")
    stored_body = updated.get("custom_subscription_confirmed_email_text", "")

    # Buttondown normalises some fields on write, so confirm what landed rather
    # than trusting the 200.
    if stored_subject != subject or stored_body != body:
        print("\nWrote, but the stored value differs from the file:", file=sys.stderr)
        print(f"  subject: {stored_subject!r}", file=sys.stderr)
        print(f"  body:    {len(stored_body)} chars", file=sys.stderr)
        return 1

    print("\nSynced.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
