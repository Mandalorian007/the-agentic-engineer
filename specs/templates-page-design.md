# Templates Page - Design Specification

**Version:** 1.0.0
**Status:** Draft for Review
**Last Updated:** October 17, 2025
**Route:** `/templates`

---

## Overview

A dedicated marketing page for showcasing production-ready starter templates. Initially featuring a single template (Agentic SaaS Starter Kit) with front-and-center positioning. Designed to scale to multiple templates in the future.

---

## Design Philosophy

**Current State (1 Template):**
- Full-page marketing treatment for the single template
- Combined landing page + product detail page
- Heavy emphasis on features, tech stack, and AI workflow
- Primary goal: Convert visitors to purchasers

**Future State (Multiple Templates):**
- Gallery/grid view of available templates
- Individual landing pages per template (`/templates/[slug]`)
- Main `/templates` page becomes a discovery hub
- Category filtering as templates grow

---

## Visual Mockups

### Full Page Layout

```
═══════════════════════════════════════════════════════════════
                        TEMPLATES
        Production-Ready Starters, Turbo Charged with AI

     Ship 10x faster with battle-tested code and AI workflows
          that feel like magic but run on solid tools
═══════════════════════════════════════════════════════════════
```

### Featured Template (Hero Card)
```
┌─────────────────────────────────────────────────────────────┐
│  🚀 AVAILABLE NOW                                            │
│                                                              │
│  ┌──────────────┐                                           │
│  │   [Image]    │  AGENTIC SAAS STARTER KIT               │
│  │  Screenshot  │                                           │
│  │  of starter  │  Ship your SaaS in hours, not weeks.     │
│  │   template   │  Turbo charged with Claude Code commands  │
│  │              │  for AI-assisted development.             │
│  └──────────────┘                                           │
│                                                              │
│  ⚡ One clean, production-ready codebase                   │
│  🤖 6 AI slash commands (/prime, /plan, /build...)         │
│  🎨 30-second theme rebrand with tweakcn                   │
│  📦 Pre-built: Auth, Dashboard, Pricing, Blog              │
│                                                              │
│  $149  $99 Launch Price (First 100)                        │
│                                                              │
│  [View Details →]  [Buy Now - $99]                         │
└─────────────────────────────────────────────────────────────┘
```

### Powered By Section
```
═══════════════════════════════════════════════════════════════
               ONE CLEAN CODEBASE, POWERED BY:

  [Next.js 15]  •  [Convex]  •  [Clerk]  •  [shadcn/ui]  •
         [Tailwind v4]  •  [Claude Code]  •  [Vercel]

         Modern tools working together, seamlessly
═══════════════════════════════════════════════════════════════
```

### Why This Template (3 Columns)
```
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│  🤖 AI-Assisted │  │  🏗️ Battle-     │  │  🎨 Your Brand  │
│                 │  │     Tested      │  │                 │
│  Claude Code    │  │  Production-    │  │  Ship with your │
│  commands guide │  │  ready patterns │  │  brand colors   │
│  you through    │  │  proven in real │  │  in 30 seconds  │
│  feature dev    │  │  SaaS apps      │  │  (tweakcn)      │
└─────────────────┘  └─────────────────┘  └─────────────────┘
```

### What You Get (Expandable Accordion)
```
▼ Complete Codebase
  □ Next.js 15 app with 4 core pages (Homepage, Pricing, Blog, Dashboard)
  □ Clerk authentication with permission-based feature gating
  □ Convex real-time backend (TypeScript, zero config)
  □ 30+ shadcn/ui components pre-installed
  □ MDX blog system with syntax highlighting

▼ AI Development Workflow
  □ 6 AI slash commands for guided feature development
  □ Convex MCP integration (AI knows your database)
  □ shadcn MCP integration (AI knows your UI components)
  □ Pre-configured hooks and settings for your stack
  □ Compatible with Claude Code and other AI coding agents

▼ Documentation & Walkthrough
  □ 5-minute quick start guide
  □ Architecture documentation
  □ Customization guide
  □ 15-minute video walkthrough

▼ Support & Updates
  □ Private GitHub repository access
  □ 6 months of updates included
  □ Issue-based support
  □ Community access
```

