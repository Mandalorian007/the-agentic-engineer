"""Configuration loading and validation"""

import os
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
    # Load environment variables from .env.local
    env_path = Path('.env.local')
    if not env_path.exists():
        raise ConfigError(
            "❌ .env.local not found\n"
            "Create .env.local with your credentials.\n"
            "See specs/blog-google-auth.md for setup instructions."
        )

    load_dotenv(env_path)

    # Load YAML configuration
    config_path = Path('blog-config.yaml')
    if not config_path.exists():
        raise ConfigError(
            "❌ blog-config.yaml not found\n"
            "Create blog-config.yaml in project root.\n"
            "See specs/blog-flow.md for configuration format."
        )

    try:
        with open(config_path) as f:
            config = yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise ConfigError(f"❌ Invalid YAML in blog-config.yaml: {e}")

    # Add credentials from environment
    config['blogger_credentials'] = {
        'client_id': os.getenv('BLOGGER_CLIENT_ID'),
        'client_secret': os.getenv('BLOGGER_CLIENT_SECRET'),
        'refresh_token': os.getenv('BLOGGER_REFRESH_TOKEN')
    }

    # Merge Cloudinary credentials with existing config from YAML
    cloudinary_config = config.get('cloudinary', {})
    cloudinary_config.update({
        'cloud_name': os.getenv('CLOUDINARY_CLOUD_NAME'),
        'api_key': os.getenv('CLOUDINARY_API_KEY'),
        'api_secret': os.getenv('CLOUDINARY_API_SECRET')
    })
    config['cloudinary'] = cloudinary_config

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
    required_fields = ['blog_name', 'blogger_blog_id']
    missing = [f for f in required_fields if f not in config or not config[f]]

    if missing:
        raise ConfigError(
            f"❌ Missing required fields in blog-config.yaml: {', '.join(missing)}\n"
            f"Example:\n"
            f"  blog_name: \"My Blog\"\n"
            f"  blogger_blog_id: \"1234567890\""
        )

    # Validate Blogger credentials
    blogger_creds = config.get('blogger_credentials', {})
    required_creds = ['client_id', 'client_secret', 'refresh_token']
    missing_creds = [
        f for f in required_creds
        if not blogger_creds.get(f)
    ]

    if missing_creds:
        raise ConfigError(
            f"❌ Missing Blogger credentials in .env.local:\n"
            f"   {', '.join(f'BLOGGER_{f.upper()}' for f in missing_creds)}\n"
            f"Run: uv run tools/generate_refresh_token.py"
        )

    # Validate Cloudinary credentials
    cloudinary = config.get('cloudinary', {})
    required_cloudinary = ['cloud_name', 'api_key', 'api_secret']
    missing_cloudinary = [
        f for f in required_cloudinary
        if not cloudinary.get(f)
    ]

    if missing_cloudinary:
        raise ConfigError(
            f"❌ Missing Cloudinary credentials in .env.local:\n"
            f"   {', '.join(f'CLOUDINARY_{f.upper()}' for f in missing_cloudinary)}\n"
            f"Sign up at cloudinary.com and add credentials to .env.local"
        )

    # Validate blog ID format (should be numeric)
    blog_id = str(config['blogger_blog_id'])
    if not blog_id.isdigit():
        raise ConfigError(
            f"❌ Invalid blogger_blog_id: {blog_id}\n"
            f"Blog ID should be a numeric string (e.g., '1234567890123456789')\n"
            f"Find it at: https://www.blogger.com/blog/posts/YOUR_BLOG_ID"
        )


def get_image_optimization_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get image optimization settings with defaults

    Args:
        config: Full configuration dict

    Returns:
        Image optimization settings
    """
    defaults = {
        'max_width': 1200,
        'max_height': 1200,
        'quality': 85,
        'format': 'JPEG'
    }

    user_config = config.get('image_optimization', {})
    return {**defaults, **user_config}


def get_markdown_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get markdown processing settings with defaults

    Args:
        config: Full configuration dict

    Returns:
        Markdown processing settings
    """
    defaults = {
        'extensions': ['tables', 'strikethrough', 'tasklists'],
        'syntax_highlighting': {
            'style': 'monokai',
            'line_numbers': True
        }
    }

    user_config = config.get('markdown', {})

    # Merge syntax_highlighting separately to handle nested dict
    if 'syntax_highlighting' in user_config:
        defaults['syntax_highlighting'].update(user_config['syntax_highlighting'])
        user_config = {k: v for k, v in user_config.items() if k != 'syntax_highlighting'}

    return {**defaults, **user_config}
