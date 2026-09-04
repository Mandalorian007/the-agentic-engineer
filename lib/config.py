"""Configuration loading and validation for Next.js blog"""

import yaml
from datetime import date, datetime
from dotenv import load_dotenv
from pathlib import Path
from typing import Dict, Any


class ConfigError(Exception):
    """Configuration errors"""
    pass


# Content streams. Posts and newsletter issues share the same file convention
# (YYYY-MM-DD-slug.mdx) and the same publishing schedule, so nearly every tool
# can work on either one by taking a `stream` argument.
STREAM_DEFAULTS = {
    'posts': {
        'content_dir': 'website/content/posts',
        'images_dir': 'website/public/blog',
        'label': 'Posts',
        'noun': 'post',
        'emoji': '\U0001F4DD',
        'config_key': None,        # paths live at the top level of the config
    },
    'newsletter': {
        'content_dir': 'website/content/issues',
        'images_dir': None,        # issues carry no images
        'label': 'Issues',
        'noun': 'issue',
        'emoji': '\u2709\uFE0F',
        'config_key': 'newsletter',
    },
}


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
            f"  domain: \"www.agentic-engineer.com\""
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

    # Optional newsletter stream. Absent is fine; present must be coherent.
    newsletter = config.get('newsletter')
    if newsletter is not None:
        if not isinstance(newsletter, dict):
            raise ConfigError("❌ blog-config.yaml: `newsletter` must be a mapping")

        # send_mode is gone: issues always send. A draft nobody remembers to
        # press send on looks identical to a successful run, while the archive
        # clock keeps going and publishes it to people who never received it.
        if 'send_mode' in newsletter:
            raise ConfigError(
                "❌ blog-config.yaml: newsletter.send_mode is no longer supported.\n"
                "   Issues always send. Remove the key."
            )

        delay = newsletter.get('archive_delay_days', 30)
        if not isinstance(delay, int) or isinstance(delay, bool) or delay < 0:
            raise ConfigError(
                "❌ blog-config.yaml: newsletter.archive_delay_days must be a "
                "non-negative integer"
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


def get_publishing_config(config: Dict[str, Any], stream: str = 'posts') -> Dict[str, Any]:
    """
    Get publishing configuration with defaults

    Args:
        config: Configuration dict from load_config()

    Returns:
        Publishing configuration dict with:
        - frequency: "weekly", "biweekly" or "monthly"
        - time: publish time string (e.g., "11:00:00")
        For weekly: days (list of day names)
        For biweekly: day (single day name), anchor (YYYY-MM-DD string)
        For monthly: day (single day name), weeks_of_month (list of ints)
    """
    publishing = config.get('publishing', {})

    # The newsletter inherits the blog's schedule unless it explicitly opts out,
    # which is what keeps an issue paired with the post that ships that morning.
    if stream == 'newsletter':
        override = (config.get('newsletter') or {}).get('publishing')
        if override:
            publishing = override

    frequency = publishing.get('frequency', 'weekly')

    result = {
        'frequency': frequency,
        'time': publishing.get('time', '11:00:00'),
    }

    if frequency == 'biweekly':
        result['day'] = publishing.get('day', 'monday')
        anchor = publishing.get('anchor')
        if not anchor:
            raise ConfigError(
                "❌ publishing.anchor is required when frequency is 'biweekly'\n"
                "   Set it to any date already on the cadence:\n"
                '     anchor: "2026-09-07"'
            )
        # YAML turns an unquoted YYYY-MM-DD into a date object. Normalise so
        # every consumer sees the same string regardless of quoting.
        if isinstance(anchor, (date, datetime)):
            anchor = anchor.strftime('%Y-%m-%d')
        result['anchor'] = str(anchor)
    elif frequency == 'monthly':
        result['day'] = publishing.get('day', 'monday')
        weeks = publishing.get('weeks_of_month', [2])
        if not isinstance(weeks, list) or not weeks:
            raise ConfigError(
                "❌ publishing.weeks_of_month must be a non-empty list of integers (1-5)"
            )
        result['weeks_of_month'] = sorted(set(int(w) for w in weeks))
    else:
        result['days'] = publishing.get('days', ['monday'])

    return result


def get_publishing_rate(config: Dict[str, Any], stream: str = 'posts') -> Dict[str, Any]:
    """
    Get publishing rate info from configuration.

    Returns:
        Dict with:
        - posts_per_month: float (e.g., 1.0 for monthly, ~4.3 for weekly)
        - frequency_label: str (e.g., "1/month", "1/week")
    """
    pub_config = get_publishing_config(config, stream)
    frequency = pub_config.get('frequency', 'weekly')

    if frequency == 'biweekly':
        # 26 slots a year. A 1st-and-3rd-weekday scheme yields only 24, because
        # a month boundary occasionally stretches the gap to three weeks.
        return {
            'posts_per_month': 26 / 12,
            'frequency_label': 'every 2 weeks',
        }

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


def get_posts_per_week(config: Dict[str, Any], stream: str = 'posts') -> int:
    """
    Calculate posts per week from configuration.

    For biweekly and monthly frequencies, returns 1 (used as a fallback
    for legacy code that expects a weekly number).

    Args:
        config: Configuration dict from load_config()

    Returns:
        Number of posts per week based on configured publish days
    """
    pub_config = get_publishing_config(config, stream)
    if pub_config.get('frequency') in ('biweekly', 'monthly'):
        return 1
    return len(pub_config.get('days', ['monday']))


def get_stream_config(config: Dict[str, Any], stream: str = 'posts') -> Dict[str, Any]:
    """
    Get paths and display labels for a content stream.

    Tools take a stream name rather than hardcoding a directory, so the same
    code serves blog posts and newsletter issues.

    Args:
        config: Configuration dict from load_config()
        stream: 'posts' or 'newsletter'

    Returns:
        Dict with:
        - stream, label, noun, emoji: display metadata
        - content_dir: Path to the stream's MDX files
        - images_dir: Path, or None for streams that carry no images

    Raises:
        ConfigError: If the stream name is unknown
    """
    if stream not in STREAM_DEFAULTS:
        raise ConfigError(
            f"\u274c Unknown content stream: {stream!r}\n"
            f"Expected one of: {', '.join(sorted(STREAM_DEFAULTS))}"
        )

    defaults = STREAM_DEFAULTS[stream]
    config_key = defaults['config_key']

    if config_key is None:
        # Posts keep their paths at the top level of blog-config.yaml
        content_dir = config.get('content_dir', defaults['content_dir'])
        images_dir = config.get('public_images_dir', defaults['images_dir'])
    else:
        section = config.get(config_key) or {}
        content_dir = section.get('content_dir', defaults['content_dir'])
        images_dir = defaults['images_dir']

    return {
        'stream': stream,
        'label': defaults['label'],
        'noun': defaults['noun'],
        'emoji': defaults['emoji'],
        'content_dir': Path(content_dir),
        'images_dir': Path(images_dir) if images_dir else None,
    }


def get_newsletter_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get newsletter settings with defaults.

    Args:
        config: Configuration dict from load_config()

    Returns:
        Dict with:
        - enabled: whether a `newsletter:` block exists at all
        - archive_delay_days: days between sending an issue and publishing it
        - content_dir: Path to the issues directory
    """
    section = config.get('newsletter') or {}

    return {
        'enabled': 'newsletter' in config,
        'archive_delay_days': section.get('archive_delay_days', 30),
        'content_dir': get_stream_config(config, 'newsletter')['content_dir'],
    }
