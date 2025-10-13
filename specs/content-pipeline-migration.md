# Content Generation Pipeline Migration Plan

## Overview

Migrate the content generation pipeline from Blogger + Cloudinary to Next.js + Vercel. This eliminates external API dependencies and simplifies the workflow to: **create → validate → commit → deploy**.

---

## Current vs New Architecture

### Current Workflow (Blogger + Cloudinary)
```
/create-post <idea>
  ↓
posts/YYYY-MM-DD-slug/post.md (Markdown)
  ↓
/quality-check (Vale + SEO)
  ↓
/build (validate, preview HTML)
  ↓
/publish (upload images to Cloudinary, publish to Blogger API)
  ↓
Blogger (live on Internet)
```

### New Workflow (Next.js + Vercel)
```
/create-post <idea>
  ↓
website/content/posts/YYYY-MM-DD-slug.mdx (MDX with proper frontmatter)
website/public/blog/YYYY-MM-DD-slug/*.webp (images)
  ↓
/quality-check (Vale + SEO)
  ↓
/build (validate Next.js build, check for errors)
  ↓
git add . && git commit -m "..." && git push
  ↓
Vercel auto-deploy (live on Internet)
```

**Key Changes:**
- ✅ No `/publish` command needed (replaced by git push → Vercel)
- ✅ No Cloudinary uploads (images committed to Git)
- ✅ No Blogger API calls (static site generation)
- ✅ Output directly to `website/` subdirectory
- ✅ MDX format with Next.js-specific frontmatter
- ✅ Category validation against hardcoded list

---

## Command Changes

### 1. `/create-post` - Major Refactor ✏️

**Old Output:**
- `posts/YYYY-MM-DD-slug/post.md` (Markdown)
- `posts/YYYY-MM-DD-slug/*.png` (images)
- Frontmatter: `title`, `date`, `tags`, `status`

**New Output:**
- `website/content/posts/YYYY-MM-DD-slug.mdx` (MDX)
- `website/public/blog/YYYY-MM-DD-slug/*.webp` (images)
- Frontmatter: `title`, `description`, `date`, `category`, `hashtags`

**Changes Required:**
- Update output paths to `website/` subdirectory
- Change file extension from `.md` to `.mdx`
- Remove multi-file structure (single MDX file, no directory)
- Update frontmatter schema:
  - Remove: `status`, `blogger_id`, `updated`, `images`
  - Add: `description` (required for SEO)
  - Rename: `tags` → `hashtags`
  - Add: `category` (required, validated against 7 categories)
- Images:
  - Generate as WebP format (already doing this with `convert_to_webp.py`)
  - Save to `website/public/blog/YYYY-MM-DD-slug/`
  - Reference in MDX with relative paths: `./image.webp`
- Category validation:
  - Must pick ONE category from: `tutorials`, `case-studies`, `guides`, `lists`, `comparisons`, `problem-solution`, `opinions`
  - AI should analyze content and pick best-fit category
  - Fail if invalid category provided

**Category Selection Logic:**
```
tutorials       - Step-by-step how-to guides
case-studies    - Real-world project showcases
guides          - Beginner-friendly fundamentals
lists           - Tips, tools, strategies
comparisons     - Product/approach comparisons
problem-solution - Addressing pain points
opinions        - Perspectives, myth-busting
```

### 2. `/build` - Major Refactor 🔨

**Old Behavior:**
- Validate Markdown syntax
- Check image references
- Convert to HTML with Pygments
- Generate `preview.html` file
- Check for Cloudinary cache

**New Behavior:**
- Validate MDX syntax
- Check image references (relative paths)
- Validate frontmatter (category, description, etc.)
- Run Next.js build in `website/` directory
- Report TypeScript/build errors
- NO preview HTML generation (use `pnpm dev` instead)

**Implementation:**
```bash
cd website && pnpm run build
```

### 3. `/quality-check` - Minor Updates ✅

**Keep mostly as-is:**
- Vale prose linting still works on MDX files
- SEO checks still valid (title, description, headings, etc.)

**Changes:**
- Update path handling for `website/content/posts/*.mdx`
- Validate `category` field exists and is valid
- Validate `description` field exists and is 150-160 chars

### 4. `/publish` - REMOVE ❌

**Reason:** No longer needed. Deployment is handled by:
```bash
git add .
git commit -m "Add new blog post"
git push origin main
# Vercel auto-deploys
```

**Alternative:** Could create a `/deploy` command that:
1. Runs `/build` to validate
2. Creates git commit with AI-generated message
3. Pushes to origin
4. Shows Vercel deployment URL