### Video Preview Section
```
┌─────────────────────────────────────────────────────────────┐
│                                                              │
│  ▶  [Video Thumbnail: "Clone to Deployed in 5 Minutes"]    │
│                                                              │
│     Watch Claude Code commands build a feature in real-time │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### More Templates Section
```
═══════════════════════════════════════════════════════════════
                    MORE TEMPLATES ON THE WAY

         We're building more production-ready starters.
              What would help you ship faster?

                    [Suggest a Template →]

              (Join the waitlist for early access)
═══════════════════════════════════════════════════════════════
```

### Final CTA Section
```
═══════════════════════════════════════════════════════════════
              Skip weeks of setup. Start shipping today.

              Get the Agentic SaaS Starter Kit now

                  [Get Started - $99] [View Docs]

          Questions? Read our FAQ or contact support
═══════════════════════════════════════════════════════════════
```

### FAQ Section (Accordion)
```
▼ What's included in the $99 price?
  Full source code, 6 months updates, video walkthrough, documentation

▼ Do I need API keys for the services?
  Yes - Convex, Clerk, and Vercel all have generous free tiers.
  Setup takes about 5 minutes total.

▼ Can I use this for client projects?
  Absolutely! One purchase, unlimited projects.

▼ What makes this "turbo charged" with AI?
  Pre-built slash commands (/prime, /plan, /build, /test, /review)
  guide you through adding features. It's like having an AI pair
  programmer who knows your entire stack.

▼ Do I need Claude Code specifically?
  The AI slash commands are designed to be portable. They work best
  with Claude Code but can be used in any AI coding agent that
  supports slash commands (Cursor, Windsurf, etc.) with minimal
  copy-paste. You can also use the template without AI tools -
  you'll just be shipping slower. 😉

▼ What if I need help?
  GitHub issues for support, comprehensive docs, video tutorials,
  and community access included.
