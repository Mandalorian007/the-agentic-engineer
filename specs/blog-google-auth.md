# Google OAuth Setup Guide for Blogger API

## Overview

This guide walks through setting up Google OAuth 2.0 authentication for the Blogger API automation system. You'll obtain credentials, generate a refresh token, and configure the application for persistent API access.

**Time Required**: 15-20 minutes
**Prerequisites**: Google account, Python 3.10+

---

## Library Selection

### Authentication Stack

Based on 2025 best practices, use Google's officially maintained libraries:

| Library | Purpose | Why This One |
|---------|---------|--------------|
| **google-auth** | Core authentication primitives | Official Google library, actively maintained |
| **google-auth-oauthlib** | OAuth 2.0 flow implementation | Handles authorization flow and token exchange |
| **google-api-python-client** | Blogger API client | Discovery-based API access for Blogger v3 |

**Deprecated**: `oauth2client` (deprecated 2017, do not use)

### Markdown Processing

| Library | Purpose | Why This One |
|---------|---------|--------------|
| **markdown-it-py** | Markdown → HTML conversion | Outstanding plugin architecture, 100% CommonMark support, fast-growing ecosystem for extensions (diagrams, highlighting) |

**Alternatives**: `mistune` (excellent performance), `Python-Markdown` (most mature, broadest legacy ecosystem)

**Rationale**: markdown-it-py's plugin system is modeled after the popular JS markdown-it library, making it the most extensible for future features like mermaid diagrams or custom rendering.

### Image Processing

| Library | Purpose | Why This One |
|---------|---------|--------------|
| **Pillow** | Pre-processing (resize, optimize) | Simple API, broad format support, sufficient for pre-upload optimization |
| **cloudinary** | Cloud storage and delivery | Advanced compression, CDN delivery, WebP/AVIF auto-conversion |

**Note**: Heavy optimization happens in Cloudinary; Pillow handles basic pre-processing only.

### Configuration & Utilities

| Library | Purpose |
|---------|---------|
| **PyYAML** | Parse `blog-config.yaml` |
| **python-dotenv** | Load `.env` credentials |
| **Pygments** | Syntax highlighting for code blocks |

---

## Part 1: Google Cloud Project Setup

### Step 1: Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click **Select a project** → **New Project**
3. Name it: `blogger-automation` (or your preference)
4. Click **Create**

### Step 2: Enable Blogger API

1. In your project, navigate to **APIs & Services** → **Library**
2. Search for "Blogger API v3"
3. Click **Enable**

### Step 3: Configure OAuth Consent Screen

The OAuth consent screen is what users see when authorizing your application to access their Google account. Even though this is a personal automation tool, Google requires this configuration.

#### 3.1: Choose User Type

1. Go to **APIs & Services** → **OAuth consent screen**
2. You'll see two user type options:

   **Internal** (only if you have Google Workspace):
   - Only available for Google Workspace organizations
   - Users within your organization can use the app
   - No verification needed
   - **Choose this if available** (simpler setup)

   **External**:
   - Anyone with a Google account can authorize the app
   - App starts in "Testing" mode (limited to test users)
   - Requires verification for public release (not needed for personal use)
   - **Choose this for personal Google accounts**

3. Select **External** (most common for personal projects)
4. Click **Create**

#### 3.2: App Information (Page 1)

Fill out the required fields:

**App Information**:
- **App name**: `Blogger Automation Tool` (or any descriptive name)
  - *This appears on the consent screen when you authorize*
  - Only you will see this, so choose something recognizable

- **User support email**: Select your email from dropdown
  - *Where users would report issues*
  - Required field, just select your own email

- **App logo**: Leave empty (optional)
  - *You don't need a logo for personal tools*

**App Domain** (all optional for personal use):
- **Application home page**: Leave empty
- **Application privacy policy link**: Leave empty
- **Application terms of service link**: Leave empty
- *These are only required if you're publishing the app publicly*

**Authorized domains**: Leave empty
- *Used for web apps with callback URLs*
- Not needed for desktop/CLI applications

**Developer Contact Information**:
- **Email addresses**: Enter your email
  - *Google uses this to notify you about your project*
  - Can be the same as user support email

