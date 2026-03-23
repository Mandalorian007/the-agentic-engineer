# The Agentic Engineer - Architecture Documentation

**Last Updated:** October 2025
**Status:** Production - Automated content pipeline with social media distribution

---

## Overview

The Agentic Engineer is a fully automated blogging platform built with Next.js 15. The system handles the complete content lifecycle: AI-generated blog posts with OpenAI-generated images, platform-optimized social media posts, automated quality checks, scheduled publishing, and automated social media distribution via GitHub Actions.

### Tech Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Framework** | Next.js 15 (App Router) | Static site generation with React |
| **Hosting** | Vercel | Zero-config deployment + global CDN |
| **Content** | MDX files | Markdown with frontmatter |
| **Rendering** | react-markdown + remark-gfm | Convert MDX to HTML |
| **Styling** | Tailwind CSS v4 + @tailwindcss/typography | Utility-first CSS + prose styling |
| **Components** | shadcn/ui (Clean Slate theme) | Pre-built accessible components |
| **UI Layouts** | shadcnblocks Pro (blog27, navbar8, footer16) | Professional blog layouts |
| **Images** | next/image + WebP | Automatic optimization |
| **Code Highlighting** | react-syntax-highlighter | Theme-aware syntax highlighting (oneLight/oneDark) |
| **Theme** | next-themes | Light/dark mode toggle |
| **Content Tools** | Python (uv) | CLI tools for generation & validation |
| **Social Distribution** | GitHub Actions + twitter-api-v2 | Automated social posting via scheduled workflows |

---

## Project Structure

```
the-agentic-engineer/
├── .claude/                      # Claude Code commands and hooks
│   ├── commands/                 # Slash commands for blog workflow
│   │   ├── create-post.md        # Generate new blog post with AI
│   │   ├── generate-socials.md   # Generate social media posts
│   │   ├── mdx-quality-review.md # SEO + Vale + Social validation
│   │   └── create-social-quality-review.md # End-to-end workflow
│   ├── hooks/                    # Python hooks for safety & validation
│   └── settings.json             # Claude Code configuration
│
├── docs/                         # Architecture & setup documentation
│   ├── architecture.md           # This file - current system architecture
│   └── shadcnblocks-setup.md     # Pro blocks setup guide
│
├── specs/                        # Work-in-progress specifications
│   ├── content-pipeline-migration.md  # Migration plan (historical)
│   └── nextjs-migration-resources.md  # Migration resources (historical)
│
├── lib/                          # Python modules for content generation
│   ├── config.py                 # Blog configuration loader
│   ├── scheduling.py             # Shared date calculation (weekly/monthly)
│   ├── frontmatter.py            # YAML frontmatter parser
│   ├── validator.py              # MDX validation & category checking
│   └── social_validator.py       # Social media post validation
│
├── tools/                        # Python CLI tools
│   ├── generate_image.py         # OpenAI image generation (gpt-image-1)
│   ├── convert_to_webp.py        # Image format conversion
│   ├── next_publish_date.py      # Calculate next publish date (weekly/monthly)
│   ├── seo_check.py              # SEO analysis & validation
│   ├── post_to_twitter.py        # Twitter posting from frontmatter
│   ├── buffer_check.py           # Content buffer monitoring
│   └── setup_check.py            # Environment validation
│
├── website/                      # Next.js application (deployed to Vercel)
│   ├── app/                      # Routes and layouts (App Router)
│   │   ├── page.tsx              # Homepage with hero section
│   │   ├── layout.tsx            # Root layout (navbar, footer, theme)
│   │   ├── blog/
│   │   │   ├── page.tsx          # Blog listing with category filters
│   │   │   ├── category/[category]/page.tsx  # Category filter pages
│   │   │   └── [slug]/page.tsx   # Individual blog post pages
│   │   ├── sitemap.ts            # XML sitemap generation
│   │   └── robots.ts             # robots.txt generation
│   │
│   ├── components/               # React components
│   │   ├── ui/                   # shadcn/ui components
│   │   ├── blog27.tsx            # Blog listing layout (shadcnblocks Pro)
│   │   ├── navbar8.tsx           # Navigation bar (shadcnblocks Pro)
│   │   ├── footer16.tsx          # Footer (shadcnblocks Pro)
│   │   ├── code-block.tsx        # Theme-aware syntax highlighting
│   │   └── theme-toggle.tsx      # Light/dark mode toggle
│   │
│   ├── content/                  # Blog content
│   │   └── posts/                # MDX blog posts
│   │       ├── 2025-10-12-voice-to-blog-automation.mdx
│   │       ├── 2025-10-13-taming-claude-yolo-mode.mdx
│   │       └── 2025-10-14-blogger-to-nextjs-migration.mdx
│   │
│   ├── public/                   # Static assets
│   │   └── blog/                 # Post images (WebP format)
│   │       ├── 2025-10-12-voice-to-blog-automation/
│   │       │   ├── hero-voice-to-blog-pipeline.webp
│   │       │   └── diagram-blog-automation-architecture.webp
│   │       └── [other posts...]/
│   │
│   ├── lib/                      # TypeScript utilities
│   │   ├── posts.ts              # Post loading with date filtering
│   │   ├── categories.ts         # Category management & validation
│   │   └── utils.ts              # Helper functions
│   │
│   └── package.json              # npm dependencies
│
├── blog-config.yaml              # Blog configuration
├── pyproject.toml                # Python dependencies (uv)
└── README.md                     # User-facing documentation
```

