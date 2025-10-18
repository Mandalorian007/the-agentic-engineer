# Agentic SaaS Starter Kit - Product Spec

**Version:** 1.0.0
**Status:** Concept
**Last Updated:** October 17, 2025

---

## Overview

Production-ready Next.js SaaS template with AI-powered development workflow. Ship your first feature in 60 minutes.

**Unique Value:** The only starter kit with built-in AI development commands via Claude Code + MCP.

---

## Tech Stack

| Component | Technology | Why |
|-----------|------------|-----|
| **Framework** | Next.js 15 (App Router) | Industry standard |
| **Database** | Convex | Real-time TypeScript backend, zero config |
| **Auth** | Clerk | Auth + subscriptions + `.has()` permissions |
| **UI** | shadcn/ui | Copy-paste components |
| **Styling** | Tailwind v4 + tweakcn | 30-second theme customization |
| **Deploy** | Vercel | Zero-config hosting |
| **AI Tooling** | Claude Code + MCP | Built-in development workflow |

---

## Project Structure

```
agentic-saas-starter/
├── .claude/
│   ├── commands/
│   │   ├── prime.md            # Load context
│   │   ├── plan.md             # Plan features
│   │   ├── build.md            # Build features
│   │   ├── test.md             # Generate tests
│   │   ├── review.md           # Code review
│   │   └── document.md         # Update docs
│   └── settings.json
│
├── app/
│   ├── (marketing)/
│   │   ├── page.tsx            # Homepage
│   │   ├── pricing/page.tsx    # Pricing page
│   │   └── blog/
│   │       ├── page.tsx        # Blog listing
│   │       └── [slug]/page.tsx # Blog post (MDX)
│   ├── (dashboard)/
│   │   └── page.tsx            # Dashboard (protected)
│   ├── layout.tsx
│   └── globals.css
│
├── convex/
│   ├── schema.ts               # TODO: App-specific schemas
│   └── [feature].ts            # Queries/mutations
│
├── components/
│   ├── ui/                     # shadcn/ui (30+ components)
│   ├── marketing/              # Landing components
│   └── dashboard/              # Dashboard components
│
├── content/
│   └── blog/                   # MDX blog posts
│       └── hello-world.mdx
│
├── lib/
│   ├── convex.ts
│   ├── mdx.ts                  # MDX renderer
│   └── utils.ts
│
└── docs/
    ├── README.md
    ├── ARCHITECTURE.md
    └── CUSTOMIZATION.md
```

---

## Core Features

### 1. Authentication (Clerk - No Webhooks Needed)

```typescript
// middleware.ts - Protect routes
import { authMiddleware } from "@clerk/nextjs";

export default authMiddleware({
  publicRoutes: ["/", "/pricing", "/blog(.*)"],
});

// app/(dashboard)/page.tsx - Dashboard
import { auth } from "@clerk/nextjs";

export default function Dashboard() {
  const { userId, has } = auth();

  const isPro = has({ permission: "org:feature:pro" });

  return (
    <div>
      <h1>Dashboard</h1>
      {isPro && <ProFeatures />}
    </div>
  );
}
```

**Key:** Clerk handles everything - no DB tables for users/subscriptions needed.

---

### 2. Feature Gating (Clerk `.has()` API)

```typescript
// Simple permission checks
const { userId, has } = auth();

// Check permissions
const canAccessPro = has({ permission: "org:feature:pro" });
const canAccessTeam = has({ permission: "org:feature:team" });

// Use in components
{canAccessPro && <AdvancedAnalytics />}

// Use in API routes
if (!has({ permission: "org:feature:pro" })) {
  return new Response("Upgrade required", { status: 403 });
}
```

---

### 3. Blog with MDX

```typescript
// content/blog/hello-world.mdx
---
title: "Hello World"
description: "Getting started with our platform"
date: "2025-10-17"
---

# Hello World

This is a blog post written in **MDX**.

import { Button } from "@/components/ui/button";

<Button>Click Me</Button>

// lib/mdx.ts - Simple MDX renderer
import { compileMDX } from 'next-mdx-remote/rsc';
import fs from 'fs';
import path from 'path';

export async function getBlogPost(slug: string) {
  const filePath = path.join('content/blog', `${slug}.mdx`);
  const source = fs.readFileSync(filePath, 'utf8');

  const { content, frontmatter } = await compileMDX({
    source,
    options: { parseFrontmatter: true }
  });

  return { content, frontmatter };
}
```

---

### 4. Rapid Theme Customization (tweakcn)

**30-second theme change:**

```bash
# 1. Visit https://tweakcn.com/editor/theme
# 2. Customize colors/radius
# 3. Export theme.json
# 4. Apply it:
pnpm dlx shadcn@latest add ./theme.json
```

