# Next.js Migration Plan

This document defines the architecture and migration plan for The Agentic Engineer Blog from Blogger to Next.js.

## Overview

Migrating from current Markdown + Blogger + Cloudinary setup to a **simple, self-contained Next.js blog** hosted on Vercel.

**Branding & Domain:**
- **Blog Name**: The Agentic Engineer
- **Domain**: the-agentic-engineer.com
- All branding should use "The Agentic Engineer" naming

**Core Philosophy:**
- ✅ Simple, maintainable, Git-based workflow
- ✅ No external CDN dependencies (no Cloudinary)
- ✅ Static generation (SSG) for best SEO and performance
- ✅ Local images served via Vercel CDN
- ✅ MDX-first content with relative image paths

---

## Architecture Decision: Option 1 (MDX + File-Based Routing)

### Directory Structure

```
the-agentic-engineer/
├── app/
│   ├── page.tsx                        # Homepage
│   ├── blog/
│   │   ├── page.tsx                    # Blog listing page (all posts)
│   │   ├── category/
│   │   │   └── [category]/
│   │   │       └── page.tsx            # Category filter page
│   │   └── [slug]/
│   │       └── page.tsx                # Dynamic blog post page
│   ├── layout.tsx                      # Root layout (navbar, footer)
│   └── sitemap.ts                      # Auto-generated sitemap
├── content/
│   └── posts/
│       ├── 2025-10-12-voice-to-blog-automation.mdx
│       └── 2025-10-13-taming-claude-yolo-mode.mdx
├── public/
│   └── blog/
│       ├── 2025-10-12-voice-to-blog-automation/
│       │   ├── hero-voice-to-blog-pipeline.webp
│       │   └── diagram-blog-automation-architecture.webp
│       └── 2025-10-13-taming-claude-yolo-mode/
│           ├── hero-safe-yolo-mode.webp
│           └── diagram-hook-flow.webp
├── lib/
│   ├── posts.ts                        # Load and parse MDX files (with date filtering)
│   ├── categories.ts                   # Hardcoded categories + validation
│   └── remark-image-path.ts            # Rewrite relative image paths
├── components/
│   ├── ui/                             # shadcn/ui components
│   ├── blog-post-card.tsx              # Blog listing card with category/hashtags
│   ├── category-filter.tsx             # Category filter tabs
│   ├── hashtag-badge.tsx               # HashTag display badge (not clickable)
│   └── navbar.tsx                      # Navigation
├── mdx-components.tsx                  # Custom MDX components (next/image wrapper)
└── next.config.mjs                     # Next.js configuration
```

### URL Structure

```
/                                       # Homepage
/blog                                   # Blog listing (all posts)
/blog/category/[category]               # Filter by category
/blog/2025-10-12-voice-to-blog-automation  # Individual post
/blog/2025-10-13-taming-claude-yolo-mode   # Individual post
/sitemap.xml                            # Auto-generated sitemap
```

### MDX Format

**Example: content/posts/2025-10-12-voice-to-blog-automation.mdx**

```mdx
---
title: "Voice to Blog Automation"
description: "Build an automated blog publishing pipeline with Claude Code"
date: "2025-10-12T10:00:00Z"
category: "case-studies"
hashtags: ["ai-agents", "python", "claude-code", "workflow-automation"]
---

![Hero image showing voice-to-blog pipeline](./hero-voice-to-blog-pipeline.webp)

## Introduction

Your blog content here...

![Architecture diagram](./diagram-blog-automation-architecture.webp)

More content with **bold** and _italic_ text.
```

**Frontmatter Fields:**
- `title` (required) - Post title
- `description` (required) - SEO meta description
- `date` (required) - ISO 8601 date (posts with future dates are hidden until that date)
- `category` (required) - Primary category (must be one of 7 hardcoded categories)
- `hashtags` (optional) - Array of freeform hashtags for display only

### How Images Work

1. **Store images** in `public/blog/[slug]/image.webp`
2. **Reference in MDX** with relative paths: `./image.webp`
3. **Custom remark plugin** rewrites `./image.webp` → `/blog/[slug]/image.webp` at build time
4. **Custom MDX component** wraps `<img>` tags with `next/image` for automatic optimization
5. **Vercel CDN** serves optimized images (WebP, responsive sizes, lazy loading)