---

## Content Workflow

### 1. Creating a Blog Post

**Recommended Workflow:**
```bash
# Complete workflow (create → socials → review → remind to deploy)
/create-social-quality-review Your blog post idea goes here
```

This command orchestrates the entire content pipeline:
1. Gets next available publish date from configured schedule
2. Creates MDX post with AI-generated content and images
3. Generates platform-optimized social media posts
4. Runs comprehensive quality review (SEO + Vale + Social)
5. Provides deployment instructions

**Step by Step (Manual):**
```bash
# 1. Create post with AI-generated content and images
/create-post Your blog post idea goes here

# 2. Generate social media posts (Twitter, LinkedIn)
/generate-socials website/content/posts/YYYY-MM-DD-slug.mdx

# 3. Run quality review
/mdx-quality-review website/content/posts/YYYY-MM-DD-slug.mdx

# 4. Deploy
git add .
git commit -m "Add new blog post: Your Title"
git push origin main
```

### 2. What Happens During Creation

When you run `/create-post`:

1. **Get next Monday date** - Uses `next_publish_date.py` for consistent scheduling
2. **Generate content** - AI creates complete blog post with proper structure
3. **Generate images** - OpenAI gpt-image-1 creates hero image and diagrams via `generate_image.py`
4. **Convert to WebP** - Optimizes images using `convert_to_webp.py`
5. **Save files**:
   - MDX: `website/content/posts/YYYY-MM-DD-slug.mdx`
   - Images: `website/public/blog/YYYY-MM-DD-slug/*.webp`
6. **Validate** - Checks category, frontmatter, and image references

### 3. Quality Review Process

When you run `/mdx-quality-review`:

1. **SEO Analysis** - `seo_check.py` validates:
   - Title length (30-60 chars)
   - Description (150-160 chars, required)
   - Category (must be one of 7 options)
   - Heading structure (single H1, proper hierarchy)
   - Content length (300+ words)
   - Image alt text
   - Internal/external links

2. **Vale Prose Linting** - Checks writing style:
   - write-good rules for clarity
   - Custom SEO rules
   - Readability metrics
   - Ignores code blocks and frontmatter

3. **Social Media Validation** - `social_validator.py` checks:
   - Twitter character limit (250 chars max, reserves 30 for URL)
   - LinkedIn character limit (2970 chars max, reserves 30 for URL)
   - Required `text` field for each platform
   - Proper schema structure
   - Warnings if no social posts defined

### 4. Deployment

```bash
git add .
git commit -m "Add new blog post: Your Title"
git push origin main
```

Vercel automatically detects the push and deploys:
- Builds Next.js site from `website/` directory
- Optimizes images
- Generates static pages
- Updates global CDN
- Live in ~1-2 minutes

---

## Post Format

### File Structure