```

---

## Page Structure

### 1. Hero Section

**Purpose:** Immediately communicate value proposition

**Content:**
- **H1:** "Templates"
- **Tagline:** "Production-Ready Starters, Turbo Charged with AI"
- **Subheading:** "Ship 10x faster with battle-tested code and AI workflows that feel like magic but run on solid tools"

**Design:**
- Full-width section with subtle gradient background
- Typography hierarchy: H1 (large), tagline (medium), subheading (body)
- Minimal decoration - let the copy do the work
- Desktop: Centered, max-width 1200px
- Mobile: Full-width, reduced font sizes

**Component:** New `TemplatesHero.tsx`

---

### 2. Featured Template Card

**Purpose:** Primary conversion point for the single available template

**Layout:**
- Large elevated card with shadow
- Left: Screenshot/hero image (40% width)
- Right: Content (60% width)
- Badge: "🚀 AVAILABLE NOW" (top-left corner)

**Content Blocks:**
- **Title:** "Agentic SaaS Starter Kit" (H2)
- **Description:** 2-3 sentence value prop
  - "Ship your SaaS in hours, not weeks."
  - "Turbo charged with AI slash commands for assisted development."
- **Key Features:** (4 checkmarks)
  - ⚡ One clean, production-ready codebase
  - 🤖 6 AI slash commands (/prime, /plan, /build...)
  - 🎨 30-second theme rebrand with tweakcn
  - 📦 Pre-built: Auth, Dashboard, Pricing, Blog
- **Pricing:**
  - Strikethrough: ~~$149~~
  - Launch price: **$99** (First 100)
- **CTAs:**
  - Primary: "Buy Now - $99" (shadcn button, primary variant)
  - Secondary: "View Details →" (button, outline variant)

**Responsive:**
- Desktop: Side-by-side layout
- Tablet: Side-by-side with reduced image size
- Mobile: Stacked (image on top, content below)

**Component:** New `FeaturedTemplateCard.tsx`

---

### 3. Powered By Section

**Purpose:** Build credibility through association with established tools

**Content:**
- **Heading:** "ONE CLEAN CODEBASE, POWERED BY:"
- **Tech Stack Badges:** (inline, centered)
  - Next.js 15
  - Convex
  - Clerk
  - shadcn/ui
  - Tailwind v4
  - Claude Code (or compatible AI agent)
  - Vercel
- **Subheading:** "Modern tools working together, seamlessly"

**Design:**
- Center-aligned
- Badges use existing `badge` component (variant: secondary)
- Light gray background section (visually separates from hero)
- Separator dots (•) between badges

**Component:** New `PoweredByStack.tsx`

---

### 4. Why This Template (3-Column Grid)

**Purpose:** Differentiate with 3 key selling points

**Columns:**

**Column 1: 🤖 AI-Assisted**
- Title: "AI-Assisted"
- Body: "AI slash commands guide you through feature development. Works with Claude Code or any compatible AI coding agent."

**Column 2: 🏗️ Battle-Tested**
- Title: "Battle-Tested"
- Body: "Production-ready patterns proven in real SaaS apps"

**Column 3: 🎨 Your Brand**
- Title: "Your Brand"
- Body: "Ship with your brand colors in 30 seconds (tweakcn)"

**Design:**
- Three equal-width columns (desktop)
- Stacked (mobile)
- Icon + title + body format
- Use existing `card` component for each column

**Component:** New `WhyThisTemplate.tsx`

---

### 5. What You Get (Expandable Accordion)

**Purpose:** Comprehensive feature list without overwhelming the page

**Sections:**

**▼ Complete Codebase**
- Next.js 15 app with 4 core pages (Homepage, Pricing, Blog, Dashboard)
- Clerk authentication with permission-based feature gating
- Convex real-time backend (TypeScript, zero config)
- 30+ shadcn/ui components pre-installed
- MDX blog system with syntax highlighting

**▼ AI Development Workflow**
- 6 AI slash commands for guided feature development
- Convex MCP integration (AI knows your database)
- shadcn MCP integration (AI knows your UI components)
- Pre-configured hooks and settings for your stack
- Compatible with Claude Code and other AI coding agents

**▼ Documentation & Walkthrough**
- 5-minute quick start guide
- Architecture documentation
- Customization guide
- 15-minute video walkthrough

**▼ Support & Updates**
- Private GitHub repository access
- 6 months of updates included
- Issue-based support
- Community access

**Design:**
- Use existing `accordion` component
- All sections collapsed by default
- Checkboxes (□) for visual scanning of items
- Max-width: 800px, centered

**Component:** New `TemplateFeatures.tsx`

---

### 6. Video Preview Section

**Purpose:** Show, don't just tell - demonstrate the AI workflow

**Content:**
- Embedded video or video thumbnail with play button
- Title: "See It In Action"
- Caption: "Watch AI slash commands build a feature in real-time"
- Video: "Clone to Deployed in 5 Minutes"

**Design:**
- 16:9 aspect ratio container
- Centered, max-width 900px
- Shadow + rounded corners
- Thumbnail until clicked (not auto-play)

**Technical:**
- Video hosted on YouTube (unlisted) or Loom
- Use `aspect-ratio` component from shadcn
- Lazy load video embed

**Component:** New `VideoPreview.tsx`

---

### 7. More Templates Section

**Purpose:** Set expectations for future offerings, invite community input

**Content:**
- **Heading:** "MORE TEMPLATES ON THE WAY"
- **Body:** "We're building more production-ready starters. What would help you ship faster?"
- **CTA:** "Suggest a Template →" (links to contact form or email)
- **Subtext:** "(Join the waitlist for early access)"

**Design:**
- Center-aligned
- Simple, clean section
- Light background (same as "Powered By" section)
- Primary button for "Suggest a Template"

**Component:** Reuse existing components, simple section

---

### 8. Final CTA Section

**Purpose:** Last chance conversion

**Content:**
- **Heading:** "Skip weeks of setup. Start shipping today."
- **Subheading:** "Get the Agentic SaaS Starter Kit now"
- **CTAs:**
  - Primary: "Get Started - $99"
  - Secondary: "View Docs"
- **Footer:** "Questions? Read our FAQ or contact support"

**Design:**
- Full-width section with gradient background
- Large, prominent buttons (desktop: side-by-side, mobile: stacked)
- High contrast for visibility

**Component:** New `TemplatesCTA.tsx`

---

### 9. FAQ Section

**Purpose:** Address common objections and questions

**Questions:**

**Q: What's included in the $99 price?**
A: Full source code, 6 months updates, video walkthrough, documentation

**Q: Do I need API keys for the services?**
A: Yes - Convex, Clerk, and Vercel all have generous free tiers. Setup takes about 5 minutes total.

**Q: Can I use this for client projects?**
A: Absolutely! One purchase, unlimited projects.

**Q: What makes this "turbo charged" with AI?**
A: Pre-built slash commands (/prime, /plan, /build, /test, /review) guide you through adding features. It's like having an AI pair programmer who knows your entire stack.

**Q: Do I need Claude Code specifically?**
A: The AI slash commands are designed to be portable. They work best with Claude Code but can be used in any AI coding agent that supports slash commands (Cursor, Windsurf, etc.) with minimal copy-paste. You can also use the template without AI tools - you'll just be shipping slower. 😉

**Q: What if I need help?**
A: GitHub issues for support, comprehensive docs, video tutorials, and community access included.

**Design:**
- Use existing `accordion` component
- Questions collapsed by default
- Max-width: 800px, centered

**Component:** New `TemplatesFAQ.tsx`

---

## Visual Design

### Color Scheme

Use existing blog theme (Clean Slate):
- **Primary accent:** For CTAs, badges, highlights
- **Background:** White (light mode), Dark gray (dark mode)
- **Card backgrounds:** Elevated with subtle shadow
- **Section backgrounds:** Alternate between white and light gray for visual separation

### Typography

- **H1:** 3xl-4xl, bold, tracking-tight
- **H2:** 2xl-3xl, semibold
- **H3:** xl-2xl, semibold
- **Body:** base, regular
- **Small:** sm, for captions and helper text

### Spacing

- **Section padding:** py-16 (desktop), py-8 (mobile)
- **Max-width:** 1200px for full-width sections, 800px for content-focused sections
- **Gap between sections:** Separator components or mb-16

### Components

Reuse existing shadcn/ui components:
- `badge` - For tech stack and status
- `button` - For all CTAs
- `card` - For grid items and featured template
- `accordion` - For "What You Get" and FAQ
- `separator` - Between major sections

---

## Technical Requirements

### Route

- **Path:** `/templates`
- **File:** `website/app/templates/page.tsx`

### Metadata

```typescript
export const metadata = {
  title: "Templates | The Agentic Engineer",
  description: "Production-ready starter templates turbo charged with AI workflows. Ship 10x faster with battle-tested code.",
  openGraph: {
    title: "Templates - Production-Ready Starters",
    description: "Ship 10x faster with AI-assisted development templates",
    images: ["/templates-og.png"], // TODO: Create OG image
  },
};
```

### Images Needed

1. **Featured template screenshot** (1200x800px)
   - Dashboard view of the Agentic SaaS Starter
   - Show clean UI, shadcn components
   - File: `/public/templates/agentic-saas-starter-hero.webp`

2. **Video thumbnail** (1920x1080px)
   - "Clone to Deployed in 5 Minutes"
   - File: `/public/templates/video-thumbnail.webp`

3. **OG Image** (1200x630px)
   - For social sharing
   - File: `/public/templates-og.png`

### Data Structure (Future-Proofing)

For when we have multiple templates, prepare data structure:

```typescript
// lib/templates.ts
export interface Template {
  id: string;
  slug: string;
  title: string;
  description: string;
  tagline: string;
  heroImage: string;
  videoUrl?: string;
  price: {
    regular: number;
    launch?: number;
    launchLimit?: number; // "First 100"
  };
  features: string[];
  techStack: string[];
  included: {
    code: string[];
    workflow: string[];
    docs: string[];
    support: string[];
  };
  status: "available" | "coming-soon";
  ctaLink: string; // Gumroad, Lemon Squeezy, etc.
}

