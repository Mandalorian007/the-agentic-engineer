# Next.js Migration Resources

This document collects resources and information for migrating the Agentic Engineer Blog to Next.js.

## Overview

Planning migration from current Markdown + Blogger setup to a Next.js-based blog platform.

**Branding & Domain:**
- **Blog Name**: The Agentic Engineer
- **Domain**: the-agentic-engineer.com
- All branding should use "The Agentic Engineer" naming

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
- **Category**: Styling & UI

#### shadcnblocks - Blog Listing Layout
- **URL**: https://www.shadcnblocks.com/block/blog27
- **Block**: blog27
- **Description**: Pre-built blog page layout for main blog listing
- **Category**: Styling & UI, Architecture & Design

#### shadcnblocks - Blog Post Layout
- **URL**: https://www.shadcnblocks.com/block/blogpost5
- **Block**: blogpost5
- **Description**: Pre-built individual blog post layout
- **Category**: Styling & UI, Architecture & Design

#### shadcnblocks - Navbar
- **URL**: https://www.shadcnblocks.com/block/navbar8
- **Block**: navbar8
- **Description**: Navigation bar layout
- **Note**: Will integrate Clerk signin/signout components for authentication
- **Category**: Styling & UI, Architecture & Design

#### shadcnblocks - Footer
- **URL**: https://www.shadcnblocks.com/block/footer16
- **Block**: footer16
- **Description**: Footer layout
- **Category**: Styling & UI, Architecture & Design

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

### Migration Strategy
<!-- Resources about migration approaches and best practices -->

### Tools & Libraries
<!-- Specific tools and libraries to consider -->

- **shadcn/ui**: Modern component library for React/Next.js
  - Built on Radix UI primitives + Tailwind CSS
  - Components you own (copy-paste, not dependencies)
  - Accessible by default
  - Init command: `pnpm dlx shadcn@latest init`

- **Clerk**: Authentication and user management
  - Components: SignInButton, SignOutButton, UserButton
  - Will integrate with navbar8 from shadcnblocks
  - Handles signin/signout flows

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

## Notes & Ideas

### Branding Consistency
- Use "The Agentic Engineer" across all UI components
- Domain: the-agentic-engineer.com
- Apply to: navbar, footer, page titles, meta tags, etc.

---

## Action Items

- [ ] Review collected resources
- [ ] Decide on architecture approach
- [ ] Create detailed migration plan

