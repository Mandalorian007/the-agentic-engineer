---
title: Voice-to-Blog Automation with AI and Python
description: Automation pipeline converting voice notes to blog posts with AI-generated
  images, automated SEO checks, and one-command publishing to Google Blogger.
date: '2025-10-12T14:30:00Z'
tags:
- ai-agents
- python
- workflow-automation
- openai
- anthropic
status: draft
blogger_id: '5381606141212975823'
updated: '2025-10-12T20:03:02.400942'
images:
  hero-voice-to-blog-pipeline.png:
    url: https://res.cloudinary.com/drdtiykkg/image/upload/v1760298543/agentic-engineer-blog/voice-to-blog-automation/hero-voice-to-blog-pipeline.webp
    hash: sha256:d720c1963a78cc145c10f50c364f2020eaad8b698d4a23cc5d66262f03fc012b
    uploaded_at: '2025-10-12T19:49:04.006429Z'
    width: 1024
    height: 1024
    format: webp
  diagram-blog-automation-architecture.png:
    url: https://res.cloudinary.com/drdtiykkg/image/upload/v1760298544/agentic-engineer-blog/voice-to-blog-automation/diagram-blog-automation-architecture.webp
    hash: sha256:24d8ff466a03c9528d9c25faf26ba63dd730d6fc511a07631839d6c5ea89ce31
    uploaded_at: '2025-10-12T19:49:05.206970Z'
    width: 1024
    height: 1024
    format: webp
---
![AI-powered blog automation workflow](./hero-voice-to-blog-pipeline.png)

## The Problem: Blogging Is Too Much Work

Let's be honest—blogging sucks. Not the writing part. Not the creative part. But everything else:

- Formatting markdown by hand
- Creating or finding images that don't look like stock photo garbage
- Converting to HTML that actually looks good
- Optimizing images for web
- Uploading images to a CDN
- Publishing to your blog platform
- Running SEO checks
- Making sure you didn't write like a robot

By the time you've done all that, you've lost the momentum that made you want to write in the first place.

## What If You Could Just… Talk?

Here's what I built: **A complete voice-to-published-blog pipeline powered by AI**.

You literally just ramble about your idea—like you're explaining it to a friend at a coffee shop—and the system:

