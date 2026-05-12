# Create with Social and Quality Review

Complete end-to-end workflow from idea to quality-reviewed post with social media content.

## Instructions

When the user runs `/create-social-quality-review <idea>`:

1. **Get next publish date:**
   ```bash
   uv run tools/next_publish_date.py
   ```
   Parse the output to get the date formats for the post.

2. **Create the post:**
   - Use `/create-post` command with the user's idea
   - Use the date from step 1 in the frontmatter
   - Remember the post file path (e.g., `website/content/posts/2025-10-20-automated-blog-publishing.mdx`)

3. **Humanize the post (drop AI-isms):**
   ```
   /humanizer
   Humanize the post at <post-path>.
   Use my writing style from website/content/posts/2026-01-19-ai-toolkit-escape-ecosystem-lock-in.mdx as a reference.

   Output rules:
   - Do NOT modify image references or the closing CTA paragraph linking to /services.
   - Preserve the YAML frontmatter exactly.
   - Minimize em dashes (apply pattern #14 — em dashes are old voice for this site).
   - Do NOT un-hyphenate technical compound modifiers like real-time, end-to-end, vendor-agnostic, plug-and-play, hands-on-keyboard.
   - Preserve all product names (Claude Code, Codex, Cursor, MCP, etc.).
   ```
   - This runs the voice pass directly after generation so socials and quality review see the humanized body.
   - **Voice sample path** above is the canonical voice anchor for this blog. Update it when a stronger-voice post lands.
   - Review the humanizer's diff before continuing if the post is on a sensitive topic.

4. **Generate social media posts:**
   ```bash
   /generate-socials website/content/posts/2025-10-20-automated-blog-publishing.mdx
   ```
   - This will add social media posts to the frontmatter
   - Social content will be validated in the next step

5. **Run quality review:**
   ```bash
   /mdx-quality-review website/content/posts/2025-10-20-automated-blog-publishing.mdx
   ```
   - Runs SEO check, Vale prose linting, and social validation
   - Ensure to resolve any reasonable issues that were discovered

6. **Final summary:**
   - Show the post file path
   - Remind user that post is ready to commit and push to deploy:
     ```bash
     git add .
     git commit -m "Add new blog post: <title>"
     git push origin main
     # Vercel will auto-deploy
     ```

## Example

```bash
/create-social-quality-review I want to write about migrating from Blogger to Next.js
```

This creates the post, generates social media content, runs quality review, and provides instructions for deployment.

## Note

Deployment is handled by:
1. Git commit (saves the post to version control)
2. Git push (triggers Vercel deployment)
3. Vercel auto-deploys and makes the post live
4. GitHub Actions automatically post to social media daily at 11:30 UTC (only when content is scheduled)

No build or publish commands needed!