**No Cloudinary needed** - images are committed to Git, served from Vercel CDN.

### Tech Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Framework** | Next.js 15 (App Router) | React framework with SSG |
| **Hosting** | Vercel | Zero-config deployment + CDN |
| **Content** | MDX files | Markdown with frontmatter |
| **Rendering** | react-markdown + remark-gfm | Convert MDX to HTML |
| **Styling** | Tailwind CSS + @tailwindcss/typography | Utility-first CSS + prose |
| **Components** | shadcn/ui | Pre-built UI components |
| **Images** | next/image | Automatic optimization |
| **Code Highlighting** | react-syntax-highlighter | Code blocks with themes |

### SEO Features

✅ **Static Generation (SSG)** - `generateStaticParams()` pre-renders all posts at build time
✅ **Dynamic Metadata** - `generateMetadata()` per post for title, description, Open Graph
✅ **Auto Sitemap** - `app/sitemap.ts` generates XML sitemap from posts
✅ **Image Optimization** - `next/image` handles alt text, dimensions, lazy loading
✅ **Clean URLs** - Semantic, hackable URLs matching current date-based structure
✅ **robots.txt** - Auto-generated by Next.js
✅ **Structured Data** - JSON-LD BlogPosting schema (implement in post page)

### Category & HashTag System Design

**Philosophy:**
- **Categories** = Primary classification for navigation/filtering (single choice per post, validated)
- **HashTags** = Secondary metadata for visual scanning (multiple per post, freeform, display-only)
- No registry files needed - categories hardcoded in TypeScript, hashtags are freeform

**Hardcoded Categories (`lib/categories.ts`):**

Aligned with blog post formats from `/create-post` command:

```typescript
export const CATEGORIES = {
  'tutorials': {
    name: 'Tutorials & How-Tos',
    description: 'Step-by-step guides teaching skills and processes'
  },
  'case-studies': {
    name: 'Case Studies',
    description: 'Real-world project showcases and results'
  },
  'guides': {
    name: 'Guides & Fundamentals',
    description: 'Beginner-friendly introductions to complex topics'
  },
  'lists': {
    name: 'Lists & Tips',
    description: 'Curated collections of tools, tips, and strategies'
  },
  'comparisons': {
    name: 'Comparisons & Reviews',
    description: 'Side-by-side comparisons and product reviews'
  },
  'problem-solution': {
    name: 'Problem & Solution',
    description: 'Addressing pain points with practical solutions'
  },
  'opinions': {
    name: 'Opinions & Analysis',
    description: 'Perspectives, analysis, and myth debunking'
  }
} as const;

export type CategoryId = keyof typeof CATEGORIES;
```

**HashTags:**
- Freeform array in frontmatter (no validation, no registry)
- Display-only badges on post cards (NOT clickable)
- No filter pages for hashtags
- Authors can use any hashtags they want

**UI Integration (blog27 layout):**
- **Category Filter Tabs**: Horizontal tabs at top of blog listing ("All", "Tutorials", "Case Studies", etc.)
- **HashTag Badges**: Displayed on each post card as visual labels (NOT clickable)
- **Active State**: Highlight selected category
- **Post Count**: Show count next to each category

**Example Post Card:**
```
┌─────────────────────────────────────┐
│ [Category Badge: Case Studies]       │
│                                      │
│ Voice-to-Blog Automation             │
│ Build an automated blog pipeline... │
│                                      │
│ #ai-agents #python #claude-code      │  ← Display-only badges (not clickable)
│                                      │
│ Oct 12, 2025 • 8 min read           │
└─────────────────────────────────────┘
```

### Scheduled Posts & Future Date Filtering

**Requirement:** Posts with future dates should not be visible until their publication date arrives.

**Implementation Options:**

**Option 1: Build-Time Filtering Only (Simplest)**
- Filter out future posts in `lib/posts.ts`
- Requires manual Vercel deploy when posts should go live
- ✅ **Pros**: Simple, no ISR complexity, works with static export
- ❌ **Cons**: Not automatic - must manually trigger deploy

**Option 2: ISR with Time-Based Revalidation (Recommended)**
- Set `revalidate = 3600` (1 hour) on blog pages
- Filter future posts at request time
- Pages rebuild hourly, picking up newly-published posts
- ✅ **Pros**: Automatic within ~1 hour, no manual intervention
- ✅ **Pros**: Works well with Vercel hosting
- ❌ **Cons**: Not instant (up to 1 hour delay)

