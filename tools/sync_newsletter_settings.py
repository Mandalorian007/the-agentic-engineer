#!/usr/bin/env python3
"""Push newsletter settings from the repo to Buttondown.

The repo is the source of truth for anything with copy in it. Buttondown's
web UI is the only other place these strings live, and drift between the two
is invisible until a subscriber gets the wrong email, so this pushes rather
than compares.

Syncs two things:

- The identity fields from `newsletter/buttondown-settings.md`: newsletter
  name, from name, reply-to address, description. These are writable on the
  free plan, and they are what a subscriber actually sees in the inbox.
- The welcome email (`newsletter/welcome-email.md`), which Buttondown calls the
  "subscription confirmed" transactional email. It fires once, after someone
  clicks the link in the double opt-in confirmation.

Requires BUTTONDOWN_NEWSLETTER_KEY, which is *not* the same key the website
uses. The site's key only needs to create subscribers; writing newsletter
settings needs the newsletter-scoped key, which the narrower key cannot do
(it returns 403 on every PATCH). Keeping them separate is deliberate: a leak
of the public-facing key cannot rewrite your transactional emails.

The welcome email is gated on the free plan:

    403 custom_transactional_emails, required_plan: standard

That is a billing gate, not a bug. It is reported and skipped rather than
failing the run, so the identity fields still land. Everything else here is
free-tier writable.

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
SETTINGS_PATH = REPO_ROOT / "newsletter" / "buttondown-settings.md"

# Buttondown field name -> the `## heading` above its fenced block in
# buttondown-settings.md. The file is written for a person to read, so the
# headings carry the explanation and this maps them back to the API.
SETTINGS_FIELDS = {
    "name": "Newsletter name",
    "from_name": 'Author (the "From" name in the inbox)',
    "reply_to_address": "Reply-to address",
    "description": "Description",
}
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


def parse_settings(path: Path) -> dict[str, str]:
    """Pull the identity fields out of the human-readable settings file.

    Each value lives in the first fenced block under its own `## heading`.
    Headings are matched exactly: the file also *discusses* these fields in
    prose, and a looser match picks up the commentary instead of the value.
    """
    raw = path.read_text()
    values: dict[str, str] = {}

    for field, heading in SETTINGS_FIELDS.items():
        pattern = (
            r"^## " + re.escape(heading) + r"[ \t]*$"
            r".*?"
            r"^```[a-z]*[ \t]*$\n(.*?)^```[ \t]*$"
        )
        match = re.search(pattern, raw, re.MULTILINE | re.DOTALL)
        if not match:
            raise SystemExit(f"{path.name}: no fenced block under '## {heading}'")
        values[field] = match.group(1).strip()

    return values


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
    parser.add_argument(
        "--force-description",
        action="store_true",
        help="Also rewrite the description, which cannot be compared remotely",
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
    settings = parse_settings(SETTINGS_PATH)

    session = requests.Session()
    session.headers.update(
        {"Authorization": f"Token {key}", "Content-Type": "application/json"}
    )

    newsletter = get_newsletter(session)
    print(f"Newsletter: {newsletter['name']}")

    # Identity fields. Buttondown stores `description` as rendered HTML, so it
    # never round-trips back to the markdown that produced it and is written
    # unconditionally rather than compared.
    comparable = {k: v for k, v in settings.items() if k != "description"}
    drift = {
        field: (newsletter.get(field, ""), value)
        for field, value in comparable.items()
        if newsletter.get(field, "") != value
    }

    print("\nIdentity fields")
    for field, value in comparable.items():
        if field in drift:
            print(f"  {field:18} {drift[field][0]!r} -> {value!r}")
        else:
            print(f"  {field:18} in sync")
    print(f"  {'description':18} write-only (stored as HTML)")

    print("\nWelcome email")
    welcome_synced = (
        newsletter.get("custom_subscription_confirmed_email_subject", "") == subject
        and newsletter.get("custom_subscription_confirmed_email_text", "") == body
    )
    print(f"  subject            {subject!r}")
    print(f"  body               {len(body)} chars, "
          f"{'in sync' if welcome_synced else 'differs'}")

    if args.dry_run:
        print("\nDry run, nothing written.")
        return 0

    exit_code = 0

    if drift or args.force_description:
        payload = dict(settings) if args.force_description else {
            field: settings[field] for field in drift
        }
        response = session.patch(
            f"{API_BASE}/newsletters/{newsletter['id']}", json=payload, timeout=15
        )
        if not response.ok:
            print(f"\nIdentity fields failed: {response.status_code} "
                  f"{response.text[:300]}", file=sys.stderr)
            exit_code = 1
        else:
            # Buttondown normalises some fields on write, so confirm what landed
            # rather than trusting the 200.
            stored = response.json()
            bad = [f for f in payload if f != "description" and stored.get(f) != payload[f]]
            if bad:
                print(f"\nWrote, but these came back different: {bad}", file=sys.stderr)
                exit_code = 1
            else:
                print(f"\nIdentity fields written: {sorted(payload)}")
    else:
        print("\nIdentity fields already in sync.")

    if welcome_synced:
        print("Welcome email already in sync.")
        return exit_code

    response = session.patch(
        f"{API_BASE}/newsletters/{newsletter['id']}",
        json={
            "custom_subscription_confirmed_email_subject": subject,
            "custom_subscription_confirmed_email_text": body,
        },
        timeout=15,
    )

    if response.status_code == 403:
        # Expected on the free plan. Reported, not fatal: the identity fields
        # above are the part that actually reaches a subscriber today.
        print("Welcome email skipped: needs the Standard plan "
              "(403 custom_transactional_emails).")
        return exit_code

    if not response.ok:
        print(f"Welcome email failed: {response.status_code} "
              f"{response.text[:300]}", file=sys.stderr)
        return 1

    updated = response.json()
    if (updated.get("custom_subscription_confirmed_email_subject", "") != subject
            or updated.get("custom_subscription_confirmed_email_text", "") != body):
        print("Welcome email wrote, but the stored value differs from the file.",
              file=sys.stderr)
        return 1

    print("Welcome email written.")
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
