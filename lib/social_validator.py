"""Social media post validator.

Validates the per-outlet text files in `surface/<stem>/` against platform
limits. `validate_social_posts` still reads the old frontmatter `social:`
block for posts that have not been migrated.
"""

import re
from typing import Any


# Platform character limits (total including URL)
TWITTER_TOTAL_MAX = 280  # Twitter's hard limit
LINKEDIN_TOTAL_MAX = 3000  # LinkedIn's hard limit
# LinkedIn collapses a post with an image to roughly this many characters
# before "…see more", so the first line has to earn the click on its own.
LINKEDIN_HOOK_MAX = 150

_URL_RE = re.compile(r"https?://\S+")

# X rewrites every link through t.co and counts it as a fixed width, whatever
# the real URL is. Counting the literal URL instead makes the budget depend on
# the length of the domain and the slug, which is both wrong and needlessly
# strict: moving the canonical host from the apex to www put six already-good
# tweets "over" a limit they were never near. Published as
# `short_url_length_https` in the API's help/configuration response; it has
# been 23 for years.
TCO_URL_LENGTH = 23


class ValidationIssue:
    """Represents a validation issue."""

    def __init__(self, platform: str, severity: str, message: str):
        self.platform = platform
        self.severity = severity  # 'error' or 'warning'
        self.message = message

    def __str__(self):
        emoji = "❌" if self.severity == "error" else "⚠️"
        return f"{emoji} [{self.platform}] {self.message}"

    def __repr__(self):
        return f"ValidationIssue({self.platform!r}, {self.severity!r}, {self.message!r})"


def build_url(slug: str, domain: str = "agentic-engineer.com") -> str:
    """Build full blog URL from slug.

    Args:
        slug: Post slug (filename without .mdx)
        domain: Blog domain

    Returns:
        Full URL
    """
    return f"https://{domain}/blog/{slug}"


def tweet_length(text: str) -> int:
    """Length of a tweet as X counts it, with every URL billed at t.co width."""
    without_urls = _URL_RE.sub("", text)
    url_count = len(_URL_RE.findall(text))
    return len(without_urls) + url_count * TCO_URL_LENGTH


def validate_tweet(text: str) -> list[ValidationIssue]:
    """
    Check the bare tweet text from `surface/<stem>/x.md`.

    The posting script appends "\\n\\n<url>", so the budget is 280 minus the
    t.co width and the separator. The text itself must carry no URL.
    """
    issues = []
    text = (text or "").strip()

    if not text:
        return [ValidationIssue("twitter", "error", "x.md is empty")]

    if _URL_RE.search(text):
        issues.append(ValidationIssue(
            "twitter", "error",
            "x.md must not contain a URL; the posting script appends the post link",
        ))

    billed = tweet_length(text) + 2 + TCO_URL_LENGTH
    if billed > TWITTER_TOTAL_MAX:
        issues.append(ValidationIssue(
            "twitter", "error",
            f"Tweet bills at {billed} chars (text {tweet_length(text)} + "
            f"{2 + TCO_URL_LENGTH} for the link), max is {TWITTER_TOTAL_MAX}",
        ))

    return issues


def validate_linkedin(text: str) -> list[ValidationIssue]:
    """
    Check the bare LinkedIn text from `surface/<stem>/linkedin.md`.

    The URL goes in the first comment, not the body, so the full limit is
    available to the text. A URL in the body is a warning rather than an error
    because LinkedIn still accepts it; it just buries the post.
    """
    issues = []
    text = (text or "").strip()

    if not text:
        return [ValidationIssue("linkedin", "error", "linkedin.md is empty")]

    if len(text) > LINKEDIN_TOTAL_MAX:
        issues.append(ValidationIssue(
            "linkedin", "error",
            f"Post is {len(text)} chars, max is {LINKEDIN_TOTAL_MAX}",
        ))

    hook = text.splitlines()[0]
    if len(hook) > LINKEDIN_HOOK_MAX:
        issues.append(ValidationIssue(
            "linkedin", "warning",
            f"First line is {len(hook)} chars; the feed collapses past "
            f"{LINKEDIN_HOOK_MAX}, so the hook is cut off",
        ))

    if _URL_RE.search(text):
        issues.append(ValidationIssue(
            "linkedin", "warning",
            "Body contains a URL; put the link in the first comment instead",
        ))

    return issues