5. Click **Save and Continue**

#### 3.3: Scopes (Page 2)

Scopes define what permissions your app requests. **Skip this page entirely** for now.

**Why skip scopes here?**
- Your application code will request the specific scope (`https://www.googleapis.com/auth/blogger`) programmatically
- You don't need to register scopes in the consent screen for "Testing" status apps
- Manually adding them here is optional and doesn't affect functionality

**What you'll see**:
- A section titled "Add or Remove Scopes"
- A table showing "Your non-sensitive scopes" and "Your sensitive scopes"
- Both will be empty

**Action**: Click **Save and Continue** (leave scopes empty)

#### 3.4: Test Users (Page 3)

Since your app is in "Testing" mode, only specified test users can authorize it. This is a security feature.

**Why this matters (CRITICAL)**:
- Apps in "Testing" status are limited to 100 test users
- Only test users can complete the OAuth flow
- If you try to authorize with a non-test-user account, you'll see "Access blocked: This app's request is invalid"

**Add yourself as a test user**:
1. Click **+ Add Users**
2. Enter your Google account email (the one that owns your Blogger blog)
3. Click **Add**
4. You should see your email in the "Test users" table

**Multiple Google accounts?** If you manage multiple Blogger blogs with different Google accounts, add all of them here.

5. Click **Save and Continue**

#### 3.5: Summary (Page 4)

Review your settings. You should see:
- **Publishing status**: Testing
- **App name**: Blogger Automation Tool
- **User type**: External
- **Test users**: Your email(s)

6. Click **Back to Dashboard**

#### 3.6: Important Notes

**"Unverified App" Warning**:
When you first authorize, you'll see a warning screen:
```
Google hasn't verified this app
This app hasn't been verified by Google yet. Only proceed if you
know and trust the developer.
```

**This is normal!** Since you're the developer and the only user:
1. Click **Advanced** (or "Show Advanced" link)
2. Click **Go to Blogger Automation Tool (unsafe)**
3. Review permissions and click **Continue**

**You only see this warning because**:
- Your app is in "Testing" status
- Google requires a verification process for public apps
- Personal tools don't need verification

**Publishing status**: Your app stays in "Testing" mode forever for personal use. You do **not** need to submit for verification unless you want to distribute the tool publicly.

**Consent screen can be edited**: You can always go back to **OAuth consent screen** to:
- Add more test users
- Update app name or contact info
- Add scopes manually (though not required)

### Step 4: Create OAuth Credentials

1. Go to **APIs & Services** → **Credentials**
2. Click **Create Credentials** → **OAuth client ID**
3. Application type: **Desktop app**
4. Name: `blogger-cli-client`
5. Click **Create**

**Download credentials**:
- Click the download icon (⬇️) next to your new OAuth client
- Save as `client_secret.json` in your project root
- **Do NOT commit this file to git**

---

## Part 2: Obtain Refresh Token

### Step 1: Install Dependencies

Create `pyproject.toml`:

```toml
[project]
name = "agentic-engineer-blog"
version = "0.1.0"
requires-python = ">=3.10"
dependencies = [
    "google-auth>=2.36.0",
    "google-auth-oauthlib>=1.2.1",
    "google-api-python-client>=2.155.0",
    "markdown-it-py>=3.0.0",
    "mdit-py-plugins>=0.4.2",  # Extensions for markdown-it-py
    "Pillow>=11.0.0",
    "cloudinary>=1.41.0",
    "PyYAML>=6.0.2",
    "python-dotenv>=1.0.1",
    "Pygments>=2.18.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

Install:
```bash
uv sync
```

### Step 2: Create Token Generation Script

Create `tools/generate_refresh_token.py`:

```python
#!/usr/bin/env python3
"""
One-time script to generate a Blogger API refresh token.
Run this once, then store the refresh token in .env
"""

from google_auth_oauthlib.flow import InstalledAppFlow
import json

SCOPES = ['https://www.googleapis.com/auth/blogger']

