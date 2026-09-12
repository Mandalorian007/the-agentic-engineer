# The Agentic Engineer

Source for [agentic-engineer.com](https://agentic-engineer.com). The blog, and the
agent pipeline that writes, lints, and ships it.

## What you're looking at

If you got here from the site: this repo is the argument. The posts about encoding
your own workflow into agents were themselves produced by an encoded workflow, and
it's all here.

Worth reading first:

| Where | What's in it |
|---|---|
| [`.claude/`](.claude/) | Slash commands and hooks. This is the encoded workflow. |
| [`tools/`](tools/) | Scheduling, SEO checks, social validation, image conversion. |
| [`lib/`](lib/) | Frontmatter parsing, publish-date math, post validators. |
| [`.vale.ini`](.vale.ini) | Prose linting. Posts fail if the writing is sloppy. |
| [`.github/workflows/`](.github/workflows/) | Scheduled social posting and content-buffer checks. |
| [`website/content/posts/`](website/content/posts/) | Every post, as source. |
| [`newsletter/`](newsletter/) | The newsletter's copy, and notes on the Buttondown API. |

The commands in `.claude/commands/` are the interesting part. One of them,
`/ship`, encodes the whole path from an idea to a Monday: the post, the
newsletter issue derived from it, the social copy, the surface kit for the
part a person does by hand, and the commit. Nothing in this repo is written
by hand from a blank file.

## The weekly routine

If you are coming back to this repo after a while, this is all you need.

| When | What | Command |
|---|---|---|
| Any day | Write next Monday's post and issue | `/ship <idea>` |
| Publish morning (Monday) | Put the post in front of people, by hand | Open Discord, copy the surface kit: LinkedIn text post; Hacker News (claim posts) or Reddit (tutorials). Answer replies. |
| Saturday | Discord tells you which Mondays are empty | `/check-buffer` any time to see it yourself |
| Monthly | Real readers, not crawlers | `/traffic` |

`/ship` does everything except the Monday paste: next open Monday, the post,
the newsletter issue derived from it, Twitter and LinkedIn copy, the surface
kit, both quality reviews, commit, push. Nothing goes live at push; Vercel,
the issue sender, and the tweet all fire on the post's date. Say "preview
only" to stop before the push.

The cadence is weekly, Mondays, set in `blog-config.yaml`. To pull a post
into an earlier gap: `uv run tools/move_post_date.py <from> <to>`, again with
`--stream newsletter` for its issue, and rename its `surface/` kit.

What changed on 2026-09-12, in case you remember the old shape: the two
pipelines (`/create-post-pipeline`, `/create-issue-pipeline`) became `/ship`;
issues are derived from posts instead of written separately; cadence went
from every other Monday to every Monday; `surface/` and the Discord kit drop
are new; `/traffic` is new.

## Features

- ✅ **Next.js 16**: Modern static site generation with App Router
- ✅ **MDX Content**: Write in MDX with frontmatter, deploy with git push
- ✅ **AI Content Generation**: Complete blog posts with AI-generated images via the `aitk` CLI
- ✅ **Social Media Automation**: Auto-generate and post to Twitter/LinkedIn via GitHub Actions
- ✅ **Quality Checks**: SEO analysis + Vale prose linting + Social validation
- ✅ **Scheduled Publishing**: Configure publish cadence (weekly/monthly), posts auto-appear on schedule
- ✅ **Content Buffer Monitoring**: Discord notifications for content pipeline status
- ✅ **Category System**: 7 hardcoded categories for consistent organization
- ✅ **Theme Toggle**: Light/dark mode with next-themes
- ✅ **Vercel Deploy**: Automatic deployment on git push

## Quick Start

### 1. Setup (One-time)

**Requirements:**
- Node.js 18+ and pnpm
- Python 3.10+ (for content generation tools)
- [`aitk`](#ai-toolkit-aitk) CLI installed and configured (`aitk config`) — used for image generation
- Vale (optional, for prose linting): `brew install vale`

**Configuration:**

1. **Install dependencies:**
   ```bash
   # Python tools
   uv sync

   # Next.js site
   cd website && pnpm install
   ```

2. **Configure environment:**
   ```bash
   # Image generation credentials (one-time, interactive)
   aitk config

   # Optional: only needed for tools/generate_embedding.py
   # echo "OPENAI_API_KEY=your-key-here" > .env.local
   ```

3. **Verify setup:**
   ```bash
   uv run tools/setup_check.py
   ```
   This validates your entire setup and provides actionable feedback.

4. **Start development server:**
   ```bash
   cd website && pnpm dev
   ```
   Visit http://localhost:3000

### 2. Ship

```bash
/ship Your blog post idea goes here
```

One command, one Monday. It runs, in order:

1. Next open Monday from the schedule
2. The post: MDX with AI-generated hero images, humanized against the voice anchor
3. The newsletter issue, derived from the post (`/create-issue --from-post`), humanized
4. Twitter and LinkedIn copy into the post's frontmatter
5. The surface kit: `surface/YYYY-MM-DD-slug.md`, the finished text for the part a person does by hand (LinkedIn post, Hacker News title and author comment for claim posts, Reddit text post for tutorials)
6. Quality review of both files (SEO, Vale, social validation, email preview)
7. Commit on `main` and push

Nothing goes live at push. Vercel publishes the post at its frontmatter date, `send-issue.yml` sends the issue that morning, and `post-to-twitter.yml` tweets and drops the surface kit into Discord so the manual part is a copy-paste from a phone. Say "preview only" to stop before the push.

The steps are still standalone commands if one needs redoing.

## Workflow

### Publish morning

The pipeline does everything except the part that only works when a person does it: putting the post in front of people. On publish morning the surface kit is in Discord. Post it on LinkedIn as text (link in the first comment). If it's a claim post, submit it to Hacker News and leave the author comment. If it's a tutorial, post it to r/ClaudeAI as a text post. Answer replies. That's the job.

### Available Commands

**Entry point:**
- `/ship <idea>` - Idea to pushed commit: post, issue, socials, surface kit, review

**Individual Steps — Posts:**
- `/create-post <idea>` - Generate MDX blog post with AI-generated images
- `/generate-socials <path>` - Generate social media posts for Twitter & LinkedIn
- `/mdx-quality-review <path>` - Run SEO + Vale prose linting + Social validation

**Individual Steps — Issues:**
- `/create-issue --from-post <path>` - Newsletter issue derived from a post (what `/ship` runs)
- `/create-issue` - Hand-written issue for a week without a post (rare)
- `/issue-quality-review <path>` - Run Vale + issue_check + email preview

**Both Streams:**
- `/check-buffer` - Slot ledger showing which publish dates are still open
- `/traffic` - Human-filtered traffic report (Vercel, Search Console, Buttondown), interpreted

### Scheduling Posts

Posts with future dates are automatically hidden until that date:

```yaml
---
title: "My Future Post"
description: "This post won't appear until the date arrives"
date: "2025-12-25T10:00:00Z"  # Future date
category: "tutorials"
hashtags: ["next.js", "automation"]
---
```

Next.js ISR (Incremental Static Regeneration) rebuilds pages hourly, so posts appear within ~1 hour of their scheduled time.

## Post Format

### File Structure

```
website/
├── content/posts/
│   └── 2025-10-12-my-post.mdx          # Single MDX file
└── public/blog/2025-10-12-my-post/
    ├── hero-automation.webp            # Images in WebP
    └── diagram-architecture.webp
```

### Frontmatter Schema

```yaml
---
title: "Post Title"                              # Required, 30-60 chars optimal
description: "SEO description for meta tags"     # Required, 150-160 chars
date: "2025-10-12T10:00:00Z"                    # Required, ISO 8601 with quotes
category: "tutorials"                            # Required, one of 7 categories
hashtags: ["python", "automation", "ai"]         # Optional, freeform display-only

social:                                          # Optional, generated by /generate-socials
  twitter:
    text: "🚀 Engaging tweet about the post (max 250 chars)"
  linkedin:
    text: "Professional LinkedIn post (max 2970 chars)"
---
```

### Categories (Required)

Every post must have ONE category:

- **tutorials** - Step-by-step how-to guides
- **case-studies** - Real-world project showcases
- **guides** - Beginner-friendly fundamentals
- **lists** - Tips, tools, strategies
- **comparisons** - Product/approach comparisons
- **problem-solution** - Addressing pain points
- **opinions** - Perspectives, myth-busting

### Image References

Use relative paths from MDX file location in MDX:

```markdown
![Alt text describing image](../../public/blog/2025-10-12-my-post/hero-automation.webp)
```

The relative path goes from `website/content/posts/` to `website/public/blog/`. Next.js automatically converts these to `/blog/...` URLs at render time, and IDE markdown preview can resolve the images locally.

## Configuration

### blog-config.yaml

```yaml
blog_name: "The Agentic Engineer"
domain: "agentic-engineer.com"

website_dir: "website"
content_dir: "website/content/posts"
public_images_dir: "website/public/blog"

image_generation:
  default_size: "1024x1024"
  format: "webp"
  quality: 85

publishing:
  frequency: "biweekly"
  day: "monday"              # Publish on Mondays
  anchor: "2026-09-07"       # any date already on the cadence
  time: "11:00:00"           # Publish time (UTC) - 6am EST

categories:
  - tutorials
  - case-studies
  - guides
  - lists
  - comparisons
  - problem-solution
  - opinions
```

### .env.local

```bash
# Optional: only needed for tools/generate_embedding.py
# (image generation now uses aitk config, not .env.local)
OPENAI_API_KEY=your-key-here

# Optional: Discord webhook for low content buffer notifications
LOW_CONTENT_WEBHOOK=https://discord.com/api/webhooks/...

# Newsletter. These are two different Buttondown keys and they are not
# interchangeable — see newsletter/buttondown-api.md.
#   Account key: subscribers and emails. Also set in website/.env.local,
#   Vercel, and GitHub Actions.
BUTTONDOWN_API_KEY=...
#   Newsletter key: newsletter settings. Found in the `api_key` field of
#   GET /v1/newsletters. Local tooling only. Do not deploy it anywhere.
BUTTONDOWN_NEWSLETTER_KEY=...

# Optional: Search Console feed for tools/traffic_report.py.
# Service-account JSON key; setup steps in docs/traffic-report.md.
GSC_SERVICE_ACCOUNT_FILE=/path/to/service-account.json
```

## Quality Checks

### SEO Analysis

```bash
uv run tools/seo_check.py website/content/posts/2025-10-12-my-post.mdx
```

**Checks:**
- ✅ Title length (30-60 chars)
- ✅ Description (150-160 chars, required)
- ✅ Category validation (one of 7 options)
- ✅ Heading structure (single H1, proper hierarchy)
- ✅ Content length (300+ words)
- ✅ Image alt text
- ✅ Internal/external links

### Prose Linting with Vale

Vale checks writing style and readability:

```bash
# Install
brew install vale
vale sync

# Lint a post
vale website/content/posts/2025-10-12-my-post.mdx
```

Vale configuration in `.vale.ini`:
- **write-good** rules for clear writing
- **SEO** custom rules
- Ignores code blocks and frontmatter

## Image Generation

Image generation is handled by the [`aitk`](#ai-toolkit-aitk) CLI (OpenAI GPT Image backend, writes WebP directly):

```bash
aitk image generate '<detailed prompt>' \
  -o website/public/blog/YYYY-MM-DD-slug/image.webp \
  -s 1536x1024 -q high -f webp
```

**Example:**
```bash
aitk image generate \
  'modern minimalist illustration of AI automation, blue and purple gradient, clean tech aesthetic, isometric view' \
  -o website/public/blog/2025-10-12-my-post/hero.webp \
  -s 1536x1024 -q high -f webp
```

**Flag notes:**
- Use **single quotes** around the prompt (per `aitk image generate --help`)
- `-s` accepts `1024x1024`, `1536x1024` (landscape, recommended for heroes), or `1024x1536`
- `-q` accepts `low`, `medium`, `high`
- `-f` accepts `png`, `jpeg`, `webp`

**Prompt Tips:**
- Specify style (minimalist, modern, flat design)
- Include colors (blue gradient, warm tones)
- Add perspective (isometric, top-down)
- Describe mood (professional, energetic)

## Humanizing Posts (Voice Pass)

After a post is drafted (by `/create-post` or by hand), an optional voice pass through the [`blader/humanizer`](https://github.com/blader/humanizer) Claude Code skill removes common AI tells (significance inflation, copula avoidance, AI-vocabulary, false ranges, rule-of-three filler, etc.) and re-injects the author's voice.

**Install (one-time, per machine):**
```bash
mkdir -p ~/.claude/skills
git clone https://github.com/blader/humanizer.git ~/.claude/skills/humanizer
```

**Usage — always pass a voice sample** to avoid homogenizing the blog's voice. The canonical voice sample for this blog is `website/content/posts/2026-01-19-ai-toolkit-escape-ecosystem-lock-in.mdx`:
```
/humanizer
Humanize the post at website/content/posts/<your-post>.mdx.
Use my writing style from website/content/posts/2026-01-19-ai-toolkit-escape-ecosystem-lock-in.mdx as a reference.
```

**Pipeline order:** the `/ship` orchestrator runs humanizer **between `/create-post` and `/generate-socials`** so socials reflect the humanized body. If you run steps manually, follow the same order.

**Style rules for this blog (override humanizer defaults):**
- **Minimize em dashes** — em dashes are old voice for this site; apply pattern #14 aggressively.
- **Do not un-hyphenate technical compound modifiers** — skip pattern #26 for terms like `real-time`, `end-to-end`, `vendor-agnostic`, `plug-and-play`, `hands-on-keyboard`.
- **Preserve product names** — Claude Code, Codex, Cursor, MCP, marketplace plugins, etc.
- **Do not rewrite the `/services` closing CTA** — wording is load-bearing for conversion.

## AI Toolkit (aitk)

This project uses [`aitk`](https://github.com/clipisode/aitk) (AI Toolkit CLI) as the unified surface for AI-backed utilities.

**One-time setup:**
```bash
aitk config           # interactive credential setup (OpenAI, ElevenLabs, etc.)
aitk --help           # list all subcommands
```

**Common needs in this project:**

| Need | Command |
|---|---|
| Generate a hero/diagram image for a blog post | `aitk image generate '<prompt>' -o <path>.webp -s 1536x1024 -q high -f webp` |
| Edit an existing image with a text prompt | `aitk image edit <input> '<prompt>'` |
| Web search (ad-hoc research) | `aitk search '<query>'` |
| Scrape a page for content research | `aitk scrape page <url>` |
| Generate narration/voiceover audio | `aitk audio ...` |
| Generate short video clips | `aitk video ...` |

**Where this matters in the pipeline:**
- `/create-post` (via Claude Code) calls `aitk image generate` for hero and inline images
- Interactive research can use `aitk search` / `aitk scrape` from the shell, or the existing MCP servers from inside Claude Code

Run `aitk <subcommand> --help` for full flag details on any command.

## Publishing Schedule

The publishing schedule is configurable in `blog-config.yaml`:

```yaml
# Weekly (every Monday) - what this site uses
publishing:
  frequency: "weekly"
  days: ["monday"]
  time: "11:00:00"       # Publish time (UTC) - 6am EST

# Biweekly (every other Monday)
publishing:
  frequency: "biweekly"
  day: "monday"
  anchor: "2026-09-07"   # any date already on the cadence
  time: "11:00:00"

# Monthly (1st and 3rd Monday of each month)
publishing:
  frequency: "monthly"
  day: "monday"
  weeks_of_month: [1, 3]
  time: "11:00:00"
```

`biweekly` and `monthly` are not interchangeable. A `weeks_of_month: [1, 3]`
schedule skips a week whenever a month's 3rd Monday falls early, so one or two
gaps a year stretch to 21 days and the year yields 24 slots. `biweekly` strides
a fixed 14 days from `anchor`, ignoring month boundaries, for 26 slots a year.
Shift the anchor by any multiple of 14 days and nothing changes.

Get the next available publish date:

```bash
uv run tools/next_publish_date.py
```

Output:
```
Next available publish date (2nd Monday of each month):
----------------------------------------
Directory name: 2026-04-13-your-slug-here
Frontmatter date: 2026-04-13T11:00:00Z
Day: Monday, April 13, 2026
```

**Changing frequency:** Just edit `blog-config.yaml` to change the publishing cadence. The entire content pipeline (date calculation, buffer monitoring) automatically adapts.

### Moving Posts to New Dates

Need to reschedule a post? Use the move tool:

```bash
# Preview what will change (dry run)
uv run tools/move_post_date.py 2025-10-27 2025-10-23 --dry-run

# Actually move the post
uv run tools/move_post_date.py 2025-10-27 2025-10-23
```

**What it does:**
- ✅ Renames MDX file with new date
- ✅ Updates frontmatter `date` field
- ✅ Renames image directory
- ✅ Updates all image references in content

**Use cases:**
- Adjusting to a new publishing schedule (e.g., weekly → biweekly)
- Filling gaps in the content calendar
- Moving posts earlier/later based on priorities

## Traffic Report

The Vercel dashboard is not the source of truth for this site: roughly three
quarters of what it counts is datacenter crawler traffic with no referrer.
`tools/traffic_report.py` separates readers from crawlers and lays three feeds
side by side, and `/traffic` runs it and interprets the result.

```bash
uv run tools/traffic_report.py              # last 28 days vs the prior 28
uv run tools/traffic_report.py --days 90
uv run tools/traffic_report.py --since 2025-10-13
uv run tools/traffic_report.py --json
```

- **Vercel Web Analytics** through the logged-in `vercel` CLI (no token needed
  locally). Visitors by day, page, referrer, country, device.
- **Google Search Console** (optional): real search clicks and the queries.
  Needs a service account; see [`docs/traffic-report.md`](docs/traffic-report.md).
- **Buttondown**: subscriber count and new subscribers in the window.

A visitor counts as human if they arrived with a referrer or came direct from
a trusted country (`analytics.trusted_countries` in `blog-config.yaml`). The
report also flags burst days and a low mobile share, which is how a bot fleet
spoofing a search referrer shows up. Full notes in `docs/traffic-report.md`.

## Social Media Automation

The publish-day workflow (`.github/workflows/post-to-twitter.yml`) does two things when a post goes live: tweets it, and drops the post's surface kit into Discord. The tweet is automated because a tweet from a small account is worth exactly what automation costs. LinkedIn, Hacker News, and Reddit are not automated on purpose: they distribute posts from people who show up in the thread, and automating them gets accounts banned.

### How It Works

1. **`/ship` writes the social copy** into the post's frontmatter under `social:` and the surface kit into `surface/`
2. **Posts go live daily at 6am EST** (11am UTC) via ISR
3. **GitHub Actions runs at 6:30am EST** (11:30am UTC): `post_to_twitter.py` tweets, then `notify_surface.py` posts the surface kit to the Discord channel (`LOW_CONTENT_WEBHOOK`)
4. **You post the kit** on LinkedIn, and on HN or Reddit depending on the post's shape

This standardized daily schedule means you can publish on ANY day of the week - just schedule a post for that date!

### Setup

1. **X developer App** — at [console.x.com](https://console.x.com), create an App inside a Project with **Read and Write** permission. OAuth 1.0a User Context is the auth flow used; tweepy 4.16+ handles it.

2. **Fund Pay-Per-Use** — the X Free tier was deprecated Feb 6, 2026. The App's account needs a positive credit balance to post.
   - **Billing → Spending controls** → set a spending limit ($5/month is ~12× this pipeline's real usage).
   - **Auto-recharge** is recommended (trigger ~$2, refill $10) so the bot doesn't silently stall when credits run out.
   - **Cost per tweet:** $0.20 (every tweet contains a URL, which puts it in the URL-rate bucket). At weekly cadence that's ~$0.80/month.

3. **Add Twitter credentials as GitHub secrets:**
   - Go to Settings → Secrets and variables → Actions
   - Add these secrets:
     - `TWITTER_API_KEY`
     - `TWITTER_API_KEY_SECRET`
     - `TWITTER_ACCESS_TOKEN`
     - `TWITTER_ACCESS_TOKEN_SECRET`

4. **GitHub Actions workflows:**
   - `.github/workflows/post-to-twitter.yml` - Runs daily at 6:30am EST (11:30am UTC)
   - Posts go live at 6am EST (11am UTC), tweets sent 30 minutes later
   - Manually trigger via GitHub UI for testing

### Platform Requirements

**Twitter:**
- Max 250 chars (reserves 30 for URL)
- Casual, engaging tone
- Emojis encouraged

**LinkedIn (Future):**
- Max 2970 chars (reserves 30 for URL)
- Professional tone
- Longer, detailed posts

### Manual Testing

```bash
# Test Twitter posting locally (uses .env.local)
uv run tools/post_to_twitter.py --dry-run

# Preview the surface kit Discord message for a date
uv run tools/notify_surface.py --dry-run --date 2026-10-12
```

## Content Buffer Monitoring

A Discord message every Saturday showing which upcoming Mondays still need a `/ship`.

### Setup

1. **Add Discord webhook to `.env.local`:**
   ```bash
   LOW_CONTENT_WEBHOOK=https://discord.com/api/webhooks/YOUR_WEBHOOK_HERE
   ```

2. **Add as GitHub secret:** Settings → Secrets and variables → Actions → `LOW_CONTENT_WEBHOOK`

3. **GitHub Action runs every Saturday at 12:00 UTC** and posts the ledger. The same webhook receives the surface kit on publish mornings.

### Manual Testing

```bash
# Print the ledger. Never posts to Discord, even with a webhook configured.
uv run tools/buffer_check.py

# Actually post it. Only the Saturday workflow normally does this.
uv run tools/buffer_check.py --notify
```

### What it shows

One `/ship` fills one Monday: a post and the issue derived from it. The report is one row per Monday for the next two months:

```
🚨 LOW · Content Buffer
Next /ship needed for  Mon Sep 28  ·  16 days
Monday
──────────────────────────────────────────────────────
2 of 9 Mondays shipped
   Mon Sep 14   Run Claude Code From Your Phone…   ✉ The agents run, I go buy shrimp
   Mon Sep 21   Run Claude Code on Any Model…      ✉ …
   Mon Sep 28   —
```

- Status is how many Mondays are fully shipped before the first one that isn't: 0 = 🚨 LOW, 1-2 = ⚠️ WARN, 3+ = ✅ GOOD
- A Monday with a post but no issue (or the reverse) is half-shipped, and the report names the command that fixes it
- Anything scheduled off a publish day is listed separately so it cannot silently vanish

## Local Development

### Start Dev Server

```bash
cd website && pnpm dev
```

Visit http://localhost:3000 for live preview with hot-reload.

### Build for Production

```bash
cd website && pnpm run build
```

Validates TypeScript, MDX, and generates static pages.

## Python Tools (Advanced)

Direct tool usage without Claude Code commands:

**Content Generation:**
- `aitk image generate '<prompt>' -o <path> -f webp` - Generate AI images (see [AI Toolkit (aitk)](#ai-toolkit-aitk))
- `uv run tools/convert_to_webp.py <input> <output>` - Convert existing PNG/JPG to WebP (rarely needed; aitk writes WebP directly)

**Validation:**
- `uv run tools/seo_check.py <mdx-file>` - SEO analysis
- `vale <mdx-file>` - Prose linting

**Utilities:**
- `uv run tools/next_publish_date.py` - Get next available publish date
- `uv run tools/move_post_date.py <old-date> <new-date>` - Move a post to a new date (with `--dry-run` to preview)

## Architecture

### Tech Stack

- **Frontend**: Next.js 16 (App Router) + Tailwind CSS
- **Content**: MDX files with gray-matter frontmatter
- **Styling**: shadcn/ui + @tailwindcss/typography
- **Deployment**: Vercel (auto-deploy on push)
- **Images**: next/image + Vercel CDN
- **Code**: react-syntax-highlighter (oneLight/oneDark themes)

### Code Syntax Highlighting

Code blocks use `react-syntax-highlighter` with PrismLight for optimized bundle size. Only the languages actually used in blog posts are registered.

**Currently registered languages:**
- `bash` / `shell`
- `python`
- `markdown`
- `typescript`
- `javascript`
- `json`
- `yaml`
- `tsx`

**Adding a new language:** If you write a post using a language not listed above (e.g., `go`, `rust`, `sql`), the code will render as plain text without highlighting. To add support:

1. Edit `website/components/code-block.tsx`
2. Add the import: `import go from "react-syntax-highlighter/dist/esm/languages/prism/go";`
3. Register it: `SyntaxHighlighter.registerLanguage("go", go);`
4. Update this list in the README

Available languages: [Prism supported languages](https://github.com/react-syntax-highlighter/react-syntax-highlighter/blob/master/AVAILABLE_LANGUAGES_PRISM.MD)

### Project Structure

```
the-agentic-engineer/
├── .claude/                      # Claude Code commands and hooks
├── lib/                          # Python modules (config, validation, frontmatter)
├── tools/                        # Python CLI tools
├── specs/                        # Architecture docs
└── website/                      # Next.js app (deployed to Vercel)
    ├── app/                      # Routes and layouts
    ├── components/               # React components (shadcn/ui)
    ├── content/posts/            # MDX blog posts
    ├── public/blog/              # Post images (WebP)
    └── lib/                      # TypeScript utilities
```

## Known Gaps (High Leverage)

### Headshot for `/about`

The About page (`website/app/about/page.tsx`) currently renders an initials placeholder (`"MF"`) in the hero. Drop a real headshot at `website/public/about/matthew-fontana.webp` and replace the placeholder `<div>` with `<Image src="/about/matthew-fontana.webp" ... />`.

This is the single highest-leverage conversion improvement on the site. Faceless consulting About pages underperform significantly; the Airbnb Passport pattern that informed the page's design is grounded in research that says trust requires a face. Environmental shots (at a desk, in a coffee shop) tend to outperform studio headshots for solo-consultant credibility.

## Project History

Migrated from Blogger + Cloudinary to Next.js + Vercel (October 2025). See `docs/architecture.md` for full system details.

## Troubleshooting

### Build Errors

```bash
cd website && pnpm run build
```

Check for:
- TypeScript errors
- Missing images
- Invalid frontmatter
- Invalid categories

### Quality Review Failures

```bash
/mdx-quality-review website/content/posts/your-post.mdx
```

Common issues:
- Description too short/long (need 150-160 chars)
- Invalid category (must be one of 7 options)
- Missing alt text on images
- Multiple H1 headings

### Vale Linting

Vale warnings are suggestions, not blockers. Focus on errors first.

## Contributing

This is a personal blog system. For questions or issues, see the migration documentation or architecture specs in `specs/`.

## License

Private project - not licensed for reuse.
