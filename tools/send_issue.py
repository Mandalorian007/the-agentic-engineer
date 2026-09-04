#!/usr/bin/env python3
"""
Send the newsletter issue scheduled for today to Buttondown.

Runs daily; a no-op on any day without an issue. On publish days it composes the
issue plus the newest post published since the previous issue, and hands it to
Buttondown for immediate delivery.

There is no draft mode. A draft that nobody remembers to press send on is
indistinguishable from a successful run, while the archive clock keeps ticking
and publishes the issue publicly a month later to people who never got it.

The two streams share a cadence but not a dependency. An issue sends whether or
not a post exists, which is the point of keeping them separate: the letter has
to survive a month with no finished tutorial.

Usage:
    uv run tools/send_issue.py                          # send today's issue
    uv run tools/send_issue.py --dry-run                # preview, no network
    uv run tools/send_issue.py --dry-run --date 2026-09-21

Environment Variables:
    BUTTONDOWN_API_KEY: Buttondown API key (required unless --dry-run)
"""

import argparse
import os
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent.parent))
from lib.config import load_config, get_stream_config, get_newsletter_config
from lib.content import (
    get_entry_for_date,
    get_latest_entry_in_window,
    get_previous_entry_date,
)

# Auto-load .env.local if it exists (for local testing)
project_root = Path(__file__).parent.parent
env_file = project_root / ".env.local"
if env_file.exists():
    load_dotenv(env_file)

API_BASE = "https://api.buttondown.com/v1"

# Buttondown's trigger for immediate delivery.
SEND_STATUS = "about_to_send"

# What Buttondown may legitimately report back for an email we asked it to send.
# It moves through this sequence quickly, so the exact value depends on timing.
# "draft" is the one answer that means the send did not take: Buttondown accepts
# the request with a 201 and silently parks the email when an account is not
# cleared to send.
ACCEPTED_SEND_STATUSES = {"about_to_send", "in_flight", "sending", "sent", "scheduled"}

# How far back the very first issue looks for a post to attach. A little over
# one cadence gap (14 days), so the debut issue can carry a post from the
# previous slot without resurrecting a months-old one. The window is half-open
# at the start, so an exact 14 would exclude a post sitting on that slot.
FIRST_ISSUE_LOOKBACK_DAYS = 16


# Fenced blocks and inline spans, kept as delimiters by re.split so the code we
# publish passes through untouched.
_CODE_RE = re.compile(
    r"(^```.*?^```$|^~~~.*?^~~~$|``[^`]+``|`[^`\n]+`)",
    re.DOTALL | re.MULTILINE,
)

# A markdown link or image target, and a link reference definition.
_LINK_RE = re.compile(r"(!?\]\()(/|\.\./\.\./public/)")
_DEFINITION_RE = re.compile(r"^(\s{0,3}\[[^\]]+\]:\s+)(/)", re.MULTILINE)
_HTML_ATTR_RE = re.compile(r"""((?:href|src)\s*=\s*["'])(/)""", re.IGNORECASE)


def absolutize(markdown: str, domain: str) -> str:
    """
    Make every path absolute, without touching code.

    An inbox has no site context, so a relative link is simply dead. But a blind
    string replace would also rewrite the example code in the issue, and on this
    blog the pasteable artifact is most of the point: issue_check.py warns when
    an issue has no code block, so every issue has one.

    This is the same reasoning the RSS feed route follows, which walks the mdast
    to avoid exactly this. Splitting on code fences gets there without a parser.
    """
    base = f"https://{domain}"

    def rewrite(text: str) -> str:
        # ](/foo and ](../../public/foo  ->  ](https://domain/foo
        text = _LINK_RE.sub(
            lambda m: m.group(1) + base + "/"
            if m.group(2) == "/"
            else m.group(1) + base + "/",
            text,
        )
        # [ref]: /foo
        text = _DEFINITION_RE.sub(lambda m: m.group(1) + base + "/", text)
        # href="/foo" and src="/foo"
        text = _HTML_ATTR_RE.sub(lambda m: m.group(1) + base + "/", text)
        return text

    # Odd indices are the captured code delimiters; leave them alone.
    parts = _CODE_RE.split(markdown)
    return "".join(
        rewrite(part) if i % 2 == 0 else part for i, part in enumerate(parts)
    )


def compose_body(
    issue_fm: dict,
    issue_body: str,
    post: tuple | None,
    domain: str,
) -> str:
    """
    Build the email body: the issue, then the attached post if there is one.

    Args:
        issue_fm: Issue frontmatter
        issue_body: Issue body markdown (frontmatter already stripped)
        post: (path, frontmatter, body) for the post to attach, or None
        domain: Blog domain

    Returns:
        Markdown ready to POST. Buttondown renders it.
    """
    body = issue_body.strip()

    # Buttondown 400s on a body that opens with a YAML fence. parse_frontmatter
    # has already stripped the real frontmatter, so this only fires when the
    # issue genuinely opens with a horizontal rule.
    if body.startswith("---"):
        body = f"# {issue_fm.get('title', 'Field notes')}\n\n{body}"

    body = absolutize(body, domain)

    if post is not None:
        post_path, post_fm, _ = post
        slug = post_path.stem
        title = post_fm.get("title", slug)
        description = post_fm.get("description", "")
        url = f"https://{domain}/blog/{slug}"

        body += (
            f"\n\n---\n\n"
            f"## New on the blog\n\n"
            f"**{title}**\n\n"
            f"{description}\n\n"
            f"[Read it →]({url})\n"
        )

    return body