```
website/
├── content/posts/
│   └── 2025-10-12-my-post.mdx          # Single MDX file
└── public/blog/2025-10-12-my-post/
    ├── hero-automation.webp            # Images in WebP format
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

Every post must have ONE category from this hardcoded list:

| Category | Description | Use Case |
|----------|-------------|----------|
| **tutorials** | Step-by-step how-to guides | Teaching specific skills |
| **case-studies** | Real-world project showcases | Demonstrating results |
| **guides** | Beginner-friendly fundamentals | Introducing concepts |
| **lists** | Tips, tools, strategies | Curated collections |
| **comparisons** | Product/approach comparisons | Evaluating options |
| **problem-solution** | Addressing pain points | Solving specific issues |
| **opinions** | Perspectives, myth-busting | Sharing viewpoints |

**Implementation:** Validated at creation time by AI and enforced in `lib/validator.py` and `website/lib/categories.ts`.

### Image References

Use **relative paths** from MDX file location:

```markdown
![Alt text describing image](../../public/blog/2025-10-12-my-post/hero-automation.webp)
```

**Why relative paths?**
- Works in IDE markdown preview
- Next.js automatically converts to `/blog/...` URLs at render time
- No build-time remark plugin needed
- Simple and maintainable

**Hero Images for Social Media:**
- Hero images (named `hero-*.webp`) are automatically detected and used for Open Graph and Twitter Card previews
- No manual configuration needed - the system scans `public/blog/{slug}/` for any file starting with `hero-`
- Social media platforms (Twitter, LinkedIn, Facebook) show rich preview cards with these images when posts are shared

---

## Scheduled Posts & Publishing Schedule

### Configurable Publishing Schedule

The publishing schedule is configured in `blog-config.yaml`:

```yaml
# Monthly (2nd Monday of each month)
publishing:
  frequency: "monthly"
  day: "monday"
  week_of_month: 2
  time: "11:00:00"  # Publish time (UTC) - 6am EST

# Weekly (every Monday)
publishing:
  frequency: "weekly"
  days: ["monday"]
  time: "11:00:00"
```

**To change publishing frequency:** Edit `blog-config.yaml`. The entire content pipeline automatically adapts:
- `scheduling.py` - Shared date calculation for weekly/monthly
- `next_publish_date.py` - Calculates next available publish date
- `buffer_check.py` - Adjusts buffer calculations (months or weeks)
- `/create-post` command - Uses configured schedule

**Examples:**
- Monthly (2nd Monday): `frequency: "monthly"`, `day: "monday"`, `week_of_month: 2`
- Weekly: `frequency: "weekly"`, `days: ["monday"]`
- Twice weekly: `frequency: "weekly"`, `days: ["monday", "thursday"]`

### How Scheduled Posts Work

Posts with future dates are automatically hidden until their publication date:

```yaml
---
title: "Future Post"
date: "2025-12-25T11:00:00Z"  # Won't appear until 6am EST on this date
category: "tutorials"
---
```

### Implementation

**1. Date Filtering** (`website/lib/posts.ts:53-60`):
```typescript
export function getPublishedPosts(): Post[] {
  const allPosts = getAllPosts();
  const now = new Date();

  return allPosts.filter(post => {
    const postDate = new Date(post.date);
    return postDate <= now;  // Only show past/present posts
  });
}
```

**2. ISR Revalidation** (rebuilds pages hourly):
```typescript
// app/blog/page.tsx, app/blog/[slug]/page.tsx
export const revalidate = 3600; // 1 hour
```

Posts appear within ~1 hour of their scheduled time without manual intervention.

---

## Automated Social Media Distribution

### How It Works

Social media posts are automatically published via GitHub Actions running daily at 6:30am EST. Posts go live at 6am EST via ISR, giving 30 minutes for Next.js to rebuild before tweeting.

**Architecture:**
1. **Content Generation** - `/generate-socials` command creates platform-optimized posts
2. **Storage** - Social content stored in frontmatter under `social:` key
3. **Validation** - Social validator checks character limits during quality review
4. **Standardized Schedule** - All posts publish at 6am EST (11am UTC)
5. **Automated Tweeting** - GitHub Actions runs at 6:30am EST (11:30am UTC) to tweet posts from today

**Implementation** (`tools/post_to_twitter.py` + `.github/workflows/post-to-twitter.yml`):

```python
# Find posts scheduled for today
# All posts publish at 6am EST (11am UTC)
# Script runs at 6:30am EST to tweet them
posts_today = get_posts_for_today(config)

