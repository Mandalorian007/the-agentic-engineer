# ShadcnBlocks Pro Setup Guide

This guide explains how to configure and install ShadcnBlocks Pro components (like blog27, blogpost5, navbar8, footer16) in this project.

## Prerequisites

- ✅ ShadcnBlocks Pro license purchased
- ✅ shadcn/ui already initialized in project
- ✅ `components.json` exists in project root

## Setup Steps

### 1. Generate Your API Key

1. Visit [shadcnblocks.com/dashboard/api](https://shadcnblocks.com/dashboard/api)
2. Click **"New API Key"**
3. Give it a name (e.g., "Development")
4. Optionally set an expiration date
5. **Copy the generated key** (starts with `sk_live_`)

### 2. Configure Environment Variables

Create or update `.env.local` in the `website/` directory:

```bash
SHADCNBLOCKS_API_KEY=sk_live_your_api_key_here
```

**Important**: Add `.env.local` to `.gitignore` to keep your API key private.

### 3. Update components.json

Add the namespaced registry configuration to `components.json`:

```json
{
  "$schema": "https://ui.shadcn.com/schema.json",
  "style": "new-york",
  "rsc": true,
  "tsx": true,
  "tailwind": {
    "config": "",
    "css": "app/globals.css",
    "baseColor": "neutral",
    "cssVariables": true,
    "prefix": ""
  },
  "iconLibrary": "lucide",
  "aliases": {
    "components": "@/components",
    "utils": "@/lib/utils",
    "ui": "@/components/ui",
    "lib": "@/lib",
    "hooks": "@/hooks"
  },
  "registries": {
    "@shadcnblocks": {
      "url": "https://shadcnblocks.com/r/{name}",
      "headers": {
        "Authorization": "Bearer ${SHADCNBLOCKS_API_KEY}"
      }
    }
  }
}
```

**Important**: The correct URL format is `https://shadcnblocks.com/r/{name}` (NOT `/api/registry/{name}.json`), and you must include the `headers` section with the Authorization bearer token.

### 4. Install Pro Blocks

Now you can install any Pro block using the shadcn CLI:

```bash
# Blog listing layout with image slots
pnpm dlx shadcn@latest add @shadcnblocks/blog27

# Individual blog post layout
pnpm dlx shadcn@latest add @shadcnblocks/blogpost5

# Navigation bar
pnpm dlx shadcn@latest add @shadcnblocks/navbar8

# Footer
pnpm dlx shadcn@latest add @shadcnblocks/footer16
```

The CLI will automatically use your API key from the environment variable for authentication.

## Troubleshooting

### ❌ "Authentication required for pro blocks"

**Possible causes:**
- API key not set in environment variables
- Incorrect environment variable name
- API key doesn't start with `sk_live_`

**Solutions:**
1. Verify your API key is correctly set: `echo $SHADCNBLOCKS_API_KEY`
2. Check the variable name matches exactly: `SHADCNBLOCKS_API_KEY`
3. Ensure the key starts with `sk_live_`
4. Restart your terminal/IDE to reload environment variables

### ❌ "Registry not configured"

**Possible causes:**
- Missing `registries` section in `components.json`
- Incorrect namespace configuration

**Solutions:**
1. Verify your `components.json` includes the `registries` section
2. Check that the namespace `@shadcnblocks` is defined
3. Ensure the URL template includes `{name}` placeholder

### ❌ "Invalid API key"

**Possible causes:**
- Expired API key
- Revoked API key
- Incomplete key format

**Solutions:**
1. Check if the key has expired in your dashboard
2. Verify the key hasn't been revoked
3. Generate a new key if needed

## Key Features of Pro Blocks

### blog27 (Blog Listing)
- Hero section with featured post and image
- Category filter tabs
- Post cards with image slots
- Grid/list layout options
- "Load More" pagination

### blogpost5 (Blog Post)
- 8:3 column split (content/sidebar)
- Table of contents with active section highlighting
- Author info section
- Social share buttons
- Breadcrumb navigation

### navbar8 (Navigation)
- Dynamic background change on scroll
- Responsive mobile menu
- Logo and navigation links
- Auth button integration points

### footer16 (Footer)
- Logo and description
- Navigation columns
- Accordion for mobile
- Social icons
- Newsletter form option

## Next Steps

After installing Pro blocks:

1. **Replace custom components** - Swap out the placeholder implementations in:
   - `app/blog/page.tsx` (use blog27)
   - `app/blog/[slug]/page.tsx` (use blogpost5)
   - `components/navbar.tsx` (use navbar8)
   - `components/footer.tsx` (use footer16)

2. **Add images** - Pro blocks have image slots; add actual blog post images

3. **Customize styling** - Adjust colors and spacing to match your brand

4. **Wire up content** - Connect Pro blocks to your MDX content system

## Resources

- [ShadcnBlocks Documentation](https://docs.shadcnblocks.com/)
- [ShadcnBlocks Dashboard](https://shadcnblocks.com/dashboard)
- [shadcn CLI Docs](https://ui.shadcn.com/docs/cli)