def email_exists(api_key: str, subject: str) -> bool:
    """
    Check whether an email with this subject already exists.

    Without this a workflow_dispatch re-run or a retried job sends the issue
    twice. Idempotency matters far more here than it does for a tweet.
    """
    try:
        response = requests.get(
            f"{API_BASE}/emails",
            headers={"Authorization": f"Token {api_key}"},
            timeout=30,
        )
        response.raise_for_status()
        results = response.json().get("results", [])
        return any(email.get("subject") == subject for email in results)
    except requests.exceptions.RequestException as e:
        # Fail closed: if we cannot confirm, do not risk a duplicate send.
        print(f"❌ Could not check for existing emails: {e}", file=sys.stderr)
        raise


def create_email(api_key: str, subject: str, body: str, status: str) -> bool:
    """
    Create the email in Buttondown and confirm what it actually stored.

    A 201 is not proof of a send. Buttondown accepts the request and parks the
    email as a draft when the account is not cleared to send, which would
    otherwise print a success line, exit 0, and leave a green workflow behind an
    email nobody received.
    """
    try:
        response = requests.post(
            f"{API_BASE}/emails",
            headers={
                "Authorization": f"Token {api_key}",
                "Content-Type": "application/json",
            },
            json={"subject": subject, "body": body, "status": status},
            timeout=30,
        )
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        detail = ""
        if e.response is not None:
            detail = f"\n   Response: {e.response.text[:500]}"
        print(f"❌ Failed to create email: {e}{detail}", file=sys.stderr)
        return False

    try:
        created = response.json()
    except ValueError:
        print(
            "❌ Buttondown returned a non-JSON body, cannot confirm the send",
            file=sys.stderr,
        )
        return False

    stored = created.get("status")
    email_id = created.get("id", "unknown")

    if stored not in ACCEPTED_SEND_STATUSES:
        print(
            f"❌ Buttondown stored the email as {stored!r}, not a send.\n"
            f"   Email id: {email_id}\n"
            f"   The most common cause is an account not yet cleared to send. "
            f"Open the dashboard, send it by hand, and check the account status.",
            file=sys.stderr,
        )
        return False

    print(f"   Buttondown id: {email_id} (status: {stored})")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Send today's newsletter issue to Buttondown"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview the composed email without any network calls",
    )
    parser.add_argument(
        "--date",
        help="Target date in YYYY-MM-DD format (defaults to today UTC)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Skip the duplicate-subject check",
    )
    args = parser.parse_args()

    try:
        config = load_config()
        newsletter = get_newsletter_config(config)
    except Exception as e:
        print(f"❌ Error loading configuration: {e}", file=sys.stderr)
        return 1

    if not newsletter["enabled"]:
        print("ℹ️  No `newsletter:` block in blog-config.yaml, nothing to send")
        return 0

    domain = config.get("domain", "agentic-engineer.com")
    status = SEND_STATUS

    if args.date:
        try:
            target_date = datetime.strptime(args.date, "%Y-%m-%d").date()
        except ValueError:
            print(f"❌ Invalid date: {args.date} (expected YYYY-MM-DD)", file=sys.stderr)
            return 1
    else:
        target_date = datetime.now(timezone.utc).date()

    # Find the issue for this date
    issues_dir = get_stream_config(config, "newsletter")["content_dir"]
    issue = get_entry_for_date(issues_dir, target_date)

    if issue is None:
        print(f"ℹ️  No issue scheduled for {target_date}")
        return 0

    issue_path, issue_fm, issue_body = issue
    subject = issue_fm.get("subject") or issue_fm.get("title")

    if not subject:
        print(f"❌ {issue_path.name} has neither `subject` nor `title`", file=sys.stderr)
        return 1

    print(f"📬 Found issue for {target_date}: {issue_path.name}")

    # Attach the newest post the list has not been pointed at yet: anything
    # published since the previous issue went out, up to and including this
    # morning. Same-date matching would strand a post that shipped on a slot
    # with no issue, and "newest post, ever" would re-attach the same stale
    # post every cycle while the blog is quiet.
    #
    # Absent is fine and expected. A field-notes-only issue is the whole reason
    # issues are a separate stream.
    posts_dir = get_stream_config(config, "posts")["content_dir"]
    previous_issue = get_previous_entry_date(issues_dir, target_date)

    if previous_issue is not None:
        window_start = previous_issue
        window_label = f"since the {previous_issue} issue"
    else:
        # First issue ever: there is no "already sent" mark to work from.
        # Look back one cadence gap so the debut does not open with a post
        # from months ago, which reads as a stalled blog rather than a new one.
        window_start = target_date - timedelta(days=FIRST_ISSUE_LOOKBACK_DAYS)
        window_label = f"last {FIRST_ISSUE_LOOKBACK_DAYS} days (first issue)"

    post = get_latest_entry_in_window(posts_dir, window_start, target_date)

    if post is not None:
        print(f"📄 Attaching post: {post[0].name}  ({window_label})")
    else:
        print(f"📄 No post {window_label}, sending the issue alone")

    body = compose_body(issue_fm, issue_body, post, domain)

    if args.dry_run:
        print("\n" + "=" * 60)
        print(f"Subject: {subject}")
        print(f"Status:  {status}")
        print(f"Length:  {len(body):,} chars")
        print("=" * 60)
        print(body)
        print("=" * 60)
        print("\n🔍 DRY RUN - no email created")
        return 0

    api_key = os.environ.get("BUTTONDOWN_API_KEY")
    if not api_key:
        print("❌ BUTTONDOWN_API_KEY is not set", file=sys.stderr)
        return 1

    if not args.force:
        try:
            if email_exists(api_key, subject):
                print(f"ℹ️  An email titled {subject!r} already exists, skipping")
                return 0
        except requests.exceptions.RequestException:
            return 1

    print(f"📤 Creating Buttondown email (status: {status})...")

    if not create_email(api_key, subject, body, status):
        return 1

    print("✅ Email sent.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