# Read social.twitter.text from frontmatter
tweet_text = build_tweet(frontmatter, slug, domain)

# Post to Twitter API
client = get_twitter_client()
client.create_tweet(text=tweet_text)
```

**Frontmatter Schema:**
```yaml
---
date: "2025-10-27T11:00:00Z"  # All posts at 6am EST (11am UTC)
social:
  twitter:
    text: "🚀 Engaging tweet about the post (max 250 chars)"
  linkedin:
    text: "Professional LinkedIn post (max 2970 chars)"
---
```

**Daily Schedule:**
- **6:00am EST (11:00 UTC)**: Post goes live, ISR begins rebuilding
- **6:30am EST (11:30 UTC)**: GitHub Actions tweets the post

**Tweet Format:**
```
{social.twitter.text}

https://agentic-engineer.com/blog/{slug}
```

**Key Features:**
- ✅ **Platform-specific content** - Different messaging for Twitter vs LinkedIn
- ✅ **Pre-validated posts** - Character limits checked during quality review
- ✅ **Isolated workflows** - Twitter and LinkedIn post independently (no cascading failures)
- ✅ **Standardized schedule** - All posts at 6am EST, tweets at 6:30am EST
- ✅ **Publish any day** - Not limited to Mon/Thu - schedule a post for any date
- ✅ **ISR-safe timing** - 30 minute window ensures post is live before tweeting
- ✅ **Version controlled** - Social posts committed alongside blog content
- ✅ **Easy testing** - Manual trigger via GitHub UI or local script

**Dependencies:**
- `tweepy>=4.14.0` - Python Twitter API client
- GitHub Actions workflows:
  - `.github/workflows/post-to-twitter.yml` - Runs daily at 6:30am EST (11:30am UTC)
  - `.github/workflows/post-to-linkedin.yml` - Future: Runs daily at 6:35am EST (11:35am UTC)
- Environment variables (set as GitHub secrets):
  - `TWITTER_API_KEY`
  - `TWITTER_API_KEY_SECRET`
  - `TWITTER_ACCESS_TOKEN`
  - `TWITTER_ACCESS_TOKEN_SECRET`

**Error Handling:**
- Posts without social content are skipped (exit 0)
- Twitter API failures exit with code 1 (workflow marked as failed)
- Each platform workflow is independent (Twitter failure doesn't affect LinkedIn)

---

## Content Buffer Monitoring

### How It Works

A GitHub Action runs every **Saturday at 8am EST** to monitor the content pipeline and send a status update via Discord webhook.

**Implementation** (`.github/workflows/buffer-check.yml` + `tools/buffer_check.py`):

```bash
# Runs periodically via GitHub Actions
uv run tools/buffer_check.py --force
```

**Discord Notification Format:**
- 🎨 **Color-coded urgency** (monthly: green ≥2 months, orange 1-2 months, red <1 month; weekly: green ≥4 weeks, orange 2-4 weeks, red <2 weeks)
- 📊 **Buffer status** (months or weeks remaining, posts scheduled @ rate)
- 📅 **Last scheduled post date**
- ✍️ **When new content is needed**
- 📝 **Complete list of scheduled posts with titles**

**Key Features:**
- ✅ **Periodic check-in** - Always know your content status without manual tracking
- ✅ **Auto-loads .env.local** - Works locally and in GitHub Actions with same command
- ✅ **Title extraction** - Parses MDX frontmatter for readable post titles
- ✅ **Adaptive calculations** - Automatically adjusts for configured publishing frequency
- ✅ **Zero manual work** - Set and forget monitoring

**Setup:**
1. Add `LOW_CONTENT_WEBHOOK` to GitHub secrets (Settings → Secrets → Actions)
2. Workflow runs automatically every Saturday morning
3. Test locally: `uv run tools/buffer_check.py --force`

---

## Next.js Architecture

### URL Structure

```
/                                       # Homepage
/blog                                   # Blog listing (all posts)
/blog/category/[category]               # Filter by category
/blog/YYYY-MM-DD-slug                   # Individual post
/sitemap.xml                            # Auto-generated sitemap
/robots.txt                             # Auto-generated robots.txt
```

### Static Generation (SSG)

All pages are pre-rendered at build time using:

**1. Blog Listing** (`app/blog/page.tsx`):
```typescript
export const revalidate = 3600; // ISR: rebuild hourly

