# The Agentic Engineer

Next.js blog with automated content generation and AI-powered image creation.

## Features

- ✅ **Next.js 15**: Modern static site generation with App Router
- ✅ **MDX Content**: Write in MDX with frontmatter, deploy with git push
- ✅ **AI Image Generation**: Generate blog images with OpenAI DALL-E
- ✅ **Quality Checks**: SEO analysis + Vale prose linting
- ✅ **Category System**: 7 hardcoded categories for consistent organization
- ✅ **Theme Toggle**: Light/dark mode with next-themes
- ✅ **Vercel Deploy**: Automatic deployment on git push
- ✅ **Zero External APIs**: No Cloudinary, no Blogger - just Next.js + Vercel

## Quick Start

### 1. Setup (One-time)

**Requirements:**
- Node.js 18+ and pnpm
- Python 3.10+ (for content generation tools)
- OpenAI API key (for image generation)
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
   # Create .env.local (root directory)
   echo "OPENAI_API_KEY=your-key-here" > .env.local
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

### 2. Create a Post

Use the `/create-post` command in Claude Code:

```bash
/create-post Your blog post idea goes here
```

This will:
- Generate a complete MDX blog post with AI
- Create hero images using DALL-E
- Save to `website/content/posts/YYYY-MM-DD-slug.mdx`
- Save images to `website/public/blog/YYYY-MM-DD-slug/*.webp`

### 3. Quality Review

```bash
# Run quality review (SEO + Vale prose linting)
/mdx-quality-review website/content/posts/YYYY-MM-DD-slug.mdx
```

### 4. Deploy

```bash
git add .
git commit -m "Add new blog post: Your Title"
git push origin main
```

Vercel automatically deploys on push! 🚀

## Workflow

### Recommended Workflow

```bash
# Complete workflow in one command
/create-quality-review Your blog post idea goes here
```

This runs:
1. Gets next available Monday publish date
2. Creates MDX post with AI-generated content
3. Generates and converts images to WebP
4. Runs quality review (SEO + Vale)
5. Reminds you to commit and push

### Available Commands

**End-to-End:**
- `/create-quality-review <idea>` - Complete workflow (create → review → remind to deploy)

**Individual Steps:**
- `/create-post <idea>` - Generate MDX blog post with AI
- `/mdx-quality-review <path>` - Run SEO + Vale prose linting

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

Use relative paths in MDX:

```markdown
![Alt text describing image](./hero-automation.webp)
```

Images are automatically optimized by Next.js `next/image` component.

## Configuration

### blog-config.yaml

```yaml
blog_name: "The Agentic Engineer"
domain: "the-agentic-engineer.com"

website_dir: "website"
content_dir: "website/content/posts"
public_images_dir: "website/public/blog"

image_generation:
  default_size: "1024x1024"
  format: "webp"
  quality: 85

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
# Required for AI image generation
OPENAI_API_KEY=your-key-here
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

Generate AI images using OpenAI DALL-E:

```bash
uv run tools/generate_image.py "detailed prompt" website/public/blog/YYYY-MM-DD-slug/image.png
```

**Example:**
```bash
uv run tools/generate_image.py "modern minimalist illustration of AI automation, blue and purple gradient, clean tech aesthetic, isometric view" website/public/blog/2025-10-12-my-post/hero.png
```

Images are automatically converted to WebP format.

**Prompt Tips:**
- Specify style (minimalist, modern, flat design)
- Include colors (blue gradient, warm tones)
- Add perspective (isometric, top-down)
- Describe mood (professional, energetic)

## Publishing Schedule

Get the next available Monday for consistent publishing:

```bash
uv run tools/next_publish_date.py
```

Output:
```
Next available Monday for publishing:
----------------------------------------
Directory name: 2025-10-20-your-slug-here
Frontmatter date: 2025-10-20T10:00:00Z
Day: Monday, October 20, 2025
```

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
- `uv run tools/generate_image.py <prompt> <path>` - Generate AI images
- `uv run tools/convert_to_webp.py <input>` - Convert images to WebP

**Validation:**
- `uv run tools/seo_check.py <mdx-file>` - SEO analysis
- `vale <mdx-file>` - Prose linting

**Utilities:**
- `uv run tools/next_publish_date.py` - Get next Monday date

## Architecture

### Tech Stack

- **Frontend**: Next.js 15 (App Router) + Tailwind CSS
- **Content**: MDX files with gray-matter frontmatter
- **Styling**: shadcn/ui + @tailwindcss/typography
- **Deployment**: Vercel (auto-deploy on push)
- **Images**: next/image + Vercel CDN
- **Code**: react-syntax-highlighter (oneLight/oneDark themes)

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

## Migration from Blogger

This project was migrated from Blogger + Cloudinary to Next.js + Vercel. See [`specs/content-pipeline-migration.md`](specs/content-pipeline-migration.md) for full migration details.

**Benefits of migration:**
- ✅ Simpler workflow (git push vs API calls)
- ✅ Faster (no external API latency)
- ✅ Cheaper (no Cloudinary costs)
- ✅ More reliable (no OAuth tokens, no rate limits)
- ✅ Better DX (local preview, hot-reload, TypeScript)

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