### 5. `/create-quality-build-publish` - Refactor 🔄

**Rename to:** `/create-quality-build`

**New workflow:**
1. Get next publish date (still use `next_publish_date.py`)
2. Run `/create-post` (outputs to `website/`)
3. Run `/quality-check` (validates MDX)
4. Run `/build` (validates Next.js build)
5. **Stop here** - user manually commits and pushes

**Optional:** Add `/create-quality-build-deploy` that includes git operations

### 6. `/sync-publish-status` - REMOVE ❌

**Reason:** No Blogger API to sync from. Post status is determined by:
- Future dates → hidden by `getPublishedPosts()` in Next.js
- Git history → source of truth

---

## Tool Changes

### Keep (with modifications)

#### `tools/generate_image.py` ✅
- Keep as-is (generates PNG from OpenAI)
- Still used by `/create-post` command

#### `tools/convert_to_webp.py` ✅
- Keep as-is
- Used by `/create-post` to convert generated images to WebP

#### `tools/next_publish_date.py` ✅
- Keep as-is
- Still scans `posts/` directory for dates
- **Future:** Could also scan `website/content/posts/*.mdx` for consistency

#### `tools/seo_check.py` ✅
- Keep with minor updates
- Update path handling for MDX files
- Add category validation check
- Add description field check

