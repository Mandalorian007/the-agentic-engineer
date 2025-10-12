# Agentic Engineer Blog Automation

Automated blog publishing system for Google Blogger with Cloudinary CDN integration.

## Features

- ✅ **Automated Publishing**: Write in Markdown, publish to Blogger with one command
- ✅ **Image CDN**: Automatic upload and optimization via Cloudinary
- ✅ **AI Image Generation**: Generate blog images with OpenAI's GPT-Image-1
- ✅ **Idempotent**: Safe to run multiple times, no duplicates
- ✅ **Smart Updates**: Detects existing posts, updates instead of duplicating
- ✅ **Path-Based Identity**: Directory name determines post URL
- ✅ **Hash-Based Deduplication**: Only uploads changed images
- ✅ **Syntax Highlighting**: Code blocks with Pygments
- ✅ **Markdown Extensions**: Tables, strikethrough, task lists

## Quick Start

### 1. Setup (One-time)

Follow the complete setup guide: [`specs/blog-google-auth.md`](specs/blog-google-auth.md)

**Summary**:
1. Create Google Cloud project
2. Enable Blogger API
3. Configure OAuth consent screen
4. Generate refresh token: `uv run tools/generate_refresh_token.py`
5. Get Cloudinary credentials from cloudinary.com
6. Configure `blog-config.yaml` and `.env.local`
7. Install Vale prose linter: `brew install vale` (optional but recommended)
8. Verify setup: `uv run tools/setup_check.py`

### 2. Create a Post

```bash
# Create post directory (format: YYYY-MM-DD-slug)
mkdir -p posts/2025-10-12-my-first-post

# Write your post
cat > posts/2025-10-12-my-first-post/post.md <<'EOF'
---
title: "My First Post"
date: 2025-10-12T10:00:00Z
tags: [tutorial, python]
status: draft
---

# Hello World

This is my **first post**!
EOF
```

### 3. Build and Publish

**Using Claude Code slash commands** (recommended):

```bash
# Optional: Run quality checks (SEO + prose linting)
/quality-check posts/2025-10-12-my-first-post/

# Validate and preview
/build posts/2025-10-12-my-first-post/

# Publish to Blogger
/publish posts/2025-10-12-my-first-post/
```

**Or run Python scripts directly**:

```bash
# Validate and preview
uv run build.py posts/2025-10-12-my-first-post/

# Publish to Blogger
uv run publish.py posts/2025-10-12-my-first-post/
```

## Workflow

### Claude Code Slash Commands

When using Claude Code, you can use these convenient slash commands:

#### Typical Workflow
The recommended workflow for creating new blog posts:

```bash
# 1. First, sync publish status to ensure dates are up-to-date
/sync-publish-status

# 2. Then create and publish a new post (all in one command)
/create-quality-build-publish Your blog post idea goes here
```

This ensures the next Monday date calculation is accurate and the complete workflow (create → quality check → build → publish) runs automatically.

#### Available Commands

**End-to-End Workflow:**
- **`/create-quality-build-publish <idea>`**: Complete workflow - gets next Monday date, creates post, runs quality checks, builds preview, and publishes to Blogger

**Individual Steps:**
- **`/create-post <idea>`**: Create a blog post from voice/text input (generates content + images automatically)
- **`/quality-check <path>`**: Run SEO analysis and Vale prose linting
- **`/build <path>`**: Validate and generate preview (no external changes)
- **`/publish <path>`**: Upload images, create/update post on Blogger (supports scheduling)
- **`/sync-publish-status`**: Sync post status from Blogger to local frontmatter

### Python Scripts

You can also run the underlying Python scripts directly:

- **`build.py`**: Validate and generate preview (no external changes)
- **`publish.py`**: Upload images, create/update post on Blogger

### First Publish

```bash
/publish posts/2025-10-12-new-post/
# Or: uv run publish.py posts/2025-10-12-new-post/
```

Result: Post **CREATED** on Blogger as DRAFT

### Update Existing Post

Edit `post.md`, then:

```bash
/publish posts/2025-10-12-new-post/
# Or: uv run publish.py posts/2025-10-12-new-post/
```

Result: Post **UPDATED** (detected via `blogger_id` or path)

### Publish Live

Change `status: draft` to `status: published`, then republish.

### Schedule Posts

To schedule a post for future publishing, simply set the `date` field in frontmatter to a future date:

```yaml
---
title: "My Future Post"
date: 2025-12-25T10:00:00Z  # Future date
tags: [tutorial]
status: published  # Will be scheduled, not published immediately
---
```

When you run `/publish` (or `uv run publish.py`):
- If `date` is in the **future**: Post is **scheduled** on Blogger
- If `date` is in the **past or present**: Post publishes immediately

**Batch scheduling workflow:**
```bash
# Write 30 posts with future dates
mkdir posts/2025-10-13-post-1
mkdir posts/2025-10-14-post-2
# ... (all with future dates in frontmatter)

# Publish all at once - they'll be scheduled!
uv run publish.py posts/2025-10-13-post-1/
uv run publish.py posts/2025-10-14-post-2/
# ... now relax! Blogger will publish them automatically

```

### Sync Post Status

If you've been away or made changes in Blogger's UI, sync your local files with actual published status:

```bash
# Sync all posts
uv run tools/sync-publish-status.py
# Or use slash command: /sync-publish-status

# Sync specific post
uv run tools/sync-publish-status.py --post-dir posts/2025-10-12-my-post/
```

**When to sync:**
- You manually changed post status in Blogger's UI
- Scheduled posts went live while you were away
- You're returning to the project after a break
- You want to verify local state matches Blogger

