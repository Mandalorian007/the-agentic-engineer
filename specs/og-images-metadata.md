# Open Graph & Twitter Card Images

**Date**: 2025-10-21
**Context**: Add social media preview images (OG/Twitter cards) to blog posts

---

## Overview

**Problem**: Blog posts shared on X/Twitter and other social platforms don't show preview images, reducing engagement and perceived quality despite having high-quality social post content.

**Solution**: Add Open Graph and Twitter Card metadata with hero images from each post to Next.js metadata generation.

**Outcome**: Blog post links show rich preview cards with hero images, title, and description on all social platforms.

---

## Phase 1: Requirements & Approach

### What We're Building

**Current State**: Blog posts have `openGraph` metadata with title/description but no images (website/app/blog/[slug]/page.tsx:52-58).

**Pain Point**: Social shares appear as text-only previews, failing to showcase the high-quality hero images already generated for each post.

**Success Criteria**:
- ✅ All blog posts include `openGraph.images` and `twitter.card` metadata
- ✅ Hero images (format: `hero-*.webp`) automatically detected from post image directory
- ✅ Twitter card validator shows rich preview with image
- ✅ LinkedIn/Facebook show proper OG image previews
- ✅ No impact on existing build/deploy pipeline

### How We're Building It

**Approach**: Enhance existing `generateMetadata()` in blog post page to detect hero image from public directory and add both Open Graph and Twitter Card metadata.

**Tools/Technologies**:
- Next.js Metadata API (already in use)
- Node.js `fs` for image detection
- Standard OG/Twitter Card meta tags

**Rationale**:
- Fits pattern: Extends existing metadata generation in website/app/blog/[slug]/page.tsx:39-59
- Minimal risk: Only adds metadata fields, doesn't modify rendering
- Reuses: Existing slug-based image path convention (`/blog/{slug}/hero-*.webp`)

**Rejected Alternatives**:
- Dynamic OG image generation (Next.js ImageResponse): Unnecessary complexity when hero images already exist
- Manual frontmatter field: Violates DRY principle, hero images follow predictable naming

> Implementation agent: Follow ONLY the selected approach above.

### Architecture

**Components**:
```
website/app/blog/[slug]/
└── page.tsx              # Add hero image detection + OG/Twitter metadata

website/lib/
└── og-image.ts           # NEW: Utility to find hero image for a post slug
```

**Integration Points**:
- Internal: Extends `generateMetadata()` in website/app/blog/[slug]/page.tsx
- External: Twitter Card validator, Facebook debugger, LinkedIn preview

### Codebase Context

**Relevant Files**:
- `website/app/blog/[slug]/page.tsx:39-59` - Current metadata generation (title, description, basic openGraph)
- `website/public/blog/` - Image directory structure (one subdirectory per post with `hero-*.webp`)
- `website/app/layout.tsx:22-25` - Root metadata (shows pattern for Metadata object)

**Patterns to Follow**:
- Metadata generation: See `website/app/blog/[slug]/page.tsx:39-59`
- Image path conversion: See `website/app/blog/[slug]/page.tsx:206-217` (relative to absolute paths)

**Don't Touch**:
- `website/app/blog/[slug]/page.tsx:74-105` - JSON-LD structured data (separate from metadata)
- Image rendering logic - Only metadata needs changes

---

## Phase 2: Implementation Tasks

### Task 1: Create Hero Image Detection Utility

**Create**:
- Create `website/lib/og-image.ts` - Hero image finder

