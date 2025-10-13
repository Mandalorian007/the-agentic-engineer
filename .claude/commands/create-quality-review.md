# Create and Quality Review

Complete end-to-end workflow from idea to quality-reviewed post.

## Instructions

When the user runs `/create-quality-review <idea>`:

1. **Get next publish date:**
   ```bash
   uv run tools/next_publish_date.py
   ```
   Parse the output to get the date formats for the post.

2. **Create the post:**
   - Use `/create-post` command with the user's idea
   - Use the date from step 1 in the frontmatter
   - Remember the post file path (e.g., `website/content/posts/2025-10-20-automated-blog-publishing.mdx`)

3. **Run quality review:**
   ```bash
   /mdx-quality-review website/content/posts/2025-10-20-automated-blog-publishing.mdx
   ```
   - Ensure to resolve any reasonable issues that were discovered

4. **Final summary:**
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
/create-quality-review I want to write about migrating from Blogger to Next.js
```

This creates the post, runs quality review, and provides instructions for deployment.

## Note

Deployment is handled by:
1. Git commit (saves the post to version control)
2. Git push (triggers Vercel deployment)
3. Vercel auto-deploys and makes the post live

No build or publish commands needed!