**Option 3: ISR with Shorter Revalidation**
- Set `revalidate = 300` (5 minutes)
- More frequent rebuilds
- ✅ **Pros**: Faster publishing (5-min delay)
- ❌ **Cons**: More Vercel function invocations, higher costs at scale

**Option 4: On-Demand Revalidation via API Route**
- Create API route `/api/revalidate?secret=xxx`
- Use external cron job or GitHub Actions to ping API at post publish time
- Trigger immediate revalidation via `revalidatePath('/blog')`
- ✅ **Pros**: Instant publishing, precise control
- ❌ **Cons**: Requires external orchestration, more complex setup

**Option 5: GitHub Actions + Auto-Deploy**
- GitHub Actions workflow checks for posts with `date <= now` daily
- If found, triggers Vercel deploy hook
- ✅ **Pros**: Fully automated, no ISR needed
- ❌ **Cons**: Requires GitHub Actions setup, daily granularity only

**Recommendation: Start with Option 2 (ISR 1-hour), upgrade to Option 4 if needed**

**Implementation in `lib/posts.ts`:**
```typescript
export function getPublishedPosts(): Post[] {
  const allPosts = getAllPosts();
  const now = new Date();

  return allPosts.filter(post => {
    // Exclude future posts
    const postDate = new Date(post.date);
    if (postDate > now) return false;

    return true;
  });
}
```

**Revalidation Setup (Option 2):**
```typescript
// app/blog/page.tsx
export const revalidate = 3600; // 1 hour

// app/blog/[slug]/page.tsx
export const revalidate = 3600; // 1 hour
```

### Key Implementation Details

**1. Post Loading (`lib/posts.ts`)**
- Read MDX files from `content/posts/`
- Parse frontmatter (title, date, category, hashtags, description)
- Extract slug from filename
- Filter by date (exclude future posts)
- Sort by date descending
- Export `getAllPosts()`, `getPublishedPosts()`, `getPostBySlug(slug)`

**2. Category Management (`lib/categories.ts`)**
- Hardcoded TypeScript constant with 7 categories
- Validate post category at build time (fail build if invalid)
- Export `CATEGORIES`, `CategoryId`, `getCategoryById(id)`, `getPostsByCategory(categoryId)`
- Filter logic for category pages

**3. Image Path Rewriting (`lib/remark-image-path.ts`)**
- Custom remark plugin
- Rewrites `./image.webp` → `/blog/[slug]/image.webp`
- Injected into MDX processing pipeline

**4. Image Component (`mdx-components.tsx`)**
- Wraps `<img>` with `next/image`
- Automatic width/height, WebP conversion
- Lazy loading except hero images

**5. Dynamic Post Page (`app/blog/[slug]/page.tsx`)**
- `generateStaticParams()` - returns all post slugs for SSG
- `generateMetadata()` - dynamic SEO metadata per post
- Renders MDX with `MDXRemote` or `react-markdown`
- Displays category badge and hashtag badges

**6. Category Filter Page (`app/blog/category/[category]/page.tsx`)**
- `generateStaticParams()` - returns all 7 category IDs for SSG
- Filters posts by category using `getPostsByCategory()`
- Renders blog27 layout with filtered posts
- Shows category name and description

**7. Sitemap (`app/sitemap.ts`)**
- Reads all posts from `content/posts/`
- Includes category filter pages
- Returns array of URLs with lastModified dates
- Auto-generates `/sitemap.xml`

---

## Resources

### Date Added: 2025-10-13

#### shadcn/ui Setup
- **Command**: `pnpm dlx shadcn@latest init`
- **Description**: Initialize a new shadcn project with UI components
- **Category**: Tools & Libraries, Styling & UI

#### tweakcn Theme
- **URL**: https://tweakcn.com/editor/theme?theme=clean-slate
- **Theme**: Clean Slate
- **Description**: Custom theme for shadcn/ui components
- **Installation**: `pnpm dlx shadcn@latest add https://tweakcn.com/r/themes/clean-slate.json`
- **Important**: Must be installed AFTER shadcn init to properly override the default theme colors. This ensures the purple/blue accent colors are applied instead of grayscale.
- **Category**: Styling & UI

