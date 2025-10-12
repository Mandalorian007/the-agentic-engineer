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
            ("Blog Configuration", self.check_blog_config),
            ("Connectivity Test", self.test_connectivity),
        ]

        for section, check_func in checks:
            print_header(f"📋 {section}")
            check_func()

        # Final summary
        self.print_summary()

    def check_dependencies(self):
        """Check if required Python packages are installed"""
        import subprocess

        required_packages = [
            ('google.auth', 'google-auth'),
            ('google_auth_oauthlib', 'google-auth-oauthlib'),
            ('googleapiclient', 'google-api-python-client'),
            ('markdown_it', 'markdown-it-py'),
            ('PIL', 'Pillow'),
            ('cloudinary', 'cloudinary'),
            ('yaml', 'PyYAML'),
            ('dotenv', 'python-dotenv'),
            ('pygments', 'Pygments'),
        ]

        missing = []
        for module_name, package_name in required_packages:
            try:
                __import__(module_name)
                print_success(f"{package_name} installed")
            except ImportError:
                missing.append(package_name)
                print_error(f"{package_name} not found")

        if missing:
            self.issues.append("Missing Python dependencies")
            print_action("Run: uv sync")
        else:
            print_success("All Python dependencies installed")

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

    def print_summary(self):
        """Print final summary"""
        print_header("📊 Summary")

        if not self.issues:
            print_success("All checks passed! 🎉")
            print()
            print_info("You're ready to create and publish posts:")
            print("  1. Create a post: posts/YYYY-MM-DD-slug/post.md")
            print("  2. Validate: uv run build.py posts/YYYY-MM-DD-slug/")
            print("  3. Publish: uv run publish.py posts/YYYY-MM-DD-slug/")
            print()
            print_info("Example:")
            print_action("  mkdir -p posts/2025-10-12-my-first-post")
            print_action("  # Edit posts/2025-10-12-my-first-post/post.md")
            print_action("  uv run build.py posts/2025-10-12-my-first-post/")
            print_action("  uv run publish.py posts/2025-10-12-my-first-post/")

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