export const templates: Template[] = [
  {
    id: "agentic-saas-starter",
    slug: "agentic-saas-starter",
    title: "Agentic SaaS Starter Kit",
    // ... rest of data
  }
];
```

### Responsive Breakpoints

- **Mobile:** < 768px
  - Single column layout
  - Stacked cards
  - Reduced font sizes
  - Full-width buttons

- **Tablet:** 768px - 1024px
  - 2-column grids where applicable
  - Side-by-side layouts maintained

- **Desktop:** > 1024px
  - 3-column grids
  - Full side-by-side layouts
  - Max-width containers

---

## Analytics & Tracking

### Key Events to Track

- Page view (`/templates`)
- CTA clicks:
  - "Buy Now - $99" (primary conversion)
  - "View Details" (engagement)
  - "Suggest a Template" (community input)
  - "View Docs" (education)
- Video play (engagement)
- FAQ accordion opens (which questions are most common?)
- Tech stack badge hovers (interest signals)

### Tools

- Vercel Analytics (built-in)
- Optional: Plausible or Fathom for privacy-friendly analytics

---

## Content Strategy

### SEO Optimization

- **Primary Keyword:** "SaaS starter template"
- **Secondary Keywords:** "Next.js SaaS template", "AI development workflow", "production-ready SaaS"
- **Meta Description:** "Production-ready SaaS starter templates with AI workflows. Ship 10x faster with Next.js 15, Convex, Clerk, and Claude Code slash commands. Launch price $99."

### Social Sharing

- Custom OG image showing the template features
- Twitter card: Summary with large image
- LinkedIn: Professional framing (productivity, modern dev tools)

---

## Implementation Plan (High-Level)

**Phase 1: Core Structure**
1. Create `/templates` route
2. Build page layout with all sections
3. Implement responsive design

**Phase 2: Components**
1. `FeaturedTemplateCard.tsx`
2. `PoweredByStack.tsx`
3. `WhyThisTemplate.tsx`
4. `TemplateFeatures.tsx` (accordion)
5. `VideoPreview.tsx`
6. `TemplatesCTA.tsx`
7. `TemplatesFAQ.tsx`

**Phase 3: Content & Assets**
1. Generate hero image (screenshot of starter template)
2. Create video walkthrough
3. Generate OG image
4. Write final copy (review and polish)

**Phase 4: Integration**
1. Add "Templates" link to navbar
2. Set up payment integration (Gumroad/Lemon Squeezy)
3. Test purchase flow
4. Add analytics tracking

**Phase 5: Launch**
1. Blog post announcing the template
2. Social media promotion
3. Email to existing audience
4. Monitor analytics and iterate

---

## Future Scaling (Multiple Templates)

When we have 2+ templates:

**Gallery View (`/templates`):**
- Grid of template cards (2-3 columns)
- Each card: Thumbnail, title, tagline, price, "Learn More" CTA
- Category filters (SaaS, E-commerce, Portfolio, etc.)
- Featured template at top

**Individual Landing Pages (`/templates/[slug]`):**
- Reuse current single-template structure
- Customized per template
- Shared components for consistency

**Refactor Needed:**
- Move current content to `/templates/agentic-saas-starter`
- Create gallery component for main `/templates` page
- Extract reusable template page structure

---

## Open Questions for Review

1. **Pricing Integration:** Gumroad vs Lemon Squeezy vs Stripe Checkout?
2. **Video Hosting:** YouTube (unlisted) vs Loom vs self-hosted?
3. **GitHub Access:** Automated via webhook after purchase or manual?
4. **Launch Price Tracking:** How to track "First 100" automatically?
5. **CTA Copy:** "Buy Now" vs "Get Started" vs "Purchase Template"?
6. **Template Suggestions:** Email form, TypeForm, or GitHub Issues?

---

## Success Metrics

### Primary KPIs
- Conversion rate (page views → purchases)
- Revenue from template sales
- Average time on page

### Secondary Metrics
- Video completion rate
- FAQ accordion engagement
- "Suggest a Template" submissions
- Social shares
- Return visitors

### Targets (Month 1)
- 1,000 page views
- 3% conversion rate (30 sales)
- $2,970 revenue (at $99/sale)
- 10+ template suggestions

---

## Notes & Considerations

### Messaging Clarifications

**Claude Code Positioning:**
- Not "required" - it's a tool in the ecosystem
- Slash commands are **portable** to any AI coding agent supporting slash commands
- Users can copy-paste into Cursor, Windsurf, etc.
- Template works standalone (just slower without AI assistance)

**Honest Marketing:**
- Avoid "only" claims
- Focus on value (save time, ship faster)
- Be specific about what's included
- Set realistic expectations (5 min setup requires API keys, not instant)

**Pricing Psychology:**
- Strikethrough regular price shows value
- Launch price creates urgency
- "First 100" creates scarcity
- $99 is impulse-buy territory for devs

---

**Document Version:** 1.0.0
**Status:** Draft - Ready for Review
**Next Steps:** Review, refine, then move to implementation planning