#### shadcnblocks - Blog Listing Layout
- **URL**: https://www.shadcnblocks.com/block/blog27
- **Block**: blog27
- **Installation**: `npx shadcn add @shadcnblocks/blog27` (after purchasing Pro)
- **Status**: PRO BLOCK - Requires purchase from shadcnblocks.com
- **Description**: Pre-built blog page layout with image slots, filters, and grid layout
- **Features**: Hero section with featured post image, category filter tabs, post cards with image slots
- **Alternative**: Currently using custom implementation with shadcn/ui Card components
- **Category**: Styling & UI, Architecture & Design

#### shadcnblocks - Blog Post Layout
- **URL**: https://www.shadcnblocks.com/block/blogpost5
- **Block**: blogpost5
- **Installation**: `npx shadcn add @shadcnblocks/blogpost5` (after purchasing Pro)
- **Status**: PRO BLOCK - Requires purchase
- **Description**: Pre-built individual blog post layout with sidebar
- **Alternative**: Currently using custom implementation
- **Category**: Styling & UI, Architecture & Design

#### shadcnblocks - Navbar
- **URL**: https://www.shadcnblocks.com/block/navbar8
- **Block**: navbar8
- **Status**: PRO BLOCK - Requires purchase
- **Description**: Navigation bar layout
- **Alternative**: Currently using custom navbar implementation with theme toggle
- **Category**: Styling & UI, Architecture & Design

#### shadcnblocks - Footer
- **URL**: https://www.shadcnblocks.com/block/footer16
- **Block**: footer16
- **Status**: PRO BLOCK - Requires purchase
- **Description**: Footer layout
- **Alternative**: Currently using custom footer implementation
- **Category**: Styling & UI, Architecture & Design

#### Note on shadcnblocks Pro - FIXED & WORKING
**Status**: Pro license purchased, registry correctly configured, blocks installing successfully!

**Setup Complete**:
- ✅ API key added to `.env` file (`SHADCNBLOCKS_API_KEY`)
- ✅ Registry configured in `components.json` with CORRECT URL format
  - **Fixed URL**: `https://shadcnblocks.com/r/{name}` (NOT `/api/registry/{name}.json`)
  - **Added**: Authorization header with API key
- ✅ Clean Slate theme properly installed from tweakcn
- ✅ blog27 component successfully installed at `components/blog27.tsx`

**Corrected Registry Configuration**:
```json
"registries": {
  "@shadcnblocks": {
    "url": "https://shadcnblocks.com/r/{name}",
    "headers": {
      "Authorization": "Bearer ${SHADCNBLOCKS_API_KEY}"
    }
  }
}
```

**Next Steps**:
1. ✅ Install blog27: `pnpm dlx shadcn@latest add @shadcnblocks/blog27` - DONE
2. Install remaining Pro blocks: blogpost5, navbar8, footer16
3. Replace custom placeholder components in `app/` pages with Pro block versions
4. Wire up Pro blocks with actual blog content (MDX posts)
5. Add images to Pro block image slots

**Key Files**:
- Setup guide: `specs/shadcnblocks-setup.md`
- Registry config: `website/components.json` (registries section - NOW FIXED)
- Environment: `website/.env.local` (contains API key - not committed)
- Installed component: `website/components/blog27.tsx`

**Important**: Pro blocks have image slots which are crucial for the blog design. The current custom components are placeholders without proper image support.

#### Clerk Authentication with shadcn Theming
- **Package**: `@clerk/nextjs`, `@clerk/themes`
- **Installation**: `pnpm add @clerk/nextjs @clerk/themes`
- **Description**: Authentication with shadcn/ui theme integration
- **Setup**:
  1. Install packages: `pnpm add @clerk/nextjs @clerk/themes`
  2. Import shadcn CSS in `globals.css`: `@import "@clerk/themes/shadcn.css";`
  3. Import theme in layout: `import { shadcn } from "@clerk/themes"`
  4. Apply to ClerkProvider: `<ClerkProvider appearance={{ baseTheme: shadcn }}>`
  5. Create middleware.ts with `clerkMiddleware()`
  6. Integrate auth components in navbar (SignInButton, SignUpButton, UserButton)