**What to Do**:
- [ ] Export function `getHeroImagePath(slug: string): string | null`
- [ ] Use `fs.readdirSync()` to scan `/public/blog/{slug}/` directory
- [ ] Find first file matching pattern `hero-*.webp`
- [ ] Return absolute URL path: `https://the-agentic-engineer.com/blog/{slug}/hero-{name}.webp`
- [ ] Return `null` if directory doesn't exist or no hero image found
- [ ] Edge case: Handle missing directories gracefully (return null, don't throw)
- [ ] Edge case: Handle multiple hero images (return first match alphabetically)

**Verify**: Create test with `getHeroImagePath('2025-11-20-afternoon-build-full-stack-saas')` returns full URL

---

### Task 2: Add OG Image to Metadata

**Modify**:
- Modify `website/app/blog/[slug]/page.tsx` - Update `generateMetadata()`

**What to Do**:
- [ ] Import `getHeroImagePath` from `@/lib/og-image`
- [ ] Call `getHeroImagePath(params.slug)` to get hero image URL
- [ ] Add `openGraph.images` array with hero image if found
- [ ] Include image width (1024) and height (1024) in metadata
- [ ] Add `openGraph.url` with full post URL
- [ ] Keep existing `openGraph.type: "article"` and `publishedTime`
- [ ] Edge case: If no hero image, omit `openGraph.images` field entirely

**Verify**: Inspect page source for `<meta property="og:image" content="...hero-*.webp" />`

---

### Task 3: Add Twitter Card Metadata

**Modify**:
- Modify `website/app/blog/[slug]/page.tsx` - Add Twitter Card fields to metadata return

**What to Do**:
- [ ] Add `twitter.card: "summary_large_image"` for large image preview
- [ ] Add `twitter.title` matching post title
- [ ] Add `twitter.description` matching post description
- [ ] Add `twitter.images` array with same hero image URL
- [ ] Use same conditional: only include Twitter fields if hero image exists
- [ ] Edge case: Gracefully degrade to summary card if no image (omit twitter.images)

**Verify**: Test with Twitter Card Validator (https://cards-dev.twitter.com/validator)

---

### Task 4: Update Type Imports

**Modify**:
- Modify `website/app/blog/[slug]/page.tsx` - Ensure proper TypeScript types

**What to Do**:
- [ ] Verify `Metadata` type import from `next` handles new fields
- [ ] No additional imports needed (twitter/openGraph fields are standard Metadata)
- [ ] Ensure return type of `generateMetadata()` remains `Promise<Metadata>`

**Verify**: `pnpm lint` passes with no TypeScript errors

---

### Implementation Notes

**Follow Patterns**: Image URL construction follows pattern in website/app/blog/[slug]/page.tsx:206-217

**Naming Conventions**: Use camelCase for functions (`getHeroImagePath`), PascalCase for types

**Special Considerations**:
- All image URLs must be absolute (include full domain) for social platform compatibility
- Hero image detection runs at build time (SSG), not runtime—safe for `fs` usage
- Domain hardcoded as `https://the-agentic-engineer.com` (matches existing JSON-LD pattern line 82)

---

## Phase 3: Verification & Acceptance

### Automated Checks

**Build**:
```bash
cd website && pnpm lint
```
✅ Expected: No ESLint or TypeScript errors

**Build Verification**:
```bash
cd website && pnpm build
```
✅ Expected: Static pages generate successfully with metadata

### Manual Verification

- [ ] **X/Twitter**: Paste blog post URL into https://cards-dev.twitter.com/validator → ✅ Expected: Shows hero image, title, description
- [ ] **LinkedIn**: Share blog post URL → ✅ Expected: Rich preview with hero image
- [ ] **Facebook**: Test with https://developers.facebook.com/tools/debug/ → ✅ Expected: OG image displays
- [ ] **Page Source**: View source of blog post → ✅ Expected: Meta tags for `og:image`, `twitter:card`, `twitter:image` present
- [ ] **Post without hero**: Test with post that has no hero image → ✅ Expected: No broken image tags, graceful degradation

### Acceptance Criteria

**Functional**:
- [ ] All existing posts show hero images in social previews
- [ ] OG metadata includes absolute image URLs with domain
- [ ] Twitter Card shows as `summary_large_image` type
- [ ] Missing hero images handled gracefully (no errors)
- [ ] Image detection works for all naming patterns (`hero-*.webp`)

**Non-Functional**:
- [ ] Performance: No impact on build time (hero detection is fast fs operation)
- [ ] Compatibility: Previews work on Twitter, LinkedIn, Facebook

**Integration**:
- [ ] No regressions: Existing metadata (title, description) still present
- [ ] Works with: ISR revalidation (metadata regenerates with pages)

**Definition of Done**:
- [ ] All success criteria validated
- [ ] Twitter Card validator passes
- [ ] Code follows existing metadata patterns
- [ ] Lint and build pass
- [ ] No impact on existing post rendering

---

## Phase 4: Documentation Updates

### Files to Update

**`README.md`**:
- Section: Features (line 5-15)
- Add: `- ✅ **Social Media Previews**: Rich cards with hero images for X/Twitter, LinkedIn, Facebook`

**`docs/architecture.md`**:
- Section: SEO Features (line 470-479)
- Add:
  - Open Graph images (hero images from posts)
  - Twitter Card metadata (summary_large_image)
  - Automatic hero image detection from public/blog/{slug}/

**`docs/architecture.md`**:
- Section: Post Format → Image References (line 242-256)
- Add: Note that hero images (hero-*.webp) are automatically used for social media previews

---

## End of Template
