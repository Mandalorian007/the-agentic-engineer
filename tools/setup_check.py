#!/usr/bin/env python3
"""
Interactive setup checker for The Agentic Engineer Blog (Next.js).
Guides you through configuration step-by-step with actionable instructions.
"""

from pathlib import Path
import os
import sys
import yaml
import subprocess
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
    """Orchestrates setup validation for Next.js blog"""

    def __init__(self):
        self.issues = []
        self.warnings = []
        self.blog_config = {}

    def run(self):
        """Run all setup checks"""
        print(f"{Color.BOLD}{'='*60}")
        print("🚀 The Agentic Engineer - Setup Verification")
        print("   Next.js Blog + Vercel Deployment")
        print(f"{'='*60}{Color.END}\n")

        # Check in order of setup flow
        checks = [
            ("Python Dependencies", self.check_python_dependencies),
            ("Node.js Dependencies", self.check_node_dependencies),
            ("Configuration Files", self.check_config_files),
            ("OpenAI Setup", self.check_openai),
            ("Blog Configuration", self.check_blog_config),
            ("Next.js Website", self.check_website),
            ("Build Test", self.test_nextjs_build),
        ]

        for section, check_func in checks:
            print_header(f"📋 {section}")
            check_func()

        # Final summary
        self.print_summary()

    def check_python_dependencies(self):
        """Check if Python dependencies are installed"""
        # Check if uv environment is set up
        venv_path = Path('.venv')
        if venv_path.exists():
            print_success("Python virtual environment exists (.venv)")
        else:
            print_error("Virtual environment not found")
            self.issues.append("Missing virtual environment")
            print_action("Run: uv sync")
            return

        # Check for Vale prose linter (optional but recommended)
        try:
            result = subprocess.run(['vale', '--version'],
                                  capture_output=True,
                                  text=True,
                                  timeout=5)
            if result.returncode == 0:
                version = result.stdout.strip().split('\n')[0]
                print_success(f"Vale prose linter installed ({version})")

                # Sync Vale styles
                print_info("   Syncing Vale style packages...")
                sync_result = subprocess.run(['vale', 'sync'],
                                            capture_output=True,
                                            text=True,
                                            timeout=30)
                if sync_result.returncode == 0:
                    print_success("   Vale styles synced")
                else:
                    print_warning("   Vale sync had issues (may be okay if styles exist)")
            else:
                print_warning("Vale installed but version check failed")
                self.warnings.append("Vale may not be properly configured")
        except FileNotFoundError:
            print_warning("Vale prose linter not found (optional)")
            self.warnings.append("Vale not installed - prose linting unavailable")
            print_info("   Optional: Install with: brew install vale")
            print_info("   Then run: vale sync")
        except subprocess.TimeoutExpired:
            print_warning("Vale check timed out")
            self.warnings.append("Vale may not be working correctly")

    def check_node_dependencies(self):
        """Check if Node.js and pnpm are installed"""
        # Check for Node.js
        try:
            result = subprocess.run(['node', '--version'],
                                  capture_output=True,
                                  text=True,
                                  timeout=5)
            if result.returncode == 0:
                version = result.stdout.strip()
                print_success(f"Node.js installed ({version})")

                # Check version is 18+
                major_version = int(version.lstrip('v').split('.')[0])
                if major_version < 18:
                    print_warning(f"Node.js {version} is below recommended 18+")
                    self.warnings.append("Node.js version should be 18 or higher")
            else:
                print_error("Node.js check failed")
                self.issues.append("Node.js may not be working correctly")
        except FileNotFoundError:
            print_error("Node.js not found")
            self.issues.append("Node.js is required for Next.js")
            print_action("Install Node.js 18+: https://nodejs.org/")
            return
        except subprocess.TimeoutExpired:
            print_warning("Node.js check timed out")
            self.warnings.append("Node.js may not be working correctly")

        # Check for pnpm
        try:
            result = subprocess.run(['pnpm', '--version'],
                                  capture_output=True,
                                  text=True,
                                  timeout=5)
            if result.returncode == 0:
                version = result.stdout.strip()
                print_success(f"pnpm installed ({version})")
            else:
                print_error("pnpm check failed")
                self.issues.append("pnpm may not be working correctly")
        except FileNotFoundError:
            print_error("pnpm not found")
            self.issues.append("pnpm is required for Next.js dependencies")
            print_action("Install pnpm: npm install -g pnpm")
            return
        except subprocess.TimeoutExpired:
            print_warning("pnpm check timed out")
            self.warnings.append("pnpm may not be working correctly")

        # Check if website dependencies are installed
        website_node_modules = Path('website/node_modules')
        if website_node_modules.exists():
            print_success("Next.js dependencies installed (website/node_modules exists)")
        else:
            print_warning("Next.js dependencies not installed")
            self.warnings.append("Website dependencies missing")
            print_action("Run: cd website && pnpm install")

    def check_config_files(self):
        """Check if required config files exist"""
        # Root .env.local (for Python tools)
        env_path = Path('.env.local')
        if env_path.exists():
            print_success(".env.local exists (for Python tools)")
        else:
            print_warning(".env.local not found (optional)")
            print_info("   Only needed if using AI image generation")
            print_info("   Create with: OPENAI_API_KEY=your-key-here")

        # blog-config.yaml
        config_path = Path('blog-config.yaml')
        if config_path.exists():
            print_success("blog-config.yaml exists")
        else:
            print_error("blog-config.yaml not found")
            self.issues.append("Missing blog-config.yaml")
            print_action("Create blog-config.yaml with blog settings")
            print_info("   See README.md for configuration format")

    def check_openai(self):
        """Check OpenAI API key setup"""
        env_path = Path('.env.local')
        if env_path.exists():
            load_dotenv(env_path)

        api_key = os.getenv('OPENAI_API_KEY')

        if api_key:
            masked = api_key[:8] + '...' if len(api_key) > 8 else '***'
            print_success(f"OPENAI_API_KEY set ({masked})")
            print_info("   Used by: tools/generate_image.py")
        else:
            print_warning("OPENAI_API_KEY not set")
            self.warnings.append("OpenAI API key not configured")
            print_info("   Image generation will not work without this")
            print_action("Optional: Add OPENAI_API_KEY to .env.local")
            print_info("   Get key from: https://platform.openai.com/api-keys")

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
            'domain': 'Your domain name',
            'categories': 'List of 7 categories',
        }

        for field, description in required_fields.items():
            if field in self.blog_config and self.blog_config[field]:
                if field == 'categories':
                    categories = self.blog_config[field]
                    expected = [
                        'tutorials', 'case-studies', 'guides', 'lists',
                        'comparisons', 'problem-solution', 'opinions'
                    ]
                    if set(categories) == set(expected):
                        print_success(f"categories: All 7 required categories present")
                    else:
                        print_error(f"categories: Missing or extra categories")
                        self.issues.append("Invalid categories in blog-config.yaml")
                        print_info(f"   Expected: {expected}")
                        print_info(f"   Found: {categories}")
                else:
                    print_success(f"{field}: {self.blog_config[field]}")
            else:
                print_error(f"{field} not set - {description}")
                self.issues.append(f"Missing {field} in blog-config.yaml")

    def check_website(self):
        """Check Next.js website directory structure"""
        website_dir = Path('website')

        if not website_dir.exists():
            print_error("website/ directory not found")
            self.issues.append("Next.js website directory missing")
            print_action("Initialize Next.js site or clone from repository")
            return

        print_success("website/ directory exists")

        # Check key directories
        required_dirs = {
            'app': 'Next.js app directory (routes)',
            'components': 'React components',
            'content/posts': 'MDX blog posts',
            'public/blog': 'Blog post images',
            'lib': 'TypeScript utilities',
        }

        for dir_path, description in required_dirs.items():
            full_path = website_dir / dir_path
            if full_path.exists():
                print_success(f"  {dir_path}/ exists - {description}")
            else:
                print_warning(f"  {dir_path}/ not found - {description}")
                self.warnings.append(f"Missing {dir_path}/ directory")

        # Check for package.json
        package_json = website_dir / 'package.json'
        if package_json.exists():
            print_success("  package.json exists")

            # Check if dependencies are installed
            node_modules = website_dir / 'node_modules'
            if not node_modules.exists():
                print_warning("  node_modules not found - dependencies not installed")
                self.warnings.append("Website dependencies not installed")
                print_action("  Run: cd website && pnpm install")
        else:
            print_error("  package.json not found")
            self.issues.append("package.json missing")

        # Check for existing posts
        content_dir = website_dir / 'content/posts'
        if content_dir.exists():
            mdx_files = list(content_dir.glob('*.mdx'))
            if mdx_files:
                print_success(f"  Found {len(mdx_files)} MDX post(s)")
            else:
                print_info("  No MDX posts found yet (expected for new setup)")

        # Check for next.config.ts
        next_config = website_dir / 'next.config.ts'
        if next_config.exists():
            print_success("  next.config.ts exists")
        else:
            print_warning("  next.config.ts not found")
            self.warnings.append("Next.js config missing")

    def test_nextjs_build(self):
        """Test if Next.js build works"""
        if self.issues:
            print_warning("Skipping build test - fix configuration issues first")
            return

        website_dir = Path('website')
        if not website_dir.exists():
            print_warning("Cannot test build - website/ directory not found")
            return

        node_modules = website_dir / 'node_modules'
        if not node_modules.exists():
            print_warning("Cannot test build - dependencies not installed")
            print_action("Run: cd website && pnpm install")
            return

        print_info("Testing Next.js build (this may take a minute)...")

        try:
            result = subprocess.run(
                ['pnpm', 'run', 'build'],
                cwd=website_dir,
                capture_output=True,
                text=True,
                timeout=120
            )

            if result.returncode == 0:
                print_success("Next.js build succeeded!")
                print_info("   Site is ready for deployment to Vercel")
            else:
                print_error("Next.js build failed")
                self.issues.append("Build errors detected")

                # Show relevant error lines
                if result.stderr:
                    error_lines = result.stderr.split('\n')
                    print_info("   Error details:")
                    for line in error_lines[-10:]:  # Last 10 lines
                        if line.strip():
                            print(f"   {line}")

                print_action("Fix build errors and run: cd website && pnpm run build")

        except subprocess.TimeoutExpired:
            print_warning("Build test timed out (may be normal for first build)")
            self.warnings.append("Build test exceeded 2 minutes")
            print_info("   Try running manually: cd website && pnpm run build")
        except Exception as e:
            print_error(f"Could not test build: {e}")
            self.warnings.append("Unable to run build test")

    def print_summary(self):
        """Print final summary"""
        print_header("📊 Summary")

        if not self.issues:
            print_success("All checks passed! 🎉")
            print()
            print_info("Your Next.js blog is ready to use:")
            print()
            print("  Development workflow:")
            print_action("    cd website && pnpm dev")
            print_info("    Visit: http://localhost:3000")
            print()
            print("  Create a blog post:")
            print_action("    /create-post Your blog post idea here")
            print()
            print("  Quality check and build:")
            print_action("    /quality-check website/content/posts/YYYY-MM-DD-slug.mdx")
            print_action("    /build")
            print()
            print("  Deploy to Vercel:")
            print_action("    git add . && git commit -m 'Add post' && git push")
            print_info("    Vercel auto-deploys on push!")

        else:
            print_error(f"Found {len(self.issues)} issue(s) to fix:")
            for i, issue in enumerate(self.issues, 1):
                print(f"  {i}. {issue}")
            print()
            print_info("📖 Documentation: README.md")
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
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