- **Features**:
  - Automatic light/dark mode sync with shadcn theme
  - Matches Clean Slate theme colors (purple/blue accents)
  - Uses shadcn CSS variables for consistent styling
  - No manual CSS customization needed
- **Official Docs**: https://clerk.com/docs/customization/themes
- **Category**: Authentication, Styling & UI

#### Markdown Processing
- **Libraries**:
  - `react-markdown`: Core markdown rendering
  - `remark-gfm`: GitHub Flavored Markdown (tables, task lists, strikethrough, etc.)
  - `@tailwindcss/typography`: Beautiful prose styling
  - `react-syntax-highlighter`: High-quality code block syntax highlighting
- **Implementation**:
  - Wrap rendered content in `<div className="prose">...</div>`
  - Automatic styling for headings, spacing, tables, lists
  - Extend react-markdown with react-syntax-highlighter for code blocks
  - Important for displaying lots of code examples
- **Category**: Markdown/MDX Processing, Tools & Libraries

---

## Categories

### Architecture & Design
<!-- Resources about Next.js architecture decisions -->

- **Page Layouts**: shadcnblocks components
  - **Navigation bar** (navbar8): https://www.shadcnblocks.com/block/navbar8
    - Base navbar structure
    - **Note**: Will replace auth buttons with Clerk components (SignInButton, SignOutButton, UserButton)
  - **Footer** (footer16): https://www.shadcnblocks.com/block/footer16
    - Footer layout for all pages
  - **Main listing page** (blog27): https://www.shadcnblocks.com/block/blog27
    - Grid/list layout for blog post listing
  - **Individual post page** (blogpost5): https://www.shadcnblocks.com/block/blogpost5
    - Single post layout with content area
  - All integrated with shadcn/ui components

### Markdown/MDX Processing
<!-- Resources about handling markdown content in Next.js -->

- **react-markdown**: Core markdown rendering library
  - Install: `pnpm add react-markdown remark-gfm`
  - Supports GitHub Flavored Markdown via `remark-gfm` plugin
  - Features: tables, task lists, strikethrough, autolinks
  - Extensible with custom components

- **react-syntax-highlighter**: Code block syntax highlighting
  - Install: `pnpm add react-syntax-highlighter`
  - Extends react-markdown for high-quality code blocks
  - Essential for blog displaying lots of code examples
  - Supports multiple themes and languages
  - Usage: Pass as custom `code` component to react-markdown

- **@tailwindcss/typography**: Prose styling plugin
  - Install: `pnpm add -D @tailwindcss/typography`
  - Enable in `tailwind.config.js`: `plugins: [require('@tailwindcss/typography')]`
  - Usage: Wrap content in `<div className="prose">...</div>`
  - Auto-styles: headings, paragraphs, lists, tables, code blocks, spacing
  - No manual CSS needed for markdown content

### Styling & UI
<!-- Resources about styling approaches -->

- **shadcn/ui**: Component library built on Radix UI and Tailwind CSS
  - Setup: `pnpm dlx shadcn@latest init`
  - Copy-paste components (not npm packages)
  - Full customization control

- **tweakcn Theme Generator**: https://tweakcn.com/editor/theme?theme=clean-slate
  - Selected theme: **Clean Slate**
  - Visual theme editor for shadcn/ui
  - Generates custom color schemes and CSS variables

- **shadcnblocks**: Pre-built layouts
  - Navbar (navbar8): https://www.shadcnblocks.com/block/navbar8
    - Navigation bar (will use Clerk auth components)
  - Footer (footer16): https://www.shadcnblocks.com/block/footer16
    - Footer layout
  - Blog listing (blog27): https://www.shadcnblocks.com/block/blog27
    - For main blog page with post grid/list
  - Blog post (blogpost5): https://www.shadcnblocks.com/block/blogpost5
    - For individual blog post pages
  - Copy-paste ready components

### Build & Deployment
<!-- Resources about building and deploying Next.js apps -->

- **Hosting Platform**: Vercel (official Next.js hosting)
  - Zero-config deployment for Next.js
  - Automatic HTTPS/SSL
  - Global CDN by default
  - Edge functions support
  - Preview deployments for branches
  - Excellent Next.js 15 support

### Migration Strategy
<!-- Resources about migration approaches and best practices -->

### Tools & Libraries
<!-- Specific tools and libraries to consider -->

