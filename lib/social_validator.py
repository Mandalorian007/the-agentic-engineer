"""Social media post validator.

Validates social media posts in frontmatter against platform requirements.
"""

from typing import Any


# Platform character limits (total including URL)
TWITTER_TOTAL_MAX = 280  # Twitter's hard limit
LINKEDIN_TOTAL_MAX = 3000  # LinkedIn's hard limit


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


def build_url(slug: str, domain: str = "the-agentic-engineer.com") -> str:
    """Build full blog URL from slug.

    Args:
        slug: Post slug (filename without .mdx)
        domain: Blog domain

    Returns:
        Full URL
    """
    return f"https://{domain}/blog/{slug}"


def validate_social_posts(
    frontmatter: dict[str, Any], slug: str, domain: str = "the-agentic-engineer.com"
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
    url_overhead = len(url) + 2  # \n\n before URL

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
            total_length = text_length + url_overhead

            if total_length > TWITTER_TOTAL_MAX:
                issues.append(
                    ValidationIssue(
                        "twitter",
                        "error",
                        f"Total tweet length is {total_length} chars (text: {text_length}, URL: {url_overhead}), max is {TWITTER_TOTAL_MAX}",
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
