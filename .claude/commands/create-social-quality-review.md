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

3. **Generate social media posts:**
   ```bash
   /generate-socials website/content/posts/2025-10-20-automated-blog-publishing.mdx
   ```
   - This will add social media posts to the frontmatter
   - Social content will be validated in the next step

4. **Run quality review:**
   ```bash
   /mdx-quality-review website/content/posts/2025-10-20-automated-blog-publishing.mdx
   ```
   - Runs SEO check, Vale prose linting, and social validation
   - Ensure to resolve any reasonable issues that were discovered

5. **Final summary:**
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
4. GitHub Actions automatically post to social media at scheduled time (Mon/Thu 10:00 UTC)

No build or publish commands needed!