#### `tools/list_tags.py` ⚠️
- **Decision:** Keep or remove?
- **Option 1:** Remove (hashtags are freeform, no registry)
- **Option 2:** Adapt to list categories instead
- **Recommendation:** Remove (hashtags don't need registry)

#### `tools/add_tag.py` ⚠️
- **Recommendation:** Remove (hashtags are freeform)

### Remove (obsolete)

#### `tools/build.py` ❌
- Replaced by `cd website && pnpm run build`
- Old logic: Markdown → HTML conversion, Cloudinary cache checks
- New logic: Next.js handles all build logic

#### `tools/publish.py` ❌
- No Blogger API calls needed
- No Cloudinary uploads needed
- Deployment is handled by Vercel

#### `tools/sync-publish-status.py` ❌
- No Blogger API to sync from

#### `tools/test_auth.py` ⚠️
- **Decision:** Remove or keep for historical reference?
- **Recommendation:** Remove (no Blogger/Cloudinary auth needed)

#### `tools/generate_refresh_token.py` ❌
- No OAuth needed

#### `tools/setup_check.py` ⚠️
- **Decision:** Update or remove?
- **Option 1:** Remove entirely
- **Option 2:** Refactor to check Next.js setup instead
  - Verify `website/` exists
  - Check `pnpm` installed
  - Verify `OPENAI_API_KEY` for image generation
  - Test Next.js build
- **Recommendation:** Option 2 - useful for onboarding

### Create New Tools

#### `tools/create_mdx_post.py` 🆕
- Extract post creation logic from command
- Generate MDX file in `website/content/posts/`
- Generate images in `website/public/blog/`
- Validate category selection
- Handle frontmatter schema

#### `tools/validate_mdx.py` 🆕 (Optional)
- Standalone validation for MDX files
- Check frontmatter schema
- Validate category
- Check image references
- Alternative: Just use Next.js build

---

## Library (`lib/`) Changes

### Remove (Blogger/Cloudinary specific)

#### `lib/blogger_client.py` ❌
- No longer needed (no Blogger API)

#### `lib/cloudinary_uploader.py` ❌
- No longer needed (images committed to Git)

#### `lib/image_processor.py` ⚠️
- **Keep parts:** Image optimization, hash computation (still useful)
- **Remove parts:** Cloudinary upload logic
- **Decision:** Simplify or remove entirely?
- **Recommendation:** Keep minimal version for image validation

#### `lib/markdown_converter.py` ❌
- No longer needed (Next.js handles MDX rendering)
- Pygments styling replaced by react-syntax-highlighter

### Keep (core functionality)

#### `lib/config.py` ⚠️
- **Update:** Remove Blogger/Cloudinary config
- **Keep:** OPENAI_API_KEY, blog metadata
- **Add:** Website paths (`website/content/posts/`, `website/public/blog/`)

#### `lib/frontmatter.py` ✅
- Keep YAML parsing logic
- Update schema validation for new frontmatter

#### `lib/validator.py` ⚠️
- **Keep:** Post directory validation, frontmatter validation
- **Remove:** Blogger path derivation, Cloudinary cache checks
- **Add:** Category validation against hardcoded list
- **Add:** MDX-specific validation

---

## Configuration Changes

### Files to Update

#### `blog-config.yaml` ⚠️
**Current:**
```yaml
blog_name: "Agentic Engineer Blog"
blogger_blog_id: "..."
image_optimization: {...}
cloudinary: {...}
markdown: {...}
```

**New:**
```yaml
blog_name: "The Agentic Engineer"
domain: "the-agentic-engineer.com"

# Paths
website_dir: "website"
content_dir: "website/content/posts"
public_images_dir: "website/public/blog"

# Image generation
image_generation:
  default_size: "1024x1024"
  format: "webp"
  quality: 85

# Categories (validation reference)
categories:
  - tutorials
  - case-studies
  - guides
  - lists
  - comparisons
  - problem-solution
  - opinions
```

#### `.env` / `.env.local` ⚠️
**Remove:**
```bash
BLOGGER_CLIENT_ID=...
BLOGGER_CLIENT_SECRET=...
BLOGGER_REFRESH_TOKEN=...
CLOUDINARY_CLOUD_NAME=...
CLOUDINARY_API_KEY=...
CLOUDINARY_API_SECRET=...
```

**Keep:**
```bash
OPENAI_API_KEY=...
```

#### `pyproject.toml` ⚠️
**Remove dependencies:**
```toml
google-auth
google-auth-oauthlib
google-api-python-client
cloudinary
Pygments  # (Next.js uses react-syntax-highlighter)
markdown-it-py  # (Next.js uses react-markdown)
mdit-py-plugins  # (Next.js plugin)
```

**Keep dependencies:**
```toml
Pillow  # (image processing)
PyYAML  # (frontmatter parsing)
python-dotenv  # (env loading)
openai  # (image generation)
requests  # (general HTTP)
```

**Minimal dependency list:**
```toml
[project]
name = "agentic-engineer-blog"
version = "2.0.0"
requires-python = ">=3.10"
dependencies = [
    "Pillow>=11.0.0",
    "PyYAML>=6.0.2",
    "python-dotenv>=1.0.1",
    "openai>=1.0.0",
    "requests>=2.31.0",
]
```

#### `tag-registry.yaml` ❌
**Remove:** Hashtags are now freeform (no registry needed)

---

## Migration Checklist

### Phase 5.5: Content Pipeline Migration (NEW)

#### Step 1: Update `/create-post` command ✏️
- [ ] Update command prompt in `.claude/commands/create-post.md`
  - Change output format from Markdown to MDX
  - Update frontmatter schema (add `description`, `category`, remove `status`, `tags`)
  - Change output paths to `website/content/posts/*.mdx`
  - Change image paths to `website/public/blog/YYYY-MM-DD-slug/*.webp`
  - Add category selection logic (AI picks from 7 options)
  - Update image reference format (relative paths: `./image.webp`)

#### Step 2: Update `/build` command 🔨
- [ ] Rewrite `.claude/commands/build.md`
  - Remove Markdown → HTML conversion logic
  - Replace with `cd website && pnpm run build`
  - Parse Next.js build output for errors
  - Report TypeScript/ESLint/build errors
  - Remove preview HTML generation

#### Step 3: Update `/quality-check` command ✅
- [ ] Update `.claude/commands/quality-check.md`
  - Update path handling for MDX files in `website/content/posts/`
  - Add category validation check
  - Add description field validation
- [ ] Update `tools/seo_check.py`
  - Add category validation
  - Add description field check (150-160 chars)

#### Step 4: Refactor combined workflow 🔄
- [ ] Rename `.claude/commands/create-quality-build-publish.md` to `create-quality-build.md`
- [ ] Update workflow to stop at build step (no publish)
- [ ] Add note about manual git commit/push
- [ ] Optional: Create `/create-quality-build-deploy` with git operations

#### Step 5: Remove obsolete commands ❌
- [ ] Delete `.claude/commands/publish.md`
- [ ] Delete `.claude/commands/sync-publish-status.md`

#### Step 6: Update/remove tools 🛠️
- [ ] Keep: `generate_image.py`, `convert_to_webp.py`, `next_publish_date.py`
- [ ] Update: `seo_check.py` (category + description validation)
- [ ] Optional: Update `setup_check.py` for Next.js validation
- [ ] Delete: `publish.py`, `sync-publish-status.py`, `test_auth.py`, `generate_refresh_token.py`
- [ ] Optional: Delete `list_tags.py`, `add_tag.py` (hashtags are freeform)
- [ ] Delete: `build.py` (replaced by Next.js build)

#### Step 7: Update libraries 📚
- [ ] Delete: `lib/blogger_client.py`, `lib/cloudinary_uploader.py`, `lib/markdown_converter.py`
- [ ] Update: `lib/config.py` (remove Blogger/Cloudinary config)
- [ ] Update: `lib/validator.py` (add category validation, remove Blogger logic)
- [ ] Keep: `lib/frontmatter.py` (update schema)
- [ ] Simplify: `lib/image_processor.py` (keep optimization, remove upload logic)

#### Step 8: Update configuration files 📋
- [ ] Update `blog-config.yaml` (remove Blogger/Cloudinary, add website paths + categories)
- [ ] Delete `tag-registry.yaml` (hashtags are freeform)
- [ ] Update `pyproject.toml` (remove 7+ dependencies, keep 5 minimal ones)
- [ ] Document `.env` cleanup (user action: remove Blogger/Cloudinary keys)

#### Step 9: Update documentation 📖
- [ ] Update `README.md` main workflow section
  - Replace `/publish` with git commit + push
  - Update command list
  - Remove Blogger/Cloudinary setup instructions
  - Add Next.js development workflow (`pnpm dev` for local preview)
- [ ] Update `specs/nextjs-migration-resources.md`
  - Mark Phase 5.5 complete
  - Update overall project status to ~90%
- [ ] Optional: Create migration guide for existing posts

---

## Testing Plan

### After Migration

1. **Test post creation:**
   ```
   /create-post Test post about Next.js migration workflow
   ```
   - Verify MDX file created in `website/content/posts/`
   - Verify images in `website/public/blog/`
   - Verify frontmatter schema (description, category, hashtags)
   - Verify category is valid

2. **Test quality checks:**
   ```
   /quality-check website/content/posts/YYYY-MM-DD-test-post.mdx
   ```
   - Vale runs successfully
   - SEO checks pass
   - Category validation works

3. **Test build:**
   ```
   /build website/content/posts/YYYY-MM-DD-test-post.mdx
   ```
   - Next.js build succeeds
   - No TypeScript errors
   - Images resolve correctly

4. **Test end-to-end:**
   ```
   /create-quality-build Test post idea
   ```
   - All steps run successfully
   - Post ready for commit

5. **Test deployment:**
   ```bash
   git add .
   git commit -m "Add test post"
   git push origin main
   ```
   - Vercel deploys successfully
   - Post visible on live site
   - Images load correctly
   - Category filter works

---

## Rollback Plan

If migration causes issues:

1. **Keep old `posts/` directory** as backup
2. **Tag Git commit** before migration: `git tag pre-nextjs-migration`
3. **Rollback:** `git reset --hard pre-nextjs-migration`
4. **Old commands still in Git history** (can cherry-pick back if needed)

---

## User Action Items

### Environment Cleanup (Cannot be done by Claude)

**Remove from `.env` or `.env.local`:**
```bash
# REMOVE THESE - No longer needed
BLOGGER_CLIENT_ID=...
BLOGGER_CLIENT_SECRET=...
BLOGGER_REFRESH_TOKEN=...
CLOUDINARY_CLOUD_NAME=...
CLOUDINARY_API_KEY=...
CLOUDINARY_API_SECRET=...
```

**Keep in `.env.local`:**
```bash
# KEEP THIS - Still needed for image generation
OPENAI_API_KEY=...
```

### Optional Cleanup

1. **Delete old `posts/` directory** (after verifying migration successful)
2. **Remove Blogger credentials** from Google Cloud Console (optional)
3. **Close Cloudinary account** (optional, if not used elsewhere)

---

## Summary

**Before:**
- Complex pipeline: Markdown → Cloudinary → Blogger API
- 14 tools, 7 lib modules, 6 Claude commands
- External dependencies: Google OAuth, Cloudinary, Blogger API
- Multi-step publishing process

**After:**
- Simple pipeline: MDX → Git → Vercel
- ~8 tools (6 removed), ~3 lib modules (4 removed), 4 Claude commands (2 removed)
- Minimal dependencies: OpenAI (images only), Vale (optional)
- One-step deployment: `git push`

**Benefits:**
- ✅ Simpler workflow
- ✅ Fewer moving parts
- ✅ No external API rate limits
- ✅ No OAuth token refresh issues
- ✅ Instant preview via `pnpm dev`
- ✅ Version control for everything (including images)
- ✅ Cheaper (no Cloudinary costs)
- ✅ Faster (no API round trips)