1. ✅ **Converts your rambling into a structured blog post**
2. ✅ **Generates professional images with AI** (OpenAI GPT-Image-1)
3. ✅ **Builds the HTML with syntax highlighting and formatting**
4. ✅ **Runs SEO and quality checks automatically**
5. ✅ **Uploads images to Cloudinary CDN**
6. ✅ **Publishes to Google Blogger as a draft**
7. ✅ **Updates instead of duplicating** (it's idempotent!)

Then you review it, change `status: draft` to `status: published`, run one command, and **you're live**.

That's it. That's the whole workflow.

## How It Works: The Four-Command Workflow

Here's the actual workflow I use now:

### Step 1: Create the Post (Voice or Text)

I have a Claude Code slash command called `/create-post`. I just talk about my idea:

```bash
/create-post So today I made a really cool tech thing. It's for blogging.
All I have to do is ramble about whatever I want to write about—I don't
even have to structure it. The system takes my blurb, converts it into
proper markdown, and even generates images for it...
```

Claude Code (powered by Anthropic's Sonnet) then:
- Analyzes my rambling and identifies the core story
- Chooses the best blog post format (tutorial, case study, listicle, etc.)
- Writes a complete, structured blog post in markdown
- **Generates images automatically** using the image generation tool
- Suggests detailed AI prompts for each image (hero images, diagrams, etc.)
- Saves everything to `posts/YYYY-MM-DD-slug/post.md`

Here's the magic: the `/create-post` command doesn't just write text—it **actively generates the images** as part of the workflow. The command has access to the `generate_image.py` tool, so it crafts detailed prompts and creates the images while writing the post.

### Step 2: Generate Images (If Needed)

If you want more images beyond what the command created, you can run:

```bash
uv run tools/generate_image.py "modern minimalist illustration of
AI automation pipeline with voice input, markdown documents, and blog
publishing, blue and purple gradient, clean tech aesthetic, isometric
view, professional futuristic mood" posts/2025-10-12-my-post/hero.png
```

Each image costs about **$0.015** (less than two cents) and looks way better than stock photos. We save the images directly in the post directory.

### Step 3: Quality Check, Build, and Publish

With the post written and images generated, I run three more slash commands:

```bash
# Optional: Check quality (SEO + prose linting)
/quality-check posts/2025-10-12-my-post/

# Validate and preview locally
/build posts/2025-10-12-my-post/

# Publish to Blogger (creates draft)
/publish posts/2025-10-12-my-post/
```

**The `/quality-check` command** runs both Vale prose linting and SEO analysis, catching issues like passive voice, wordy phrases, missing meta descriptions, and title length problems.

**The `/build` command** validates everything:
- Checks frontmatter and tag registry
- Validates image references
- Converts markdown to HTML with syntax highlighting
- Generates a local preview HTML file

**The `/publish` command** does the actual publishing:
- Uploads images to Cloudinary CDN (with hash-based deduplication)
- Converts markdown to HTML with Pygments syntax highlighting
- Detects if the post already exists (via directory path)
- Creates OR updates the post on Blogger (no duplicates!)
- Saves the `blogger_id` back to frontmatter for future updates

When I'm ready to go live, I just change `status: draft` to `status: published` in the markdown and run `/publish` again. **One command. Live blog post.**

## The Technical Stack

Here's what makes this work:

### AI Content Generation
- **Claude Code (Anthropic Sonnet 4.5)** - Converts rambling to structured posts
- **OpenAI GPT-Image-1** - Generates custom blog images from prompts

### Content Pipeline
- **Python 3.13** with `uv` for dependency management
- **Markdown → HTML** conversion with Python-Markdown
- **Pygments** for code syntax highlighting
- **YAML frontmatter** for metadata (title, date, tags, status)

### Infrastructure
- **Cloudinary** - Image CDN with automatic WebP conversion
- **Google Blogger API** - Publishing platform (with OAuth 2.0)
- **Vale** - Prose linting for readability and style
- Custom **SEO checker** - Validates title length, meta descriptions, headings, content length

### Smart Features
- **Idempotent publishing** - Detects existing posts by directory path, updates instead of duplicating
- **Hash-based image deduplication** - Only uploads changed images to Cloudinary
- **Tag registry** - Enforced tag consistency (no tag sprawl!)
- **Path-based URLs** - `2025-10-12-hello-world` → `/2025/10/hello-world.html`

## The Architecture: How Everything Fits Together

![Blog automation architecture diagram](./diagram-blog-automation-architecture.png)

Here's the flow:

1. **Voice/Text Input** → Claude Code `/create-post` command
2. **AI Processing** → Structured markdown + image prompts + frontmatter
3. **Image Generation** → OpenAI API → Saved to post directory
4. **Build Step** → Validates tags, converts markdown, generates preview HTML
5. **Quality Checks** → SEO analysis + Vale prose linting (optional)
6. **Publish Step** →
   - Upload images to Cloudinary (if changed)
   - Convert markdown to HTML with Pygments
   - Create/update post via Blogger API
   - Save `blogger_id` to frontmatter
7. **Status Toggle** → Change `draft` → `published` and republish

Everything is idempotent—you can run commands many times safely. The system is smart enough to:
- Detect existing posts by directory name
- Only upload images when their hashes change
- Update instead of duplicate
- Preserve your `blogger_id` across runs

## What This Actually Looks Like in Practice

Let me show you a real example. Here's my actual workflow from 30 minutes ago (yes, this is the meta-post about itself):

```bash
# 1. Talk about my idea (literally just rambled into Claude Code)
/create-post So today I made a really cool tech thing...

# 2. Claude wrote the post AND generated the images automatically!

# 3. Optional: Run quality checks
/quality-check posts/2025-10-12-voice-to-blog-automation/

# 4. Build and preview
/build posts/2025-10-12-voice-to-blog-automation/

# 5. Publish as draft
/publish posts/2025-10-12-voice-to-blog-automation/

# 6. Review on Blogger, then publish live
# (Edit status: draft → published in post.md)
/publish posts/2025-10-12-voice-to-blog-automation/
```

**Total hands-on time: ~5 minutes** (most of it reviewing the AI output—the images generated automatically!)

Compare that to traditional blogging:
- Write in markdown editor: 45-60 minutes
- Find/create images: 20-30 minutes
- Format and optimize: 15-20 minutes
- Upload to blog platform: 10-15 minutes
- SEO checks: 10 minutes

**Old way: 2+ hours. New way: 5 minutes.**

## The Quality Checks: Making Sure It's Actually Good

One concern with AI-generated content: is it any good? Will it rank? Is it readable?

The `/quality-check` command runs two automated checks:

### 1. SEO Analysis

Checks for search optimization best practices:
- ✅ Title length (30-60 chars for Google)
- ✅ Meta description (150-160 chars)
- ✅ Heading structure (single H1, proper H2/H3 hierarchy)
- ✅ Content length (300+ words recommended)
- ✅ Image alt text
- ✅ Internal/external links
- ✅ Keyword density

**Example output:**
```
✅ Title length: 52 characters (optimal)
✅ Single H1 heading found
✅ Content length: 1,847 words
⚠️  Add meta description for search results
✅ 3 images with alt text
```

### 2. Prose Linting with Vale

Vale checks writing quality automatically:
- Passive voice detection
- Readability scores
- Clichés and weasel words
- Technical writing best practices

**Example output:**
```
 12:34  suggestion  'really' is a weasel word  write-good.Weasel
 45:12  warning     This sentence is too long  write-good.TooWordy
```

You can ignore suggestions, but the system catches common mistakes before publishing. Run `/quality-check` on any post to get instant feedback.

## Why This Matters: The Future of Content Creation

This isn't just about saving time (though that's significant). It's about **removing friction from the creative process**.

When you have an idea, the momentum is **right now**. But by the time you've:
- Opened your markdown editor
- Formatted the frontmatter
- Found stock images
- Remembered how to publish to Blogger
- Dealt with OAuth tokens expiring
- Manually uploaded images

...the moment has passed. You've talked yourself out of it.

With this system, the barrier is **as low as talking**. You're 5 minutes from published draft.

### What's Next?

I'm planning to add:
- **Automatic social media posts** (LinkedIn, Twitter) from blog content
- **Voice-to-text input** (literally just record audio, get blog post)
- **Multi-platform publishing** (Dev.to, Medium, Hashnode)
- **Analytics integration** (track what actually performs)
- **Automated internal linking** (connect related posts automatically)

## What's Coming Next

This blog will dive deep into each piece of this automation pipeline—from setting up the Blogger API and OAuth flows, to building the markdown converter, to integrating Cloudinary for image optimization. I'll walk through the architecture decisions, the code, and the lessons learned along the way.

But here's where it gets even more interesting: **adding an agentic layer on top**.

Imagine the system automatically:
- Generating follow-up posts based on engagement metrics
- Creating social media threads from your blog content
- Suggesting related topics based on trending searches
- Autonomously maintaining and updating older posts
- Building internal link networks between related content

We're just scratching the surface of what's possible when you combine AI agents with content workflows.

**Stay tuned for more.** The future of content creation is autonomous, and we're going to build it together.

## Conclusion: Just Talk and Ship

The best blogging system is the one you actually use. If the friction is low enough, you'll write more. If you write more, you'll get better. If you get better, you'll reach more people.

This system removes the boring parts and lets you focus on the only thing that matters: **having something to say**.

Stop wrestling with markdown formatting and image optimization. **Just talk about your idea and ship it.**

