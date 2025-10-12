# Publish Command

Publish or update a blog post to Google Blogger.

## Instructions

When the user runs `/publish <path>`:

1. **Validate the path:**
   - If path is a directory, use as-is
   - If path is already a file ending in `post.md`, use the parent directory
   - If no path provided, ask the user to specify a post path

2. **Run the publish script:**
   - Execute: `uv run publish.py <path-to-post-directory>/`
   - This will:
     - Validate post content
     - Upload images to Cloudinary CDN (if not already cached)
     - Convert markdown to HTML
     - Create or update the post on Blogger (idempotent)
     - Update frontmatter with `blogger_id` and image metadata

3. **Display results:**
   - Show the publish operation summary
   - Indicate whether this was a CREATE or UPDATE operation
   - Display the post ID and blog URL
   - Show image upload status (uploaded or cached)
   - Confirm the post status (DRAFT or PUBLISHED)

4. **Important notes:**
   - Posts are created as DRAFT by default
   - To publish live, change `status: draft` to `status: published` in the post's frontmatter, then run `/publish` again
   - The operation is idempotent - safe to run multiple times
   - Images are hash-checked and only re-uploaded if changed

## Example

```
/publish posts/2025-10-12-my-post/
```

This publishes the post to Blogger as a draft (or updates an existing post).
