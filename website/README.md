# The Agentic Engineer - Next.js Website

Next.js 15 website for The Agentic Engineer blog, built with TypeScript, Tailwind CSS, and shadcn/ui.

## 🎨 Design

- **Theme**: Clean Slate (from [tweakcn.com](https://tweakcn.com/editor/theme?theme=clean-slate))
- **Base Color**: Neutral
- **Style**: New York (shadcn/ui)
- **Theme documentation**: See `app/globals.css` header comment

## 📁 Project Structure

```
website/
├── app/
│   ├── layout.tsx              # Root layout with navbar and footer
│   ├── page.tsx                # Homepage
│   ├── blog/
│   │   ├── page.tsx            # Blog listing (all posts)
│   │   ├── [slug]/
│   │   │   └── page.tsx        # Individual blog post
│   │   └── category/
│   │       └── [category]/
│   │           └── page.tsx    # Category filtered posts
│   └── globals.css             # Global styles + theme variables
├── components/
│   ├── navbar.tsx              # Navigation with auth placeholders
│   ├── footer.tsx              # Footer with links
│   └── ui/                     # shadcn/ui components
│       ├── button.tsx
│       ├── card.tsx
│       ├── badge.tsx
│       └── separator.tsx
└── lib/
    └── utils.ts                # shadcn/ui utilities
```

## 🚀 Current Status

### ✅ Phase 1: Basic Scaffolding (COMPLETE)

- [x] Next.js 15 + TypeScript setup
- [x] Tailwind CSS v4 configuration
- [x] shadcn/ui with Clean Slate theme
- [x] Navbar component (with auth placeholders for future Clerk integration)
- [x] Footer component
- [x] Root layout with navbar/footer
- [x] Homepage with hero section
- [x] Blog listing page with placeholder posts
- [x] Category filter pages (7 hardcoded categories)
- [x] Individual blog post pages
- [x] Build test - all pages compile successfully

### 🔄 Phase 2: Content Integration (TODO)

- [ ] Install markdown processing libraries
- [ ] Configure MDX support
- [ ] Implement content loading utilities
- [ ] Wire up real content to pages

## 🔧 Development

```bash
# Install dependencies
pnpm install

# Run development server
pnpm dev

# Build for production
pnpm build
```

Visit [http://localhost:3000](http://localhost:3000) to view the site.

## 📝 Routes

| Route                          | Description                      |
| ------------------------------ | -------------------------------- |
| `/`                            | Homepage                         |
| `/blog`                        | Blog listing (all posts)         |
| `/blog/[slug]`                 | Individual blog post             |
| `/blog/category/[category]`    | Posts filtered by category       |

## 🎨 Categories

The blog uses 7 hardcoded categories:

1. **Tutorials & How-Tos** (`tutorials`)
2. **Case Studies** (`case-studies`)
3. **Guides & Fundamentals** (`guides`)
4. **Lists & Tips** (`lists`)
5. **Comparisons & Reviews** (`comparisons`)
6. **Problem & Solution** (`problem-solution`)
7. **Opinions & Analysis** (`opinions`)

## 🔐 Authentication

Authentication UI is present but not functional yet. Placeholders exist for future [Clerk](https://clerk.com) integration. See `components/navbar.tsx` for TODO comments.

## 🚢 Deployment

Deploy to **Vercel** with these settings:
- **Root Directory**: `website/` (since Next.js app is in subdirectory)
- **Build Command**: `pnpm build`
- **Output Directory**: `.next`

## 📚 Resources

- [Next.js Documentation](https://nextjs.org/docs)
- [shadcn/ui Documentation](https://ui.shadcn.com)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [tweakcn Theme Editor](https://tweakcn.com/editor/theme?theme=clean-slate)