def main():
    print("=== Blogger API Token Generator ===\n")

    # Check for client_secret.json
    try:
        flow = InstalledAppFlow.from_client_secrets_file(
            'client_secret.json',
            scopes=SCOPES
        )
    except FileNotFoundError:
        print("❌ Error: client_secret.json not found")
        print("Download it from Google Cloud Console → Credentials")
        return

    # Run local server for OAuth flow
    print("🌐 Opening browser for authorization...")
    print("   If browser doesn't open, copy the URL from the terminal\n")

    creds = flow.run_local_server(
        port=8080,
        prompt='consent',
        access_type='offline'
    )

    print("\n✅ Authorization successful!\n")

    # Extract credentials
    client_id = creds.client_id
    client_secret = creds.client_secret
    refresh_token = creds.refresh_token

    # Display for .env
    print("=== Add these to your .env file ===\n")
    print(f"BLOGGER_CLIENT_ID={client_id}")
    print(f"BLOGGER_CLIENT_SECRET={client_secret}")
    print(f"BLOGGER_REFRESH_TOKEN={refresh_token}")
    print("\n" + "="*50)

    # Optional: Save to file for reference
    with open('.credentials.json', 'w') as f:
        json.dump({
            'client_id': client_id,
            'client_secret': client_secret,
            'refresh_token': refresh_token
        }, f, indent=2)

    print("\n💾 Credentials also saved to .credentials.json")
    print("⚠️  Remember to add both files to .gitignore!\n")

if __name__ == '__main__':
    main()
```

Make executable:
```bash
chmod +x tools/generate_refresh_token.py
```

### Step 3: Generate Your Refresh Token

Run the script:
```bash
uv run tools/generate_refresh_token.py
```

**What happens**:
1. Browser opens to Google OAuth consent page
2. Select your Google account
3. Click **Continue** (you'll see a warning since app is unverified - this is normal for personal projects)
4. Grant permissions to manage your Blogger account
5. Script displays credentials in terminal

**Copy the output** and add to `.env.local`:

```bash
# Google Blogger API Credentials
BLOGGER_CLIENT_ID=your-client-id.apps.googleusercontent.com
BLOGGER_CLIENT_SECRET=your-client-secret
BLOGGER_REFRESH_TOKEN=your-refresh-token

# Cloudinary Credentials (get from cloudinary.com)
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret
```

### Step 4: Get Your Blog ID

You need your Blogger blog's numeric ID.

**Option A: From Blogger Dashboard**
1. Go to [blogger.com](https://www.blogger.com)
2. Select your blog
3. In the URL, find the ID: `https://www.blogger.com/blog/posts/1234567890123456789`
4. Copy the numeric ID

**Option B: Using API**

Create `tools/get_blog_id.py`:

```python
#!/usr/bin/env python3
"""Helper script to list your blogs and their IDs"""

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from dotenv import load_dotenv
import os

load_dotenv('.env.local')

def main():
    creds = Credentials(
        token=None,
        refresh_token=os.getenv('BLOGGER_REFRESH_TOKEN'),
        client_id=os.getenv('BLOGGER_CLIENT_ID'),
        client_secret=os.getenv('BLOGGER_CLIENT_SECRET'),
        token_uri='https://oauth2.googleapis.com/token'
    )

    service = build('blogger', 'v3', credentials=creds)
    result = service.blogs().listByUser(userId='self').execute()

    print("=== Your Blogger Blogs ===\n")
    for blog in result.get('items', []):
        print(f"Name: {blog['name']}")
        print(f"ID:   {blog['id']}")
        print(f"URL:  {blog['url']}")
        print()

if __name__ == '__main__':
    main()
```

Run:
```bash
uv run tools/get_blog_id.py
```

Copy your blog ID.

---

## Part 3: Configure the Application

### Step 1: Create blog-config.yaml

Create `blog-config.yaml` in project root:

```yaml
# Blog Identity
blog_name: "Agentic Engineer Blog"
blogger_blog_id: "1234567890123456789"  # Replace with your blog ID

# Image Optimization (applied before Cloudinary upload)
image_optimization:
  max_width: 1200        # Resize images wider than this
  max_height: 1200       # Resize images taller than this
  quality: 85            # JPEG quality (1-100)
  format: "JPEG"         # Pre-upload format (JPEG or PNG)

# Cloudinary Upload Settings
cloudinary:
  folder: "blog-posts"   # Base folder for uploads
  format: "webp"         # Final format (webp, auto)
  quality: "auto:good"   # auto, auto:low, auto:good, auto:best, or 1-100

# Markdown Processing
markdown:
  extensions:
    - "tables"           # GitHub-style tables
    - "strikethrough"    # ~~text~~
    - "tasklists"        # - [ ] todo items
  syntax_highlighting:
    style: "monokai"     # Pygments style
    line_numbers: true
```