- **shadcn/ui**: Modern component library for React/Next.js
  - Built on Radix UI primitives + Tailwind CSS
  - Components you own (copy-paste, not dependencies)
  - Accessible by default
  - Init command: `pnpm dlx shadcn@latest init`

- **Clerk**: Authentication and user management (for future features)
  - Components: SignInButton, SignOutButton, UserButton
  - Integrated with navbar8 from shadcnblocks
  - Handles signin/signout flows
  - **Theming**: Uses shadcn theme via `@clerk/themes` package
    - Import `shadcn` theme from `@clerk/themes`
    - Import `@clerk/themes/shadcn.css` in `globals.css`
    - Apply `baseTheme: shadcn` to `<ClerkProvider>` appearance prop
    - Automatically adapts to light/dark mode from shadcn/ui configuration
  - **Note**: Auth is included in navbar but NOT required for any features initially
  - **Purpose**: Enables future comments system or subscription features
  - Login UI will be present but no gated content

- **react-markdown**: Markdown to HTML rendering
  - Install: `pnpm add react-markdown remark-gfm`
  - Supports GitHub Flavored Markdown (tables, task lists, strikethrough)
  - Extensible with custom components

- **react-syntax-highlighter**: Syntax highlighting for code blocks
  - Install: `pnpm add react-syntax-highlighter`
  - Extends react-markdown for high-quality code display
  - Critical for technical blog with lots of code examples

- **@tailwindcss/typography**: Prose styling for markdown
  - Install: `pnpm add -D @tailwindcss/typography`
  - Usage: `<div className="prose">...</div>`
  - Automatic beautiful styling for all markdown elements

---

## Migration Checklist

### Phase 1: Project Setup ✅ COMPLETE
- [x] Initialize Next.js 15 project with TypeScript (in `website/` subdirectory)
- [x] Configure Tailwind CSS v4 + @tailwindcss/typography
- [x] Set up shadcn/ui with Clean Slate theme (Neutral base color)
- [x] Install shadcn/ui components (button, card, badge, separator, dropdown-menu, etc.)
- [x] **Install shadcnblocks Pro components** (blog27, blogpost5, navbar8, footer16)
- [x] **Replace navbar with navbar8 Pro block** - Includes theme toggle, responsive mobile menu
- [x] **Replace footer with footer16 Pro block** - Includes accordion on mobile, social links
- [x] Create root layout with navbar and footer
- [x] **Add light/dark theme toggle** (next-themes integration)
- [x] **Install Clerk authentication** (@clerk/nextjs, @clerk/themes)
- [x] **Configure Clerk with shadcn theming** - Import shadcn theme, apply to ClerkProvider
- [x] Create homepage with hero section
- [x] **Update blog listing page (`/blog`) to use blog27 Pro component**
- [x] **Wire up blog27 with actual categories from spec** (7 categories aligned with /create-post)
- [x] Create category filter page (`/blog/category/[category]`)
- [x] Create individual blog post page (`/blog/[slug]`)
- [x] Fix container layout issues
- [x] **Test build - all pages compile successfully with Pro components**
- [x] Install markdown dependencies (react-markdown, remark-gfm, react-syntax-highlighter, gray-matter)
- [x] Configure next.config.mjs with Turbopack

### Phase 2: Content Migration ✅ COMPLETE
- [x] Analyze existing posts and assign categories (from 7 hardcoded options)
- [x] Convert existing posts from `posts/YYYY-MM-DD-slug/post.md` → `content/posts/YYYY-MM-DD-slug.mdx`
  - [x] 2025-10-12-voice-to-blog-automation.mdx
  - [x] 2025-10-13-taming-claude-yolo-mode.mdx
- [x] Add `category` field to each post's frontmatter (validate against hardcoded list)
- [x] Rename `tags` field to `hashtags` in frontmatter
- [x] Update frontmatter (remove `blogger_id`, `updated`, `images`, `status` fields)
- [x] Move images from `posts/*/` → `public/blog/[slug]/`
  - [x] 2025-10-12 images (hero + diagram)
  - [x] 2025-10-13 images (hero + diagram)
- [x] Convert images to WebP format (already in WebP)
- [x] Update image references to use relative paths (`./image.webp`)