def validate_social_posts(
    frontmatter: dict[str, Any], slug: str, domain: str = "agentic-engineer.com"
) -> list[ValidationIssue]:
    """Validate social media posts in frontmatter.

    Args:
        frontmatter: Parsed frontmatter dictionary
        slug: Post slug (for URL calculation)
        domain: Blog domain (for URL calculation)

    Returns:
        List of validation issues (empty if valid)
    """
    issues = []

    # Build the actual URL that will be appended
    url = build_url(slug, domain)
    # LinkedIn posts the URL as written, so it costs what it measures.
    url_overhead = len(url) + 2  # \n\n before URL
    # X shortens it first, so only the t.co width is charged.
    tco_overhead = TCO_URL_LENGTH + 2

    # Check if social field exists
    if "social" not in frontmatter:
        issues.append(
            ValidationIssue(
                "general",
                "warning",
                "No social media posts defined. Run /generate-socials to add them.",
            )
        )
        return issues

    social = frontmatter["social"]

    # Social must be a dictionary
    if not isinstance(social, dict):
        issues.append(
            ValidationIssue(
                "general", "error", "social field must be a dictionary, not a string"
            )
        )
        return issues

    # Validate Twitter
    if "twitter" in social:
        twitter = social["twitter"]
        if not isinstance(twitter, dict):
            issues.append(
                ValidationIssue(
                    "twitter", "error", "twitter field must be a dictionary"
                )
            )
        elif "text" not in twitter:
            issues.append(
                ValidationIssue("twitter", "error", "twitter.text field is required")
            )
        elif not isinstance(twitter["text"], str):
            issues.append(
                ValidationIssue("twitter", "error", "twitter.text must be a string")
            )
        elif not twitter["text"].strip():
            issues.append(
                ValidationIssue("twitter", "error", "twitter.text cannot be empty")
            )
        else:
            # Calculate total length with actual URL
            text_length = len(twitter["text"])
            total_length = text_length + tco_overhead

            if total_length > TWITTER_TOTAL_MAX:
                issues.append(
                    ValidationIssue(
                        "twitter",
                        "error",
                        f"Total tweet length is {total_length} chars (text: {text_length}, t.co URL: {tco_overhead}), max is {TWITTER_TOTAL_MAX}",
                    )
                )

    # Validate LinkedIn
    if "linkedin" in social:
        linkedin = social["linkedin"]
        if not isinstance(linkedin, dict):
            issues.append(
                ValidationIssue(
                    "linkedin", "error", "linkedin field must be a dictionary"
                )
            )
        elif "text" not in linkedin:
            issues.append(
                ValidationIssue("linkedin", "error", "linkedin.text field is required")
            )
        elif not isinstance(linkedin["text"], str):
            issues.append(
                ValidationIssue("linkedin", "error", "linkedin.text must be a string")
            )
        elif not linkedin["text"].strip():
            issues.append(
                ValidationIssue("linkedin", "error", "linkedin.text cannot be empty")
            )
        else:
            # Calculate total length with actual URL
            text_length = len(linkedin["text"])
            total_length = text_length + url_overhead

            if total_length > LINKEDIN_TOTAL_MAX:
                issues.append(
                    ValidationIssue(
                        "linkedin",
                        "error",
                        f"Total post length is {total_length} chars (text: {text_length}, URL: {url_overhead}), max is {LINKEDIN_TOTAL_MAX}",
                    )
                )

    # Warn if no platforms defined
    if not any(platform in social for platform in ["twitter", "linkedin"]):
        issues.append(
            ValidationIssue(
                "general",
                "warning",
                "No platforms defined in social field. Add twitter and/or linkedin.",
            )
        )

    return issues


def print_validation_results(issues: list[ValidationIssue]) -> None:
    """Print validation results in a user-friendly format.

    Args:
        issues: List of validation issues
    """
    if not issues:
        print("✅ Social media posts are valid")
        return

    errors = [i for i in issues if i.severity == "error"]
    warnings = [i for i in issues if i.severity == "warning"]

    if errors:
        print("Social Media Validation Errors:")
        for issue in errors:
            print(f"  {issue}")

    if warnings:
        print("\nSocial Media Validation Warnings:")
        for issue in warnings:
            print(f"  {issue}")

    if errors:
        print(f"\n❌ Found {len(errors)} error(s) - fix before publishing")
    elif warnings:
        print(f"\n⚠️  Found {len(warnings)} warning(s) - consider addressing")