### Step 2: Create .gitignore

Create/update `.gitignore`:

```gitignore
# Credentials (NEVER COMMIT)
.env.local
client_secret.json
.credentials.json
token.pickle

# Python
__pycache__/
*.py[cod]
*$py.class
.venv/
venv/
*.egg-info/
dist/
build/

# IDEs
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Build artifacts
*.log
```

### Step 3: Verify Configuration

Create `tools/test_auth.py`:

```python
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
```

Run verification:
```bash
uv run tools/test_auth.py
```

**Expected output**:
```
🔧 Blogger Automation Setup Verification

=== Testing Configuration ===

✅ .env.local loaded successfully
✅ blog-config.yaml loaded successfully
   Blog: Agentic Engineer Blog
   Blog ID: 1234567890123456789

=== Testing Blogger Authentication ===

✅ Refresh token is valid
✅ Successfully connected to blog: Agentic Engineer Blog
   URL: https://agentic-engineer.blogspot.com/
   Posts: 0

=== Testing Cloudinary Configuration ===

✅ Cloudinary configured successfully
   Cloud: your-cloud-name

==================================================
✅ All tests passed! Ready to build and publish.
==================================================
```

---

## Part 4: Authentication Implementation

### Production Authentication Module

For `lib/auth.py`, use this pattern:

```python
"""Authentication utilities for Blogger API"""

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import os

class BloggerAuthError(Exception):
    """Authentication errors"""
    pass

def get_blogger_service(client_id: str, client_secret: str, refresh_token: str):
    """
    Create authenticated Blogger API service.

    Args:
        client_id: OAuth client ID
        client_secret: OAuth client secret
        refresh_token: Long-lived refresh token

    Returns:
        Authenticated Blogger API service

    Raises:
        BloggerAuthError: If authentication fails
    """
    try:
        creds = Credentials(
            token=None,
            refresh_token=refresh_token,
            client_id=client_id,
            client_secret=client_secret,
            token_uri='https://oauth2.googleapis.com/token'
        )

        # Refresh to get valid access token
        creds.refresh(Request())

        # Build service
        service = build('blogger', 'v3', credentials=creds)

        return service

    except Exception as e:
        raise BloggerAuthError(f"Failed to authenticate with Blogger API: {e}")

def test_connection(service, blog_id: str) -> bool:
    """
    Test API connection by fetching blog info.

    Args:
        service: Authenticated Blogger service
        blog_id: Blogger blog ID

    Returns:
        True if connection successful

    Raises:
        BloggerAuthError: If connection fails
    """
    try:
        blog = service.blogs().get(blogId=blog_id).execute()
        return True
    except HttpError as e:
        if e.resp.status == 401:
            raise BloggerAuthError("Invalid credentials or expired token")
        elif e.resp.status == 404:
            raise BloggerAuthError(f"Blog not found: {blog_id}")
        else:
            raise BloggerAuthError(f"API error: {e}")
```

### Token Refresh Behavior

