What makes a tech stack powerful for working with AI agents? After six months of experimentation, my opinions have shifted dramatically.

The core principle: One language, end-to-end type safety.

When you use TypeScript everywhere—frontend, APIs, database access, business logic—you get magic:

• Single context for language standards (AI learns patterns once)
• One type-checking command validates UI → API → database
• Type safety across all boundaries
• AI can verify correctness using types

My stack:

Next.js - Framework
• Built-in SEO, SSR, static generation
• LLMs know it intimately
• Rich ecosystem (shadcn/ui, Tailwind)
• Perfect for web-first SaaS

Convex - Database
• End-to-end type safety with Zod schemas
• One source of truth for data models
• Types flow through entire stack
• MCP integration for direct database access

Clerk - Auth & Subscriptions
• Pre-built components, zero auth code
• Managed subscription infrastructure
• Simple permissions API
• Up and running in minutes

But the real game-changer? MCP integrations:
• shadcn MCP - Agent knows all available components
• Convex MCP - Direct database queries from AI

Small, clean codebase. Easy to reason about. Perfect for AI context windows. End-to-end type checking. Rapid iteration.

The god-tier stack for agentic engineering:
