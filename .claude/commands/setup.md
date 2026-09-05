# Verify Setup

Run `uv run tools/setup_check.py` to validate the local environment.

It checks:
- Python dependencies (uv virtual environment, Vale prose linter)
- Node dependencies and version
- Configuration files (`.env.local`, `blog-config.yaml`)
- OpenAI API key (optional, only for `tools/generate_embedding.py`)
- Newsletter stream (the `newsletter:` block, the issues directory, `BUTTONDOWN_API_KEY`)
- Blog configuration (name, domain, the 7 categories)
- Next.js website presence and configuration
- A build test

Note that it runs a production build at the end, so stop `pnpm dev` first.

## Environment variables

### Root `.env.local` — Python tooling

```bash
# Buttondown account key: creates subscribers and emails.
# Same value goes in website/.env.local, Vercel, and GitHub Actions.
BUTTONDOWN_API_KEY=xxx

# Buttondown newsletter key: writes newsletter settings. A different key.
# See newsletter/buttondown-api.md.
BUTTONDOWN_NEWSLETTER_KEY=xxx

# Discord webhook for the Saturday content buffer check.
# Sending is opt-in: only --notify actually posts.
LOW_CONTENT_WEBHOOK=https://discord.com/api/webhooks/...

# Optional: image embedding generation only.
OPENAI_API_KEY=xxx

# Twitter/X, for the daily post-to-twitter workflow.
TWITTER_API_KEY=xxx
TWITTER_API_KEY_SECRET=xxx
TWITTER_ACCESS_TOKEN=xxx
TWITTER_ACCESS_TOKEN_SECRET=xxx
```

### `website/.env.local` — Next.js

See `website/.env.example` for the full annotated list.

```bash
BUTTONDOWN_API_KEY=xxx      # /api/subscribe
REVALIDATE_SECRET=xxx       # /api/revalidate, must match the GitHub secret
PREVIEW_UNPUBLISHED=true    # show scheduled posts and unsent issues locally
```

`SHADCNBLOCKS_API_KEY` is needed only when pulling a new Pro block through the
registry in `website/components.json`. The site builds and runs without it.

## Deployment targets

These live outside the repo and no local check can see them.

**Vercel** (Production): `BUTTONDOWN_API_KEY`, `REVALIDATE_SECRET`.
Leave `PREVIEW_UNPUBLISHED` unset here, or scheduled content becomes public.

**Vercel** (Preview): set `PREVIEW_UNPUBLISHED=true` so a preview deploy can
render scheduled posts and unsent issues. Those pages are noindex either way.

**GitHub Actions secrets**: `BUTTONDOWN_API_KEY`, `REVALIDATE_SECRET`,
`LOW_CONTENT_WEBHOOK`, and the four Twitter values.

**Buttondown dashboard**: the newsletter name, From name, reply-to address,
description, and confirmation-page copy are set by hand. `newsletter/buttondown-settings.md`
holds the exact strings to paste.