**Key points**:
- Access tokens expire after ~1 hour
- Refresh tokens are **long-lived** (can last months/years)
- `creds.refresh(Request())` automatically exchanges refresh token for new access token
- No user interaction needed after initial setup
- Refresh tokens can be revoked from [Google Account Settings](https://myaccount.google.com/permissions)

### Security Best Practices

1. **Never commit credentials**:
   ```bash
   # Add to .gitignore
   .env.local
   client_secret.json
   ```
   Note: `.env` is reserved for MCP configuration

2. **Use environment variables** for all secrets

3. **Limit OAuth scopes**: Only request `https://www.googleapis.com/auth/blogger`

4. **Rotate refresh tokens** periodically (regenerate using `generate_refresh_token.py`)

5. **For production servers**: Use service accounts or Secret Manager (beyond MVP scope)

---

## Troubleshooting

### Error: "Access blocked: This app's request is invalid"

**Cause**: OAuth consent screen not configured or missing test user

**Fix**:
1. Google Cloud Console → OAuth consent screen
2. Add your email to **Test users**
3. Regenerate refresh token

### Error: "invalid_grant"

**Cause**: Refresh token expired or revoked

**Fix**:
1. Run `uv run tools/generate_refresh_token.py` again
2. Update `.env.local` with new refresh token

### Error: "insufficient_permissions" or "insufficientPermissions"

**Cause**: OAuth scope missing or blog ID wrong

**Fix**:
1. Verify blog ID with `get_blog_id.py`
2. Ensure OAuth scope is `https://www.googleapis.com/auth/blogger`
3. Regenerate refresh token with correct scope

### Error: "The caller does not have permission"

**Cause**: Authenticated account doesn't own the blog

**Fix**:
- Ensure the Google account used for OAuth is an author/admin on the blog
- Check blog permissions at blogger.com → Settings → Permissions

---

## Next Steps

After completing this setup:

1. ✅ **Authentication configured** - Ready to use Blogger API
2. ✅ **Configuration files created** - `blog-config.yaml` and `.env.local`
3. ✅ **Dependencies installed** - All libraries available

**You're ready to implement**:
- `build.py` - Validation and preview
- `publish.py` - Image upload and post publishing

Refer to `specs/blog-flow.md` for implementation details.

---

## Appendix: Library Details

### Why markdown-it-py?

**Extensibility advantages**:
```python
from markdown_it import MarkdownIt
from mdit_py_plugins.front_matter import front_matter_plugin
from mdit_py_plugins.footnote import footnote_plugin

md = (
    MarkdownIt()
    .use(front_matter_plugin)
    .use(footnote_plugin)
    .enable('table')
)

# Future: Add diagram support
# .use(mermaid_plugin)  # When available
```

**Plugin ecosystem growing rapidly**:
- Tables, strikethrough, task lists (built-in)
- Footnotes, definition lists (mdit-py-plugins)
- LaTeX math (mdit-py-plugins)
- Future: Mermaid, graphviz renderers

**100% CommonMark compliance** ensures portability.

### Why google-auth over oauth2client?

| Feature | oauth2client | google-auth |
|---------|--------------|-------------|
| Maintained | ❌ (deprecated 2017) | ✅ |
| Security updates | ❌ | ✅ |
| Token storage | Built-in | Manual (more flexible) |
| Modern Python | Limited | Full support |
| Google recommendation | No | Yes |

### Cloudinary vs Self-Hosted

**Cloudinary advantages**:
- Automatic format selection (WebP for Chrome, AVIF for modern browsers)
- On-the-fly transformations (resize, crop, quality adjust)
- Global CDN delivery
- Free tier: 25GB storage, 25GB bandwidth/month

**For MVP**: Cloudinary handles optimization better than local Pillow processing.

---

## Quick Reference

### Essential Commands

```bash
# One-time setup
uv run tools/generate_refresh_token.py
uv run tools/get_blog_id.py

# Verify configuration
uv run tools/test_auth.py

# Main workflow (after implementation)
uv run build.py posts/2025-10-12-my-post/
uv run publish.py posts/2025-10-12-my-post/
```

### Environment Variables Reference

File: `.env.local`

```bash
# Blogger (from OAuth flow)
BLOGGER_CLIENT_ID=xxx.apps.googleusercontent.com
BLOGGER_CLIENT_SECRET=xxx
BLOGGER_REFRESH_TOKEN=xxx

# Cloudinary (from cloudinary.com dashboard)
CLOUDINARY_CLOUD_NAME=xxx
CLOUDINARY_API_KEY=xxx
CLOUDINARY_API_SECRET=xxx
```

### Scope Reference

```python
SCOPES = ['https://www.googleapis.com/auth/blogger']
```

This scope grants:
- ✅ Read blog metadata
- ✅ Create posts
- ✅ Update posts
- ✅ Delete posts
- ❌ Does NOT grant access to other Google services
