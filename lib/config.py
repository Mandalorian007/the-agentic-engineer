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
        - frequency: "weekly" or "twice-weekly"
        - days: list of day names (e.g., ["monday", "thursday"])
        - time: publish time string (e.g., "10:00:00")
    """
    publishing = config.get('publishing', {})
    return {
        'frequency': publishing.get('frequency', 'weekly'),
        'days': publishing.get('days', ['monday']),
        'time': publishing.get('time', '10:00:00'),
    }


def get_posts_per_week(config: Dict[str, Any]) -> int:
    """
    Calculate posts per week from configuration

    Args:
        config: Configuration dict from load_config()

    Returns:
        Number of posts per week based on configured publish days
    """
    return len(get_publishing_config(config)['days'])