export default function BlogPage() {
  const posts = getPublishedPosts(); // Filters out future dates
  // Render with blog27 component
}
```

**2. Individual Posts** (`app/blog/[slug]/page.tsx:108-113`):
```typescript
export function generateStaticParams() {
  const posts = getAllPostSlugs();
  return posts.map(slug => ({ slug }));
}

export function generateMetadata({ params }: Props) {
  const post = getPostBySlug(params.slug);
  // Return title, description, Open Graph, etc.
}
```

**3. Category Pages** (`app/blog/category/[category]/page.tsx:41-45`):
```typescript
export function generateStaticParams() {
  return Object.keys(CATEGORIES).map(category => ({
    category
  }));
}
```

### SEO Features

- ✅ **Dynamic Metadata** - Per-page title, description, Open Graph
- ✅ **Open Graph Images** - Hero images automatically included for rich social previews
- ✅ **Twitter Card Metadata** - summary_large_image cards with hero images
- ✅ **Automatic Hero Detection** - Scans public/blog/{slug}/ for hero-*.webp files
- ✅ **JSON-LD Structured Data** - BlogPosting schema for rich results
- ✅ **XML Sitemap** - Auto-generated from posts and category pages
- ✅ **robots.txt** - Allow all, link to sitemap
- ✅ **Image Optimization** - next/image handles dimensions, WebP, lazy loading
- ✅ **Clean URLs** - Semantic, hackable URL structure
- ✅ **ISR (Incremental Static Regeneration)** - Hourly page rebuilds

### Theme System

**Implementation:**
- `next-themes` for theme management
- CSS variables defined in `globals.css`
- Clean Slate theme from tweakcn
- Theme toggle in navbar (navbar8 component)

**Code Styling** (`components/code-block.tsx`):
```typescript
import { useTheme } from 'next-themes';

export function CodeBlock({ children, language }) {
  const { theme } = useTheme();

  return (
    <SyntaxHighlighter
      style={theme === 'dark' ? oneDark : oneLight}
      language={language}
    >
      {children}
    </SyntaxHighlighter>
  );
}
```

**Inline Code** (custom CSS in `app/blog/[slug]/page.tsx`):
- Light mode: `#f5f5f5` background, `#383a42` text
- Dark mode: `#282c34` background, `#abb2bf` text

---

## UI Components

### shadcn/ui Base Components

