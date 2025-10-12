#!/usr/bin/env python3
"""Test authentication and configuration"""

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from dotenv import load_dotenv
import yaml
import os

def test_config():
    """Test configuration loading"""
    print("=== Testing Configuration ===\n")

    # Check .env.local
    load_dotenv('.env.local')
    required_env = [
        'BLOGGER_CLIENT_ID',
        'BLOGGER_CLIENT_SECRET',
        'BLOGGER_REFRESH_TOKEN',
        'CLOUDINARY_CLOUD_NAME',
        'CLOUDINARY_API_KEY',
        'CLOUDINARY_API_SECRET'
    ]

    missing = [k for k in required_env if not os.getenv(k)]
    if missing:
        print(f"❌ Missing .env.local variables: {', '.join(missing)}")
        return False
    print("✅ .env.local loaded successfully")

    # Check blog-config.yaml
    try:
        with open('blog-config.yaml') as f:
            config = yaml.safe_load(f)
        print("✅ blog-config.yaml loaded successfully")
        print(f"   Blog: {config['blog_name']}")
        print(f"   Blog ID: {config['blogger_blog_id']}")
    except Exception as e:
        print(f"❌ Error loading blog-config.yaml: {e}")
        return False

    return True

def test_blogger_auth():
    """Test Blogger API authentication"""
    print("\n=== Testing Blogger Authentication ===\n")

    try:
        creds = Credentials(
            token=None,
            refresh_token=os.getenv('BLOGGER_REFRESH_TOKEN'),
            client_id=os.getenv('BLOGGER_CLIENT_ID'),
            client_secret=os.getenv('BLOGGER_CLIENT_SECRET'),
            token_uri='https://oauth2.googleapis.com/token'
        )

        # Refresh to get access token
        creds.refresh(Request())
        print("✅ Refresh token is valid")

        # Test API call
        service = build('blogger', 'v3', credentials=creds)

        with open('blog-config.yaml') as f:
            config = yaml.safe_load(f)

        blog = service.blogs().get(blogId=config['blogger_blog_id']).execute()
        print(f"✅ Successfully connected to blog: {blog['name']}")
        print(f"   URL: {blog['url']}")
        print(f"   Posts: {blog.get('posts', {}).get('totalItems', 0)}")

        return True

    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        return False

def test_cloudinary():
    """Test Cloudinary configuration"""
    print("\n=== Testing Cloudinary Configuration ===\n")

    try:
        import cloudinary
        cloudinary.config(
            cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
            api_key=os.getenv('CLOUDINARY_API_KEY'),
            api_secret=os.getenv('CLOUDINARY_API_SECRET')
        )
        print("✅ Cloudinary configured successfully")
        print(f"   Cloud: {os.getenv('CLOUDINARY_CLOUD_NAME')}")
        return True
    except Exception as e:
        print(f"❌ Cloudinary configuration failed: {e}")
        return False

def main():
    print("🔧 Blogger Automation Setup Verification\n")

    results = [
        test_config(),
        test_blogger_auth(),
        test_cloudinary()
    ]

    print("\n" + "="*50)
    if all(results):
        print("✅ All tests passed! Ready to build and publish.")
    else:
        print("❌ Some tests failed. Fix the errors above.")
    print("="*50 + "\n")

if __name__ == '__main__':
    main()
