# Claude Context for The Agentic Engineer Website

## ⚠️ CRITICAL: Development Workflow

**ALWAYS use `pnpm lint` instead of `pnpm build` during development.**

- ✅ `pnpm lint` - Checks ESLint + TypeScript without breaking the dev server
- ❌ `pnpm build` - Breaks the running `pnpm dev` server (Next.js limitation)

**Why:** Both `pnpm dev` and `pnpm build` use the same `.next` directory. Running build while dev is active causes conflicts and requires manual restart. There is no workaround.

**Lint catches:**
- ESLint errors and warnings
- TypeScript type errors
- All issues that would fail the build

**Only run `pnpm build`:**
- When dev server is stopped
- Before deploying to production
- To verify final build output

---

## Directory Structure

```
the-agentic-engineer/
├── website/                      # Next.js blog (this subdirectory)
│   ├── app/                      # Next.js 15 App Router
│   │   ├── page.tsx              # Homepage
│   │   ├── blog/                 # Blog pages (/blog, /blog/[slug])
│   │   ├── layout.tsx            # Root layout
│   │   └── globals.css           # Tailwind v4 + typography styles
│   ├── components/               # shadcn/ui + Pro blocks (navbar8, footer16, blog27)
│   ├── content/posts/            # MDX blog posts
│   ├── lib/                      # Post loading, categories
│   └── public/blog/              # Post images (Vercel CDN)
│
├── tools/                        # Python scripts (build.py, publish.py, seo_check.py, etc.)
├── lib/                          # Python modules (blogger_client, cloudinary_uploader, etc.)
├── specs/                        # Documentation (nextjs-migration-resources.md, etc.)
├── .claude/
│   ├── commands/                 # Slash commands (/create-post, /build, /publish, etc.)
│   ├── hooks/                    # Safety hooks (pre_tool_use.py)
│   └── settings.json             # Claude Code configuration
└── posts/                        # Source markdown (being migrated to website/content/posts/)
```

---

## Tech Stack

- **Framework**: Next.js 15 (App Router) with Turbopack
- **Styling**: Tailwind CSS v4 + @tailwindcss/typography
- **Components**: shadcn/ui (Clean Slate theme)
- **Markdown**: react-markdown + remark-gfm
- **Code Highlighting**: react-syntax-highlighter (oneDark theme)
- **Auth**: Clerk (configured but not required for features)
- **Hosting**: Vercel (deploy from `website/` subdirectory)

---

## Key Implementation Details

**Markdown Styling:**
- Uses `prose` classes from @tailwindcss/typography
- Custom prose styles in `globals.css` for complete control
- Inline code: `relative rounded border px-[0.3rem] py-[0.2rem] font-mono text-sm bg-muted`
- Multi-line code: SyntaxHighlighter with oneDark theme

**Categories:**
- 7 hardcoded categories in `lib/categories.ts`
- Aligned with `/create-post` command formats
- Filter pages: `/blog/category/[category]`

**Images:**
- Stored in `public/blog/[slug]/`
- Referenced in MDX as `./image.webp`
- Custom img component converts to `next/image`
- Auto-optimization by Next.js + Vercel CDN