**CSS variables in `globals.css`:**
```css
@layer base {
  :root {
    --background: 0 0% 100%;
    --foreground: 222.2 84% 4.9%;
    --primary: 221.2 83.2% 53.3%;
    /* Change these = instant rebrand */
  }
}
```

**Marketability:** "Rebrand the entire app in 30 seconds with tweakcn"

---

## AI Development Workflow

### Command: `/prime`

Load project context - reads structure, docs, key files.

### Command: `/plan`

```
/plan Add user profile feature with avatar upload

→ Generates detailed spec:
  - Convex schema changes
  - Next.js pages needed
  - shadcn components to use
  - Permission requirements
  - Implementation steps
```

### Command: `/build`

```
/build [feature from plan]

→ Implements:
  - Creates Convex mutations/queries
  - Generates Next.js pages
  - Adds shadcn UI components
  - Wires up auth checks
```

### Command: `/test`

```
/test components/profile/avatar-upload.tsx

→ Generates:
  - Unit tests (Vitest)
  - Component tests (React Testing Library)
  - Integration tests
```

### Command: `/review`

```
/review convex/items.ts

→ Checks:
  - Security (auth, permissions)
  - TypeScript types
  - Convex best practices
  - Performance issues
```

### Command: `/document`

```
/document

→ Updates:
  - API.md (Convex functions)
  - FEATURES.md
  - ARCHITECTURE.md
```

---

## MCP Integration

### Convex MCP
- Test queries/mutations directly
- Validate schemas
- Check auth flows

### shadcn MCP
- Browse available components
- Generate usage examples
- Plan UI layouts

**Marketability:** "AI that knows your database AND your UI components"

---

## Pre-Built Pages

### 1. Homepage (`app/page.tsx`)
- Hero section with CTA
- Features grid
- Pricing teaser
- Social proof section

### 2. Pricing Page (`app/pricing/page.tsx`)
- 3 tiers (Free, Pro, Team)
- Feature comparison table
- Clerk subscription integration
- FAQs

### 3. Blog (`app/blog/`)
- Listing page with all posts
- Individual post pages (MDX)
- Syntax highlighting
- Reading time
- Share buttons

### 4. Dashboard (`app/(dashboard)/page.tsx`)
- Protected by Clerk middleware
- Sidebar navigation
- Stats/metrics cards
- Permission-gated features

---

## What's Included

**Code:**
- Next.js 15 app (4 core pages ready)
- Clerk auth with `.has()` permissions (no DB needed)
- Convex backend (ready for your schemas)
- shadcn/ui (30+ components installed)
- MDX blog system
- Tailwind v4 + tweakcn integration

**AI Workflow:**
- 6 Claude Code commands
- Convex MCP integration
- shadcn MCP integration
- Pre-configured for your stack

**DX Features:**
- Zod schema driven Convex backend (unified types everywhere)
- 30-second theme customization (tweakcn)
- Clean Clerk `.has()` API for permissions
- Type-safe Convex queries
- MDX with syntax highlighting

**Documentation:**
- Quick start (5 min to first run)
- Architecture guide
- Customization guide (tweakcn)
- AI commands reference

**Distribution:**
- Private GitHub repository
- Video walkthrough (15 min)
- 6 months updates

---

## Marketing Angles

### 1. "The AI-First SaaS Starter"
Build features 10x faster with built-in Claude Code commands. No other starter has this.

### 2. "30-Second Rebrand"
Show tweakcn demo - complete visual rebrand in 30 seconds. Instant differentiation.

### 3. "No Boilerplate Database Code"
Clerk handles users/subscriptions. Your Convex DB is for YOUR features, not auth tables.

### 4. "Modern Stack, Zero Config"
Next.js 15 + Convex + Clerk. Deploy-ready in 5 minutes.

### 5. "Zod-Driven Type Safety"
Define your schemas once in Zod. Get full type safety from DB to UI automatically.

### 6. "Build in Public" Feature
Pre-built blog system. Show off your progress while building your product.

---

## Distribution

**GitHub Repository:**
- Private repo access after purchase
- Updates via `git pull`
- Issues for support

**Video Walkthrough (15 min):**
1. Setup demo (5 min) - Clone to deployed in 5 minutes
2. AI workflow demo (5 min) - Build a feature with `/plan` → `/build`
3. Customization demo (5 min) - tweakcn rebrand + add blog post

**Format:** Loom or YouTube (unlisted)

---

## Pricing

- **Regular:** $149
- **Launch:** $99 (first 100)
- **Early Bird:** $79 (first 20)

**Value Prop:** Save 30-40 hours of setup = $1,500-$6,000 value for $149.

---

**Document Version:** 1.0
**Last Updated:** October 17, 2025
**Status:** Ready to Build
