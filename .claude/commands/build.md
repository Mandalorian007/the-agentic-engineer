# Build Command

Validate and preview a blog post locally without publishing.

## Instructions

When the user runs `/build <path>`:

1. **Validate the path:**
   - If path is a directory, use as-is
   - If path is already a file ending in `post.md`, use the parent directory
   - If no path provided, ask the user to specify a post path

2. **Run the build script:**
   - Execute: `uv run build.py <path-to-post-directory>/`
   - This will:
     - Validate post content and frontmatter
     - Check image references
     - Convert markdown to HTML
     - Generate preview HTML file
     - Show validation summary

3. **Display results:**
   - Show the build output
   - Highlight any validation errors or warnings
   - Indicate the location of the generated preview file
   - Confirm whether the post is ready to publish

## Example

```
/build posts/2025-10-12-my-post/
```

This validates the post and creates `posts/2025-10-12-my-post/preview.html` for local review.