The sync tool updates:
- Post status (draft → published or vice versa)
- Published date
- Updated timestamp

**Note:** The setup check script (`uv run tools/setup-check.py`) automatically runs sync if you have published posts, so you'll always see the latest status when verifying your setup.

## Configuration

### blog-config.yaml

```yaml
blog_name: "Agentic Engineer Blog"
blogger_blog_id: "your-blog-id-here"

image_optimization:
  max_width: 1200
  quality: 85

cloudinary:
  folder: "blog-posts"
  format: "webp"
  quality: "auto:good"
```

### .env.local

```bash
BLOGGER_CLIENT_ID=xxx
BLOGGER_CLIENT_SECRET=xxx
BLOGGER_REFRESH_TOKEN=xxx
CLOUDINARY_CLOUD_NAME=xxx
CLOUDINARY_API_KEY=xxx
CLOUDINARY_API_SECRET=xxx
OPENAI_API_KEY=xxx  # Optional: for AI image generation
```

## Post Format

### Directory Naming

`YYYY-MM-DD-slug` → `/YYYY/MM/slug.html`

Example: `2025-10-12-hello-world` → `/2025/10/hello-world.html`

### Frontmatter

```yaml
---
title: "Post Title"              # Required
date: 2025-10-12T10:00:00Z      # Required
tags: [python, tutorial]         # Optional (must be in tag-registry.yaml)
status: draft                    # draft or published
---
```

After publishing, `blogger_id`, `updated`, and `images` fields are added automatically.

## Quality Checks

### SEO Analysis

Check your posts for SEO best practices:

```bash
uv run tools/seo_check.py posts/2025-10-12-my-first-post/
```

**Checks:**
- ✅ Title length (30-60 characters optimal for Google)
- ✅ Meta description (150-160 characters)
- ✅ Heading structure (single H1, proper hierarchy)
- ✅ Content length (300+ words recommended)
- ✅ Image alt text
- ✅ Internal/external links

### Prose Linting with Vale

Vale checks writing style, catches common errors, and ensures readability.

**Installation:**
```bash
brew install vale
vale sync  # Download style packages
```

**Usage:**
```bash
# Lint a single post
vale posts/2025-10-12-my-first-post/post.md

# Run full quality check (SEO + Vale)
# Use /quality-check command in Claude Code
```

**Configuration:**

Vale is configured in `.vale.ini` with:
- **write-good** rules for clear, concise writing
- **SEO** custom rules for search optimization
- Relaxed settings for technical content
- Ignores code blocks and frontmatter

Alert levels:
- 💡 **Suggestion**: Consider but not required (passive voice, weasel words)
- ⚠️ **Warning**: Should fix (too wordy, clichés, title length)
- ❌ **Error**: Must fix (multiple H1 headings)

## Image Generation

Generate AI images for your blog posts using OpenAI's GPT-Image-1:

```bash
uv run tools/generate_image.py "your detailed prompt" posts/YYYY-MM-DD-slug/image.png
```

**Example:**
```bash
uv run tools/generate_image.py "modern minimalist illustration of AI automation with robotic arms assembling puzzle pieces, blue and teal gradient background, clean tech aesthetic, slightly isometric perspective, professional and futuristic mood" posts/2025-10-12-my-post/hero.png
```

**Prompt Tips:**
- Be specific about style (minimalist, modern, flat design, realistic, abstract)
- Include colors or color schemes (blue gradient, warm tones, monochrome)
- Specify perspective (isometric, top-down, close-up, wide angle)
- Add mood descriptors (professional, playful, serious, energetic)
- Detail the subject (what objects, actions, composition)

**Features:**
- Uses GPT-Image-1 (latest model, high quality)
- Generates 1024x1024 images
- Cost: ~$0.015 per image
- Automatically creates directories
- More detailed prompts = better results

**Note:** Requires `OPENAI_API_KEY` in `.env.local`

## Publishing Schedule

### Next Monday Publish Date

Maintain a consistent Monday publishing schedule:

```bash
uv run tools/next_publish_date.py
```

**Features**:
- Scans all post directories to find the next available Monday
- Skips Mondays that already have scheduled posts
- Provides both directory name format and frontmatter date format

**Example output**:
```
Next available Monday for publishing:
----------------------------------------
Directory name: 2025-10-20-your-slug-here
Frontmatter date: 2025-10-20T10:00:00Z
Day: Monday, October 20, 2025
----------------------------------------

Latest scheduled post: 2025-10-12 (Sunday)
Days until next post: 8
```

## Tag Management

### Tag Registry

All tags must be approved in `tag-registry.yaml` to ensure consistency.

**View approved tags**:
```bash
uv run tools/list_tags.py
```

**Add a new tag**:
```bash
uv run tools/add_tag.py <tag-name>

# Example
uv run tools/add_tag.py docker
```

**Tag validation**:
- Build command validates tags against registry
- Unapproved tags fail validation with suggestions
- Intentional workflow to prevent tag sprawl

**Example error**:
```
❌ Unapproved tags used: docker, kubernetes

To use these tags:
  1. Add them to tag-registry.yaml
  2. Run build again
```

## Troubleshooting

Run verification:
```bash
uv run tools/test_auth.py
```

See [`specs/blog-google-auth.md`](specs/blog-google-auth.md) for detailed troubleshooting.

## Architecture

See [`specs/blog-flow.md`](specs/blog-flow.md) for complete design documentation.

## Using Claude Code with this project

```bash
env $(grep -v "^#" .env | grep -v "^$" | xargs) claude --dangerously-skip-permissions
```