Installed from [shadcn/ui](https://ui.shadcn.com/):
- `button`, `card`, `badge`, `separator`
- `dropdown-menu`, `navigation-menu`
- `sheet`, `accordion`, `avatar`
- All customizable, theme-aware

**Setup:**
```bash
pnpm dlx shadcn@latest init
pnpm dlx shadcn@latest add https://tweakcn.com/r/themes/clean-slate.json
```

### shadcnblocks Pro Layouts

Professional layouts from [shadcnblocks.com](https://www.shadcnblocks.com/) (Pro license):

**blog27** - Blog listing page:
- Grid layout with post cards
- Category filter tabs
- Featured post highlight
- Image slots for hero images

**navbar8** - Navigation bar:
- Logo and navigation links
- Theme toggle (light/dark)
- Mobile responsive menu
- Search integration ready

**footer16** - Footer:
- Multi-column layout
- Social media links
- Mobile accordion view
- Newsletter signup ready

**Setup:** See `docs/shadcnblocks-setup.md` for configuration details.

---

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
  frequency: "monthly"
  day: "monday"              # Publish on Mondays
  week_of_month: 2           # 2nd occurrence each month
  time: "11:00:00"           # Publish time (UTC) - 6am EST - posts go live for ISR

categories:
  - tutorials
  - case-studies
  - guides
  - lists
  - comparisons
  - problem-solution
  - opinions
```

### .env.local (Root Directory)

```bash
# Required for AI image generation
OPENAI_API_KEY=your-key-here
```

### pyproject.toml

Minimal Python dependencies (6 packages):

```toml
[project]
name = "the-agentic-engineer"
version = "2.0.0"
requires-python = ">=3.10"
dependencies = [
    "Pillow>=11.0.0",           # Image processing
    "PyYAML>=6.0.2",            # YAML parsing
    "python-dotenv>=1.0.1",     # Environment variables
    "openai>=1.0.0",            # Image generation (gpt-image-1)
    "requests>=2.31.0",         # HTTP requests
    "tweepy>=4.14.0",           # Twitter API integration
]
```

**Install:**
```bash
uv sync
```

### website/package.json

Next.js dependencies:

```json
{
  "dependencies": {
    "next": "^15.0.3",
    "react": "^19.0.0",
    "react-dom": "^19.0.0",
    "next-themes": "^0.4.4",
    "@tailwindcss/typography": "^0.5.16",
    "react-markdown": "^9.0.1",
    "remark-gfm": "^4.0.0",
    "react-syntax-highlighter": "^15.6.1",
    "gray-matter": "^4.0.3"
  }
}
```

**Note:** `twitter-api-v2` was moved to Python dependencies. Social media posting is now handled by Python scripts via GitHub Actions, not Next.js.

---

## Python Tools Reference

### Content Generation

#### generate_image.py
```bash
uv run tools/generate_image.py "prompt" output.webp
```

**Purpose:** Generate AI images using OpenAI gpt-image-1 model
**Output:** WebP format, 1024x1024 pixels
**Requires:** `OPENAI_API_KEY` in `.env.local`

**Example:**
```bash
uv run tools/generate_image.py \
  "modern minimalist illustration of AI automation, blue gradient, isometric view" \
  website/public/blog/2025-10-12-my-post/hero.webp
```

**Prompt Tips:**
- Specify style (minimalist, modern, flat design)
- Include colors (blue gradient, warm tones)
- Add perspective (isometric, top-down)
- Describe mood (professional, energetic)

#### convert_to_webp.py
```bash
uv run tools/convert_to_webp.py input.png output.webp
```

**Purpose:** Convert existing images to WebP format
**Quality:** 85% (configurable in script)
**Note:** Rarely needed - `generate_image.py` outputs WebP directly

### Validation

#### seo_check.py
```bash
uv run tools/seo_check.py website/content/posts/YYYY-MM-DD-slug.mdx
```

**Purpose:** Comprehensive SEO analysis
**Checks:**
- ✅ Title length (30-60 chars optimal)
- ✅ Description (150-160 chars, required)
- ✅ Category validation (one of 7 options)
- ✅ Heading structure (single H1, proper hierarchy)
- ✅ Content length (300+ words recommended)
- ✅ Image alt text presence
- ✅ Internal/external links

**Output:** Colored terminal output with warnings and suggestions

#### Vale Prose Linting
```bash
# Install (one-time)
brew install vale
vale sync

# Lint a post
vale website/content/posts/YYYY-MM-DD-slug.mdx
```

**Purpose:** Writing style and readability checks
**Configuration:** `.vale.ini` at project root
**Rules:**
- write-good (clarity, passive voice, weasel words)
- Custom SEO rules
- Ignores code blocks and frontmatter

**Note:** Vale warnings are suggestions, not blockers. Focus on errors first.

### Utilities

#### next_publish_date.py
```bash
uv run tools/next_publish_date.py
```

**Purpose:** Calculate next available publish date based on configured schedule
**Configuration:** Reads `publishing` section from `blog-config.yaml`
**Output:**
```
Next available publish date (2nd Monday of each month):
----------------------------------------
Directory name: 2026-04-13-your-slug-here
Frontmatter date: 2026-04-13T11:00:00Z
Day: Monday, April 13, 2026
```

**Logic:**
- Loads publishing schedule from `blog-config.yaml`
- Scans existing posts in `website/content/posts/`
- Finds next configured publish date not already used
- Supports weekly (any weekday combination) and monthly (nth weekday) schedules
- Returns properly formatted date for frontmatter

#### move_post_date.py
```bash
# Preview changes without making them
uv run tools/move_post_date.py 2025-10-27 2025-10-23 --dry-run

# Actually move the post
uv run tools/move_post_date.py 2025-10-27 2025-10-23

# Move with specific time (optional)
uv run tools/move_post_date.py 2025-10-27 "2025-10-23T14:30:00Z"
```

**Purpose:** Move a blog post from one date to another
**What it does:**
- Renames MDX file with new date prefix
- Updates `date` field in frontmatter
- Renames image directory to match new date
- Updates all image path references in MDX content

**Options:**
- `--dry-run` - Preview changes without making them (recommended first step)
- `-q, --quiet` - Minimal output (only errors)

**Use Cases:**
- Adjusting content schedule (e.g., weekly to monthly)
- Filling gaps in the content calendar
- Rescheduling posts based on priorities
- Fixing accidentally scheduled dates

**Example Output:**
```
📄 Found post: 2025-10-27-packaging-expertise-context-engineering.mdx

============================================================
📋 MOVE PLAN
============================================================

1. Rename MDX file:
   2025-10-27-packaging-expertise-context-engineering.mdx
   → 2025-10-23-packaging-expertise-context-engineering.mdx

2. Update frontmatter date:
   2025-10-27T10:00:00Z
   → 2025-10-23T10:00:00Z

3. Update 2 image reference(s) in content

4. Rename image directory:
   2025-10-27-packaging-expertise-context-engineering/
   → 2025-10-23-packaging-expertise-context-engineering/

============================================================

✅ Move completed successfully!
   Post moved from 2025-10-27 to 2025-10-23
```

**Safety Features:**
- Always validates dates are valid
- Checks if target date already has a post
- Verifies image directory exists before moving
- Provides detailed preview with `--dry-run`
- Reports all changes being made

#### setup_check.py
```bash
uv run tools/setup_check.py
```

**Purpose:** Validate entire development environment
**Checks:**
- ✅ Python 3.10+ installed
- ✅ uv package manager available
- ✅ Python dependencies installed
- ✅ Node.js 18+ and pnpm available
- ✅ Next.js dependencies installed
- ✅ `OPENAI_API_KEY` configured
- ✅ Vale installed (optional)
- ✅ Required directories exist

**Use Case:** First-time setup verification and troubleshooting

#### buffer_check.py
```bash
uv run tools/buffer_check.py --force
```

**Purpose:** Monitor content buffer and send Discord notification
**Configuration:** Reads `publishing` section from `blog-config.yaml` to calculate buffer metrics
**Output:** Status update with scheduled posts (months-based for monthly, weeks-based for weekly)
**Requires:** `LOW_CONTENT_WEBHOOK` in `.env.local` or GitHub secrets

**Automated Usage:**
- GitHub Action runs every Saturday at 8am EST
- Sends color-coded Discord notification
- Shows buffer remaining (months or weeks), scheduled posts, and deadlines
- Automatically adapts to configured publishing frequency (weekly or monthly)

**Manual Testing:**
```bash
# Send test notification (auto-loads .env.local)
uv run tools/buffer_check.py --force
```

**Example Output:**
```
📊 Content Buffer Status
==================================================
Posts scheduled: 3
Publishing rate: 1/month
Schedule: 2nd Monday of each month
Buffer: 2.5 months
```

---

## Development

### Local Preview

```bash
cd website && pnpm dev
```

Visit http://localhost:3000 for live preview with hot-reload.

**Features:**
- Instant updates on file save
- MDX live rendering
- Theme toggle works
- All routes accessible

### Build for Production

```bash
cd website && pnpm run build
```

**What it does:**
- Validates TypeScript
- Type-checks all components
- Validates MDX files
- Generates static pages for all posts and categories
- Optimizes images
- Creates sitemap and robots.txt
- Reports any errors or warnings

**Expected output:**
```
✓ Compiled successfully
✓ Generating static pages
✓ Generated static pages for all routes
```

---

## Deployment

### Vercel Setup

1. **Create Vercel project:**
   - Connect GitHub repository
   - Configure root directory to `website/`
   - Set build command: `pnpm run build`
   - Set output directory: `.next`

2. **Configure domain:**
   - Add custom domain: `agentic-engineer.com`
   - Vercel handles SSL automatically

3. **Environment variables:**
   - Optional: Add `OPENAI_API_KEY` if generating images in CI
   - Not needed for deployment (images pre-generated locally)

4. **Deploy:**
   ```bash
   git push origin main
   ```
   Vercel auto-deploys on every push to main branch.

### Deployment Checklist

Before first deploy:
- [ ] All posts have valid categories
- [ ] All images exist in `website/public/blog/`
- [ ] Build succeeds locally (`pnpm run build`)
- [ ] Sitemap generates correctly
- [ ] robots.txt accessible
- [ ] Theme toggle works
- [ ] Category filters work

---

## System Evolution

**Current State (v2.0):** Next.js 15 + Vercel with automated social media distribution
- **Workflow:** MDX → Git → Vercel → GitHub Actions → Social platforms
- **Tools:** 6 Python CLI tools
- **Dependencies:** 6 Python packages, standard Next.js stack
- **Deployment:** `git push` (auto-deploys to Vercel)
- **Social Media:** Automated via GitHub Actions (Twitter/LinkedIn)
- **Images:** WebP format, committed to Git, served by Vercel CDN

**Historical Note:** Migrated from Blogger + Cloudinary (October 2025). Migration docs available in `specs/` for reference.

---

## Tools & Resources

### Official Documentation

- **Next.js:** https://nextjs.org/docs
- **shadcn/ui:** https://ui.shadcn.com/
- **shadcnblocks:** https://www.shadcnblocks.com/
- **Tailwind CSS:** https://tailwindcss.com/docs
- **Vercel:** https://vercel.com/docs

### Theme & Styling

- **tweakcn Theme Editor:** https://tweakcn.com/editor/theme?theme=clean-slate
- **Clean Slate Theme:** Pre-installed via `pnpm dlx shadcn@latest add https://tweakcn.com/r/themes/clean-slate.json`
- **@tailwindcss/typography:** Prose styling for markdown

### Code Highlighting

- **react-syntax-highlighter:** https://github.com/react-syntax-highlighter/react-syntax-highlighter
- **oneLight theme:** Light mode code blocks
- **oneDark theme:** Dark mode code blocks

### Content Processing

- **react-markdown:** https://github.com/remarkjs/react-markdown
- **remark-gfm:** GitHub Flavored Markdown support
- **gray-matter:** Frontmatter parsing

### Image Generation

- **OpenAI Images API:** https://platform.openai.com/docs/guides/images
- **Pillow:** Python image processing

### Prose Linting

- **Vale:** https://vale.sh/
- **write-good rules:** Built-in Vale package
- **Installation:** `brew install vale && vale sync`

---

## Troubleshooting

### Build Errors

```bash
cd website && pnpm run build
```

**Common issues:**
- TypeScript errors in components
- Missing images in `public/blog/`
- Invalid frontmatter in MDX files
- Invalid categories (must be one of 7)

**Fix:** Check build output for specific file and line numbers.

### Quality Review Failures

```bash
/mdx-quality-review website/content/posts/your-post.mdx
```

**Common issues:**
- Description too short/long (need 150-160 chars)
- Invalid category (must be one of 7 options)
- Missing alt text on images
- Multiple H1 headings

**Fix:** Edit MDX file and re-run quality review.

### Vale Linting

Vale warnings are **suggestions**, not blockers.

**Priority:**
1. Fix Vale **errors** (serious issues)
2. Review Vale **warnings** (suggestions)
3. Ignore Vale **suggestions** (optional improvements)

### Image Issues

**Images not loading:**
1. Check path: `website/public/blog/YYYY-MM-DD-slug/image.webp`
2. Check reference in MDX: `![Alt text](../../public/blog/YYYY-MM-DD-slug/image.webp)`
3. Verify WebP format (not PNG/JPG)
4. Check file permissions

**Image generation fails:**
1. Verify `OPENAI_API_KEY` in `.env.local`
2. Check OpenAI account credits
3. Try simpler prompt
4. Check network connection

---

## Contributing

This is a personal blog system, but the architecture is documented for:
- Future maintainers
- Developers interested in similar setups
- Reference for AI-assisted development workflows

For questions or issues, see:
- This architecture document
- `README.md` for user-facing workflows
- `docs/shadcnblocks-setup.md` for UI component setup

---

## License

Private project - not licensed for reuse.

---

**Last Updated:** October 2025
**Version:** 2.0.0 (Post-migration)
**Status:** Production-ready ✅
