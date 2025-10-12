# Agentic Engineer Blog Automation

Automated blog publishing system for Google Blogger with Cloudinary CDN integration.

## Features

✅ **Automated Publishing**: Write in Markdown, publish to Blogger with one command
✅ **Image CDN**: Automatic upload and optimization via Cloudinary
✅ **Idempotent**: Safe to run multiple times, no duplicates
✅ **Smart Updates**: Detects existing posts, updates instead of duplicating
✅ **Path-Based Identity**: Directory name determines post URL
✅ **Hash-Based Deduplication**: Only uploads changed images
✅ **Syntax Highlighting**: Code blocks with Pygments
✅ **Markdown Extensions**: Tables, strikethrough, task lists

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
7. Verify setup: `uv run tools/test_auth.py`

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

```bash
# Validate and preview
uv run build.py posts/2025-10-12-my-first-post/

# Publish to Blogger
uv run publish.py posts/2025-10-12-my-first-post/
```

## Workflow

### Commands

- **`build.py`**: Validate and generate preview (no external changes)
- **`publish.py`**: Upload images, create/update post on Blogger

### First Publish

```bash
uv run publish.py posts/2025-10-12-new-post/
```

Result: Post **CREATED** on Blogger as DRAFT

### Update Existing Post

Edit `post.md`, then:

```bash
uv run publish.py posts/2025-10-12-new-post/
```

Result: Post **UPDATED** (detected via `blogger_id` or path)

### Publish Live

Change `status: draft` to `status: published`, then republish.

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