### Phase 3: Core Implementation ✅ COMPLETE
- [x] Implement `lib/posts.ts` (post loading/parsing with date filtering)
  - [x] getAllPosts(), getPublishedPosts(), getPostBySlug(), getAllPostSlugs()
- [x] Implement `lib/categories.ts` (hardcoded categories + validation)
  - [x] CATEGORIES const, getCategoryById(), getPostsByCategory(), getCategoryCounts()
- [x] ~~Implement `lib/remark-image-path.ts` (image path rewriting)~~ - Handled inline in blog post page component
- [x] ~~Create `mdx-components.tsx` (next/image wrapper)~~ - Custom img component in blog post page
- [x] Build `app/page.tsx` (homepage)
- [x] Build `app/blog/page.tsx` (blog listing with category filter tabs)
- [x] Build `app/blog/category/[category]/page.tsx` (category filter page)
- [x] Build `app/blog/[slug]/page.tsx` (dynamic post page with category/hashtags)
  - [x] generateStaticParams() for SSG
  - [x] generateMetadata() for SEO
  - [x] Custom img component (relative path → next/image)
  - [x] Custom code component (react-syntax-highlighter with oneDark theme)
  - [x] Custom inline code styling (matches oneDark theme)
- [ ] Build `app/sitemap.ts` (sitemap generation including category pages)
- [x] Implement root layout with navbar/footer
- [ ] Add ISR revalidation (1 hour) to blog pages

### Phase 4: UI Components ✅ COMPLETE
- [x] ~~Create `components/category-filter.tsx`~~ - Category tabs integrated in blog27 component
- [x] ~~Create `components/hashtag-badge.tsx`~~ - Using shadcn/ui Badge component directly
- [x] Integrate shadcnblocks navbar8 (with Clerk auth placeholders for future use)
- [x] Integrate shadcnblocks footer16
- [x] Integrate shadcnblocks blog27 (blog listing layout with category filters)
- [x] ~~Integrate shadcnblocks blogpost5~~ - Using custom layout in app/blog/[slug]/page.tsx
- [x] Style code blocks with react-syntax-highlighter (theme-aware)
- [x] Typography styling using @tailwindcss/typography plugin (maintainable defaults)
  - [x] Inline code - custom styling matching syntax highlighter, theme-aware (light/dark modes)
    - Light mode: `#f5f5f5` background, `#383a42` text (subtle oneDark-inspired)
    - Dark mode: `#282c34` background, `#abb2bf` text (true oneDark colors)
  - [x] Multi-line code blocks - Theme-aware SyntaxHighlighter via CodeBlock component
    - Light mode: oneLight theme
    - Dark mode: oneDark theme
    - Client component with useTheme hook for automatic switching
  - [x] All markdown elements - handled by typography plugin with minimal theme overrides
  - [x] Custom H2 styling - bottom border for visual hierarchy

### Phase 5: SEO & Polish ⚠️ IN PROGRESS (20%)
- [x] Implement `generateMetadata()` for dynamic SEO (blog posts)
  - [x] Title, description, Open Graph metadata
  - [x] Published time for articles
- [ ] Add `generateMetadata()` for category pages
- [ ] Add JSON-LD structured data (BlogPosting schema)
- [ ] Build `app/sitemap.ts` (sitemap generation including category pages)
- [ ] Test sitemap generation (verify all routes included)
- [x] Verify image optimization (next/image working with WebP, responsive, lazy loading)
- [x] Test all internal links (category links, post links working)
- [ ] Add RSS feed (`app/rss.xml/route.ts`)
- [x] Implement scheduled post filtering (future dates hidden via getPublishedPosts())
- [ ] Add ISR revalidation (1 hour) to blog pages
- [ ] Test ISR revalidation works correctly

### Phase 6: Deployment
- [ ] Create Vercel project
- [ ] **Configure root directory**: Set to `website/` in Vercel project settings (since Next.js app is in subdirectory)
- [ ] Configure domain (the-agentic-engineer.com)
- [ ] Set up environment variables (if needed)
- [ ] Deploy to production
- [ ] Verify SEO (Google Search Console)

---

## Notes & Ideas

