# Verify Setup

Run the comprehensive setup verification script using `uv run tools/setup_check.py` to validate:
- Python dependencies installation (uv virtual environment, Vale prose linter)
- Configuration files (.env.local, blog-config.yaml)
- Google OAuth credentials (client ID, secret, refresh token)
- Cloudinary credentials (cloud name, API key, secret)
- OpenAI API key (optional, for AI image generation)
- Blog configuration (blog name, blog ID)
- Next.js website configuration (website/.env.local)
  - **Clerk authentication** (publishable key, secret key) - **REQUIRED**
  - shadcnblocks Pro API key - **REQUIRED** for Pro blocks
  - components.json registry configuration
- API connectivity (Blogger API and Cloudinary)

## Required Environment Variables

### Root `.env.local` (Python blog automation)
```bash
BLOGGER_CLIENT_ID=xxx
BLOGGER_CLIENT_SECRET=xxx
BLOGGER_REFRESH_TOKEN=xxx
CLOUDINARY_CLOUD_NAME=xxx
CLOUDINARY_API_KEY=xxx
CLOUDINARY_API_SECRET=xxx
OPENAI_API_KEY=xxx  # Optional: for AI image generation
```

### `website/.env.local` (Next.js website)
```bash
# Clerk Authentication - REQUIRED
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_xxx
CLERK_SECRET_KEY=sk_test_xxx

# shadcnblocks Pro - REQUIRED for Pro blocks (blog27, navbar8, footer16, etc.)
SHADCNBLOCKS_API_KEY=sk_live_xxx
```

**Note**: Both Clerk and shadcnblocks credentials are validated by the setup check script and are required for the Next.js website to function properly.

## Clerk Setup Steps

1. **Create a Clerk account** at https://clerk.com
2. **Create a new project** in the Clerk dashboard
3. **Configure authentication methods** (email/password, Google OAuth, etc.)
4. **Set callback URLs**:
   - Local development: `http://localhost:3000`
   - Production: `https://agentic-engineer.com`
5. **Copy API keys** from dashboard:
   - Publishable Key → `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY`
   - Secret Key → `CLERK_SECRET_KEY`
6. **Add keys to `website/.env.local`** (create file if it doesn't exist)
7. **Verify**: Run `cd website && pnpm dev` to test authentication

The script provides actionable guidance for each missing or misconfigured component, with specific commands to fix issues and links to detailed documentation.
