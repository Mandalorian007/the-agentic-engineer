"""Configuration loading and validation for Next.js blog"""

import yaml
from dotenv import load_dotenv
from pathlib import Path
from typing import Dict, Any


class ConfigError(Exception):
    """Configuration errors"""
    pass


def load_config() -> Dict[str, Any]:
    """
    Load configuration from blog-config.yaml and .env.local

    Returns:
        Complete configuration dict with all settings

    Raises:
        ConfigError: If configuration is invalid or missing
    """
    # Load environment variables from .env.local (optional now)
    env_path = Path('.env.local')
    if env_path.exists():
        load_dotenv(env_path)

    # Load YAML configuration
    config_path = Path('blog-config.yaml')
    if not config_path.exists():
        raise ConfigError(
            "❌ blog-config.yaml not found\n"
            "Create blog-config.yaml in project root."
        )

    try:
        with open(config_path) as f:
            config = yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise ConfigError(f"❌ Invalid YAML in blog-config.yaml: {e}")

    # Validate configuration
    validate_config(config)

    return config


def validate_config(config: Dict[str, Any]) -> None:
    """
    Validate configuration has all required fields

    Args:
        config: Configuration dict to validate

    Raises:
        ConfigError: If required fields are missing or invalid
    """
    # Required top-level fields
    required_fields = ['blog_name', 'domain']
    missing = [f for f in required_fields if f not in config or not config[f]]

    if missing:
        raise ConfigError(
            f"❌ Missing required fields in blog-config.yaml: {', '.join(missing)}\n"
            f"Example:\n"
            f"  blog_name: \"The Agentic Engineer\"\n"
            f"  domain: \"agentic-engineer.com\""
        )

    # Validate categories list
    categories = config.get('categories', [])
    expected_categories = [
        'tutorials',
        'case-studies',
        'guides',
        'lists',
        'comparisons',
        'problem-solution',
        'opinions'
    ]

    if set(categories) != set(expected_categories):
        raise ConfigError(
            f"❌ Invalid categories in blog-config.yaml\n"
            f"Expected: {expected_categories}\n"
            f"Found: {categories}"
        )


def get_categories() -> list:
    """
    Get the list of valid categories

    Returns:
        List of valid category slugs
    """
    return [
        'tutorials',
        'case-studies',
        'guides',
        'lists',
        'comparisons',
        'problem-solution',
        'opinions'
    ]


def get_publishing_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get publishing configuration with defaults

    Args:
        config: Configuration dict from load_config()

    Returns:
        Publishing configuration dict with:
        - frequency: "weekly" or "monthly"
        - time: publish time string (e.g., "11:00:00")
        For weekly: days (list of day names)
        For monthly: day (single day name), weeks_of_month (list of ints)

    Note:
        For backwards compatibility, the legacy "week_of_month" (single int)
        is accepted and normalized into "weeks_of_month" (list).
    """
    publishing = config.get('publishing', {})
    frequency = publishing.get('frequency', 'weekly')

    result = {
        'frequency': frequency,
        'time': publishing.get('time', '11:00:00'),
    }

    if frequency == 'monthly':
        result['day'] = publishing.get('day', 'monday')

        if 'weeks_of_month' in publishing:
            weeks = publishing['weeks_of_month']
            if not isinstance(weeks, list) or not weeks:
                raise ConfigError(
                    "❌ publishing.weeks_of_month must be a non-empty list of integers (1-5)"
                )
            result['weeks_of_month'] = sorted(set(int(w) for w in weeks))
        else:
            result['weeks_of_month'] = [publishing.get('week_of_month', 2)]
    else:
        result['days'] = publishing.get('days', ['monday'])

    return result


def get_publishing_rate(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get publishing rate info from configuration.

    Returns:
        Dict with:
        - posts_per_month: float (e.g., 1.0 for monthly, ~4.3 for weekly)
        - frequency_label: str (e.g., "1/month", "1/week")
    """
    pub_config = get_publishing_config(config)
    frequency = pub_config.get('frequency', 'weekly')

    if frequency == 'monthly':
        weeks_count = len(pub_config.get('weeks_of_month', [2]))
        return {
            'posts_per_month': float(weeks_count),
            'frequency_label': f'{weeks_count}/month',
        }
    else:
        days_count = len(pub_config.get('days', ['monday']))
        return {
            'posts_per_month': days_count * 4.33,
            'frequency_label': f'{days_count}/week',
        }


def get_posts_per_week(config: Dict[str, Any]) -> int:
    """
    Calculate posts per week from configuration.

    For monthly frequency, returns 1 (used as a fallback for
    legacy code that expects a weekly number).

    Args:
        config: Configuration dict from load_config()

    Returns:
        Number of posts per week based on configured publish days
    """
    pub_config = get_publishing_config(config)
    if pub_config.get('frequency') == 'monthly':
        return 1
    return len(pub_config.get('days', ['monday']))