### Project Structure Note
- **Next.js app location**: `website/` subdirectory
- **Reason**: Separates Next.js site from Python blog automation tools to avoid conflicts
- **Critical**: All Next.js development happens in `website/` subdirectory - this isolation prevents interference with existing Python tooling layer (lib/, tools/, posts/)
- **Vercel deployment**: Must configure root directory to `website/` in Vercel project settings
- **Git structure**:
  ```
  the-agentic-engineer/          # Git repo root
  ├── lib/                       # Python modules
  ├── tools/                     # Publishing scripts
  ├── posts/                     # Source posts (to be migrated)
  ├── specs/                     # Documentation
  └── website/                   # Next.js app (deployed to Vercel)
      ├── app/
      ├── components/
      ├── content/               # MDX posts
      └── public/                # Static assets
  ```

### Branding Consistency
- Use "The Agentic Engineer" across all UI components
- Domain: the-agentic-engineer.com
- Apply to: navbar, footer, page titles, meta tags, etc.

### Future Enhancements (Post-Launch)
- [ ] Archive pages by date (`/blog/2025/10`)
- [ ] Search functionality (client-side fuzzy search or Algolia)
- [ ] Reading time calculation (display on post cards)
- [ ] Table of contents generation (for long posts)
- [ ] Related posts suggestions (based on tags/categories)
- [ ] Comment system (Giscus or similar, gated by Clerk auth)
- [ ] Newsletter subscriptions (email capture, gated by Clerk auth)
- [ ] Post reactions/likes (gated by Clerk auth)
- [x] Dark mode toggle (already implemented with next-themes)
- [ ] Social share buttons

---

## Overall Project Status

### **Progress: ~75% Complete**

**✅ Phases Complete:**
- **Phase 1**: Project Setup (100%)
- **Phase 2**: Content Migration (100%)
- **Phase 3**: Core Implementation (100%)
- **Phase 4**: UI Components (100%)

**⚠️ Phases In Progress:**
- **Phase 5**: SEO & Polish (20%)
  - Missing: Sitemap, RSS feed, JSON-LD, ISR configuration
- **Phase 6**: Deployment (0%)
  - Not started

### **What's Working Right Now:**

✅ **Full-featured blog with 2 posts**
- Homepage with hero section
- Blog listing page with category filter tabs
- Category filter pages (`/blog/category/[category]`)
- Individual post pages with sidebar
- Theme toggle (light/dark mode)

✅ **Theme-aware code styling**
- Inline code adapts to theme (light/dark)
- Multi-line code blocks use oneLight/oneDark themes
- All typography elements styled via @tailwindcss/typography

✅ **Content infrastructure**
- MDX posts with frontmatter
- Image optimization via next/image
- Category system (7 hardcoded categories)
- Hashtag display badges
- Future date filtering (scheduled posts)

✅ **Pro components integrated**
- navbar8 (with theme toggle)
- footer16 (with mobile accordion)
- blog27 (blog listing layout)
- All styled with Clean Slate theme

### **Critical Path to Launch:**

**Priority 1 - SEO (Required for launch):**
1. Build `app/sitemap.ts` - Generate XML sitemap
2. Add JSON-LD structured data to blog posts
3. Add `generateMetadata()` to category pages
4. Configure ISR revalidation (1 hour) on blog pages

**Priority 2 - Deployment:**
1. Create Vercel project
2. Configure root directory to `website/`
3. Deploy to production
4. Configure domain (the-agentic-engineer.com)

**Priority 3 - Optional (Post-launch):**
1. RSS feed
2. Enhanced metadata
3. Performance optimizations

### **Key Implementation Details:**

**Components:**
- `components/code-block.tsx` - Theme-aware syntax highlighting
- `lib/posts.ts` - Post loading with date filtering
- `lib/categories.ts` - Category management and validation
- `app/blog/[slug]/page.tsx` - Dynamic post rendering

**Styling Approach:**
- Minimal custom CSS (~50 lines of prose overrides)
- @tailwindcss/typography handles most styling
- Theme integration via CSS variables
- Custom code styling adapts to light/dark themes

**Tech Stack:**
- Next.js 15 (App Router) with Turbopack
- Tailwind CSS v4 + @tailwindcss/typography
- shadcn/ui (Clean Slate theme)
- react-markdown + remark-gfm
- react-syntax-highlighter (oneLight/oneDark)
- Clerk authentication (configured but optional)

**Ready for production deployment once sitemap and metadata are complete!**

