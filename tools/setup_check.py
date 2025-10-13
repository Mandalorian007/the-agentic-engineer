#!/usr/bin/env python3
"""
Interactive setup checker for the Agentic Engineer Blog automation.
Guides you through configuration step-by-step with actionable instructions.
"""

from pathlib import Path
import os
import sys
import yaml
from dotenv import load_dotenv

# Color codes for terminal output
class Color:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text):
    """Print a bold header"""
    print(f"\n{Color.BOLD}{text}{Color.END}")

def print_success(text):
    """Print success message"""
    print(f"{Color.GREEN}✅ {text}{Color.END}")

def print_error(text):
    """Print error message"""
    print(f"{Color.RED}❌ {text}{Color.END}")

def print_warning(text):
    """Print warning message"""
    print(f"{Color.YELLOW}⚠️  {text}{Color.END}")

def print_info(text):
    """Print info message"""
    print(f"{Color.BLUE}ℹ️  {text}{Color.END}")

def print_action(text):
    """Print action to take"""
    print(f"{Color.YELLOW}→ {text}{Color.END}")


class SetupChecker:
    """Orchestrates setup validation"""

    def __init__(self):
        self.issues = []
        self.warnings = []
        self.env_vars = {}
        self.blog_config = {}

    def run(self):
        """Run all setup checks"""
        print(f"{Color.BOLD}{'='*60}")
        print("🚀 Agentic Engineer Blog - Setup Verification")
        print(f"{'='*60}{Color.END}\n")

        # Check in order of setup flow
        checks = [
            ("Dependencies", self.check_dependencies),
            ("Configuration Files", self.check_config_files),
            ("Google OAuth Setup", self.check_google_oauth),
            ("Cloudinary Setup", self.check_cloudinary),
            ("OpenAI Setup", self.check_openai),
            ("Blog Configuration", self.check_blog_config),
            ("Next.js Website Setup", self.check_website_setup),
            ("Connectivity Test", self.test_connectivity),
        ]

        for section, check_func in checks:
            print_header(f"📋 {section}")
            check_func()

        # Final summary
        self.print_summary()

    def check_dependencies(self):
        """Check if required dependencies are installed"""
        import subprocess

        # Check if uv environment is set up
        venv_path = Path('.venv')
        if venv_path.exists():
            print_success("Python virtual environment exists (.venv)")
        else:
            print_error("Virtual environment not found")
            self.issues.append("Missing virtual environment")
            print_action("Run: uv sync")

        # Check for Vale prose linter
        try:
            result = subprocess.run(['vale', '--version'],
                                  capture_output=True,
                                  text=True,
                                  timeout=5)
            if result.returncode == 0:
                version = result.stdout.strip().split('\n')[0]
                print_success(f"Vale prose linter installed ({version})")

                # Sync Vale styles to ensure they're up to date
                print_info("   Syncing Vale style packages...")
                sync_result = subprocess.run(['vale', 'sync'],
                                            capture_output=True,
                                            text=True,
                                            timeout=30)
                if sync_result.returncode == 0:
                    print_success("   Vale styles synced")
                else:
                    print_warning("   Vale sync had issues (may be okay if styles already exist)")
            else:
                print_warning("Vale installed but version check failed")
                self.warnings.append("Vale may not be properly configured")
        except FileNotFoundError:
            print_warning("Vale prose linter not found")
            self.warnings.append("Vale not installed - prose linting unavailable")
            print_action("Install Vale: brew install vale")
            print_info("   Then run: vale sync")
        except subprocess.TimeoutExpired:
            print_warning("Vale check timed out")
            self.warnings.append("Vale may not be working correctly")

    def check_config_files(self):
        """Check if required config files exist"""
        files = {
            '.env.local': 'Environment variables (credentials)',
            'blog-config.yaml': 'Blog configuration',
            'client_secret.json': 'Google OAuth client secret (if not yet converted to refresh token)',
        }

        for filename, description in files.items():
            path = Path(filename)
            if path.exists():
                print_success(f"{filename} exists - {description}")
            else:
                if filename == 'client_secret.json':
                    # This is optional if refresh token already exists
                    print_warning(f"{filename} not found (optional if refresh token already set)")
                else:
                    print_error(f"{filename} not found - {description}")
                    self.issues.append(f"Missing {filename}")

                    if filename == '.env.local':
                        print_action("Create .env.local with the following template:")
                        print("    BLOGGER_CLIENT_ID=")
                        print("    BLOGGER_CLIENT_SECRET=")
                        print("    BLOGGER_REFRESH_TOKEN=")
                        print("    CLOUDINARY_CLOUD_NAME=")
                        print("    CLOUDINARY_API_KEY=")
                        print("    CLOUDINARY_API_SECRET=")
                        print("    OPENAI_API_KEY=")
                        print_info("See: specs/blog-google-auth.md for detailed setup")

                    elif filename == 'blog-config.yaml':
                        print_action("Create blog-config.yaml with blog settings")
                        print_info("See: specs/blog-flow.md for configuration format")

    def check_google_oauth(self):
        """Check Google OAuth setup"""
        # Load .env.local if it exists
        env_path = Path('.env.local')
        if env_path.exists():
            load_dotenv(env_path)

        required_vars = {
            'BLOGGER_CLIENT_ID': 'OAuth Client ID from Google Cloud Console',
            'BLOGGER_CLIENT_SECRET': 'OAuth Client Secret from Google Cloud Console',
            'BLOGGER_REFRESH_TOKEN': 'Long-lived refresh token for API access',
        }

        all_present = True
        for var, description in required_vars.items():
            value = os.getenv(var)
            self.env_vars[var] = value

            if value:
                # Mask secrets in output
                masked = value[:8] + '...' if len(value) > 8 else '***'
                print_success(f"{var} set ({masked})")
            else:
                print_error(f"{var} not set - {description}")
                all_present = False

        if not all_present:
            self.issues.append("Missing Google OAuth credentials")
            print()
            print_action("To set up Google OAuth:")

            if not os.getenv('BLOGGER_CLIENT_ID') or not os.getenv('BLOGGER_CLIENT_SECRET'):
                print("  1. Go to Google Cloud Console: https://console.cloud.google.com/")
                print("  2. Create project → Enable Blogger API → Create OAuth credentials")
                print("  3. Download client_secret.json to project root")
                print_info("Detailed guide: specs/blog-google-auth.md")

            if not os.getenv('BLOGGER_REFRESH_TOKEN'):
                if Path('client_secret.json').exists():
                    print("  4. Generate refresh token:")
                    print_action("     uv run tools/generate_refresh_token.py")
                else:
                    print("  4. First download client_secret.json, then run:")
                    print_action("     uv run tools/generate_refresh_token.py")

    def check_cloudinary(self):
        """Check Cloudinary setup"""
        required_vars = {
            'CLOUDINARY_CLOUD_NAME': 'Your Cloudinary cloud name',
            'CLOUDINARY_API_KEY': 'Cloudinary API key',
            'CLOUDINARY_API_SECRET': 'Cloudinary API secret',
        }

        all_present = True
        for var, description in required_vars.items():
            value = os.getenv(var)
            self.env_vars[var] = value

            if value:
                masked = value[:6] + '...' if len(value) > 6 else '***'
                print_success(f"{var} set ({masked})")
            else:
                print_error(f"{var} not set - {description}")
                all_present = False

        if not all_present:
            self.issues.append("Missing Cloudinary credentials")
            print()
            print_action("To set up Cloudinary:")
            print("  1. Sign up at https://cloudinary.com/ (free tier available)")
            print("  2. Go to Dashboard → Account Details")
            print("  3. Copy Cloud Name, API Key, and API Secret")
            print("  4. Add them to .env.local")

    def check_openai(self):
        """Check OpenAI API key setup"""
        api_key = os.getenv('OPENAI_API_KEY')

        if api_key:
            masked = api_key[:8] + '...' if len(api_key) > 8 else '***'
            print_success(f"OPENAI_API_KEY set ({masked})")
        else:
            print_warning("OPENAI_API_KEY not set - Image generation unavailable")
            self.warnings.append("OpenAI API key not configured")
            print()
            print_action("To set up OpenAI API (optional for image generation):")
            print("  1. Sign up at https://platform.openai.com/")
            print("  2. Generate API key at: https://platform.openai.com/api-keys")
            print("  3. Add OPENAI_API_KEY to .env.local")
            print_info("   Used by: uv run tools/generate_image.py")

    def check_blog_config(self):
        """Check blog-config.yaml"""
        config_path = Path('blog-config.yaml')
        if not config_path.exists():
            print_error("blog-config.yaml not found")
            self.issues.append("Missing blog-config.yaml")
            return

        try:
            with open(config_path) as f:
                self.blog_config = yaml.safe_load(f)
            print_success("blog-config.yaml is valid YAML")
        except yaml.YAMLError as e:
            print_error(f"Invalid YAML: {e}")
            self.issues.append("Invalid blog-config.yaml")
            return

        # Check required fields
        required_fields = {
            'blog_name': 'Your blog name',
            'blogger_blog_id': 'Numeric blog ID from Blogger',
        }

        for field, description in required_fields.items():
            if field in self.blog_config and self.blog_config[field]:
                print_success(f"{field}: {self.blog_config[field]}")
            else:
                print_error(f"{field} not set - {description}")
                self.issues.append(f"Missing {field} in blog-config.yaml")

        # Validate blog ID format
        blog_id = self.blog_config.get('blogger_blog_id')
        if blog_id:
            blog_id_str = str(blog_id)
            if not blog_id_str.isdigit():
                print_error(f"Invalid blogger_blog_id: {blog_id}")
                print_action("Blog ID must be numeric (e.g., '1234567890123456789')")
                self.issues.append("Invalid blog ID format")

        if not blog_id:
            print()
            print_action("To find your blog ID:")
            print("  Check Blogger dashboard URL:")
            print("    https://www.blogger.com/blog/posts/[YOUR_BLOG_ID]")

    def check_website_setup(self):
        """Check Next.js website configuration"""
        website_dir = Path('website')

        if not website_dir.exists():
            print_warning("website/ directory not found - Next.js site not initialized")
            self.warnings.append("Next.js website not set up")
            return

        print_success("website/ directory exists")

        # Check for website/.env.local file
        website_env = website_dir / '.env.local'
        if website_env.exists():
            print_success("website/.env.local exists")

            # Parse environment variables
            env_vars = {}
            try:
                with open(website_env) as f:
                    env_content = f.read()
                    for line in env_content.splitlines():
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            env_vars[key.strip()] = value.strip()
            except Exception as e:
                print_warning(f"  Could not parse website/.env.local: {e}")
                self.warnings.append("Unable to parse website/.env.local")
                return

            # Check for Clerk Authentication (REQUIRED)
            clerk_pub_key = env_vars.get('NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY', '')
            clerk_secret_key = env_vars.get('CLERK_SECRET_KEY', '')

            clerk_missing = []
            if clerk_pub_key:
                if clerk_pub_key.startswith('pk_test_') or clerk_pub_key.startswith('pk_live_'):
                    masked = clerk_pub_key[:12] + '...'
                    print_success(f"  NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY set ({masked})")
                else:
                    print_warning("  NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY format may be incorrect")
                    self.warnings.append("Clerk publishable key format unexpected")
            else:
                print_error("  NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY not set")
                clerk_missing.append('NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY')

            if clerk_secret_key:
                if clerk_secret_key.startswith('sk_test_') or clerk_secret_key.startswith('sk_live_'):
                    masked = clerk_secret_key[:12] + '...'
                    print_success(f"  CLERK_SECRET_KEY set ({masked})")
                else:
                    print_warning("  CLERK_SECRET_KEY format may be incorrect")
                    self.warnings.append("Clerk secret key format unexpected")
            else:
                print_error("  CLERK_SECRET_KEY not set")
                clerk_missing.append('CLERK_SECRET_KEY')

            if clerk_missing:
                self.issues.append("Missing Clerk authentication credentials")
                print()
                print_action("  Clerk authentication is REQUIRED for Next.js website")
                print_action("  Add to website/.env.local:")
                for key in clerk_missing:
                    print(f"    {key}=")
                print_info("  Setup guide:")
                print("    1. Create account at https://clerk.com")
                print("    2. Create new project in Clerk dashboard")
                print("    3. Copy Publishable Key and Secret Key")
                print("    4. Set callback URLs:")
                print("       - Local: http://localhost:3000")
                print("       - Production: https://the-agentic-engineer.com")

            # Check for SHADCNBLOCKS_API_KEY
            shadcn_key = env_vars.get('SHADCNBLOCKS_API_KEY', '')
            if shadcn_key:
                if shadcn_key.startswith('sk_live_'):
                    masked = shadcn_key[:12] + '...'
                    print_success(f"  SHADCNBLOCKS_API_KEY set ({masked})")
                else:
                    print_warning("  SHADCNBLOCKS_API_KEY set but doesn't start with 'sk_live_'")
                    self.warnings.append("Shadcnblocks API key format may be incorrect")
            else:
                print_warning("  SHADCNBLOCKS_API_KEY not found in .env.local")
                self.warnings.append("Shadcnblocks API key not configured")
                print_action("  Add to website/.env.local: SHADCNBLOCKS_API_KEY=sk_live_...")
                print_info("  Get key from: https://www.shadcnblocks.com/dashboard/api")
        else:
            print_error("website/.env.local not found")
            self.issues.append("Website environment file missing")
            print_action("Create website/.env.local with:")
            print("  # Clerk Authentication (REQUIRED)")
            print("  NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_...")
            print("  CLERK_SECRET_KEY=sk_test_...")
            print()
            print("  # shadcnblocks Pro (REQUIRED for Pro blocks)")
            print("  SHADCNBLOCKS_API_KEY=sk_live_...")
            print()
            print_info("Clerk setup: https://clerk.com")
            print_info("shadcnblocks API key: https://www.shadcnblocks.com/dashboard/api")

        # Check components.json registry configuration
        components_json = website_dir / 'components.json'
        if components_json.exists():
            print_success("website/components.json exists")

            try:
                import json
                with open(components_json) as f:
                    config = json.load(f)

                # Check for registries configuration
                if 'registries' in config:
                    print_success("  registries section found")

                    if '@shadcnblocks' in config['registries']:
                        registry = config['registries']['@shadcnblocks']
                        print_success("  @shadcnblocks registry configured")

                        # Check URL format
                        url = registry.get('url', '')
                        if url == 'https://shadcnblocks.com/r/{name}':
                            print_success("  Registry URL is correct")
                        else:
                            print_warning(f"  Registry URL may be incorrect: {url}")
                            print_warning(f"  Expected: https://shadcnblocks.com/r/{{name}}")
                            self.warnings.append("Shadcnblocks registry URL format may be incorrect")
                            print_action("  Update components.json registry URL")

                        # Check for Authorization header
                        headers = registry.get('headers', {})
                        if 'Authorization' in headers:
                            print_success("  Authorization header configured")
                        else:
                            print_warning("  Authorization header missing")
                            self.warnings.append("Shadcnblocks registry missing Authorization header")
                            print_action("  Add to components.json:")
                            print('    "headers": {"Authorization": "Bearer ${SHADCNBLOCKS_API_KEY}"}')
                    else:
                        print_warning("  @shadcnblocks registry not found")
                        self.warnings.append("Shadcnblocks registry not configured")
                        print_action("  See: specs/shadcnblocks-setup.md")
                else:
                    print_warning("  No registries section in components.json")
                    self.warnings.append("Shadcnblocks registry section missing")
                    print_action("  See: specs/shadcnblocks-setup.md")
            except json.JSONDecodeError as e:
                print_warning(f"  Invalid JSON in components.json: {e}")
                self.warnings.append("components.json has invalid JSON")
            except Exception as e:
                print_warning(f"  Could not check components.json: {e}")
                self.warnings.append("Unable to validate components.json")
        else:
            print_warning("website/components.json not found")
            self.warnings.append("components.json missing")
            print_action("Run in website/: pnpm dlx shadcn@latest init")

    def test_connectivity(self):
        """Test actual API connectivity if everything is configured"""
        if self.issues:
            print_warning("Skipping connectivity test - fix configuration issues first")
            return

        print_info("Testing API connectivity...")

        # Test Blogger API
        try:
            from google.oauth2.credentials import Credentials
            from google.auth.transport.requests import Request
            from googleapiclient.discovery import build

            creds = Credentials(
                token=None,
                refresh_token=self.env_vars.get('BLOGGER_REFRESH_TOKEN'),
                client_id=self.env_vars.get('BLOGGER_CLIENT_ID'),
                client_secret=self.env_vars.get('BLOGGER_CLIENT_SECRET'),
                token_uri='https://oauth2.googleapis.com/token'
            )

            # Refresh to get access token
            creds.refresh(Request())
            print_success("Blogger API: Refresh token is valid")

            # Test API call
            service = build('blogger', 'v3', credentials=creds)
            blog = service.blogs().get(blogId=self.blog_config['blogger_blog_id']).execute()
            print_success(f"Blogger API: Connected to '{blog['name']}'")
            print_info(f"   URL: {blog['url']}")
            print_info(f"   Posts: {blog.get('posts', {}).get('totalItems', 0)}")

        except Exception as e:
            print_error(f"Blogger API connection failed: {e}")
            self.issues.append("Blogger API connectivity issue")

            # Provide specific troubleshooting
            error_str = str(e).lower()
            if 'invalid_grant' in error_str:
                print_action("Refresh token expired or invalid. Regenerate it:")
                print_action("  uv run tools/generate_refresh_token.py")
            elif 'not found' in error_str or '404' in error_str:
                print_action("Blog ID not found. Check your Blogger dashboard URL:")
                print_action("  https://www.blogger.com/blog/posts/[YOUR_BLOG_ID]")
            elif 'unauthorized' in error_str or '401' in error_str:
                print_action("Authorization failed. Check OAuth consent screen test users:")
                print_action("  https://console.cloud.google.com/apis/credentials/consent")
            else:
                print_info("See: specs/blog-google-auth.md for troubleshooting")

        # Test Cloudinary
        try:
            import cloudinary
            cloudinary.config(
                cloud_name=self.env_vars.get('CLOUDINARY_CLOUD_NAME'),
                api_key=self.env_vars.get('CLOUDINARY_API_KEY'),
                api_secret=self.env_vars.get('CLOUDINARY_API_SECRET')
            )
            print_success(f"Cloudinary: Configuration valid")
            print_info(f"   Cloud: {self.env_vars.get('CLOUDINARY_CLOUD_NAME')}")

        except Exception as e:
            print_error(f"Cloudinary configuration failed: {e}")
            self.issues.append("Cloudinary configuration issue")
            print_action("Verify credentials at: https://cloudinary.com/console")

    def sync_published_posts(self):
        """Sync published post status from Blogger by calling the sync script"""
        if self.issues:
            return  # Skip if there are configuration issues

        posts_dir = Path('posts')
        if not posts_dir.exists():
            return  # No posts to sync

        # Check if there are any posts with blogger_id (quick check to avoid unnecessary subprocess call)
        has_published = False
        for post_dir in posts_dir.iterdir():
            if post_dir.is_dir() and (post_dir / 'post.md').exists():
                with open(post_dir / 'post.md', 'r') as f:
                    content = f.read()
                    if 'blogger_id:' in content:
                        has_published = True
                        break

        if not has_published:
            return  # No published posts to sync

        try:
            import subprocess
            result = subprocess.run(
                ['uv', 'run', 'tools/sync-publish-status.py'],
                capture_output=True,
                text=True,
                timeout=60
            )

            # Show the sync output directly
            if result.stdout:
                print(result.stdout, end='')

            if result.returncode != 0 and result.stderr:
                print_warning("Sync had issues:")
                print(result.stderr, end='')

        except subprocess.TimeoutExpired:
            print_warning("Sync timed out (you can run manually later)")
            print_action("Run manually: uv run tools/sync-publish-status.py")
        except Exception as e:
            print_warning(f"Could not run sync: {e}")
            print_action("Run manually: uv run tools/sync-publish-status.py")

    def print_summary(self):
        """Print final summary"""
        # Try to sync posts if setup is complete
        self.sync_published_posts()

        print_header("📊 Summary")

        if not self.issues:
            print_success("All checks passed! 🎉")
            print()
            print_info("You're ready to create and publish posts:")
            print("  1. Create a post: posts/YYYY-MM-DD-slug/post.md")
            print("  2. Validate: uv run tools/build.py posts/YYYY-MM-DD-slug/")
            print("  3. Publish: uv run tools/publish.py posts/YYYY-MM-DD-slug/")
            print()
            print_info("Example:")
            print_action("  mkdir -p posts/2025-10-12-my-first-post")
            print_action("  # Edit posts/2025-10-12-my-first-post/post.md")
            print_action("  uv run tools/build.py posts/2025-10-12-my-first-post/")
            print_action("  uv run tools/publish.py posts/2025-10-12-my-first-post/")

        else:
            print_error(f"Found {len(self.issues)} issue(s) to fix:")
            for i, issue in enumerate(self.issues, 1):
                print(f"  {i}. {issue}")
            print()
            print_info("📖 Detailed setup guide: specs/blog-google-auth.md")
            print_info("🔧 After fixing issues, run this script again:")
            print_action("   uv run tools/setup_check.py")

        if self.warnings:
            print()
            print_warning(f"{len(self.warnings)} warning(s):")
            for warning in self.warnings:
                print(f"  - {warning}")

        print(f"\n{Color.BOLD}{'='*60}{Color.END}\n")


def main():
    """Run setup checker"""
    checker = SetupChecker()
    try:
        checker.run()
        sys.exit(0 if not checker.issues else 1)
    except KeyboardInterrupt:
        print("\n\nSetup check interrupted.")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
