# Verify Setup

Run the comprehensive setup verification script using `uv run tools/setup_check.py` to validate:
- Python dependencies installation
- Configuration files (.env.local, blog-config.yaml)
- Google OAuth credentials (client ID, secret, refresh token)
- Cloudinary credentials (cloud name, API key, secret)
- Blog configuration (blog name, blog ID)
- API connectivity (Blogger API and Cloudinary)
- Next.js website configuration (website/.env, shadcnblocks registry)

The script provides actionable guidance for each missing or misconfigured component, with specific commands to fix issues and links to detailed documentation.
