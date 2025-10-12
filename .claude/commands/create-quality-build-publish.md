# Create, Quality Check, Build, and Publish

Complete end-to-end workflow from idea to published post.

## Instructions

When the user runs `/create-quality-build-publish <idea>`:

1. **Get next publish date:**
   ```bash
   uv run tools/next_publish_date.py
   ```
   Parse the output to get the date formats for the post.

2. **Create the post:**
   - Use `/create-post` command with the user's idea
   - Use the date from step 1 in the frontmatter
   - Remember the post directory path (e.g., `posts/2025-10-20-automated-blog-publishing/`)

3. **Run quality checks:**
   ```bash
   /quality-check posts/2025-10-20-automated-blog-publishing/
   ```
   - ensure to resolve any reasonable issues that were discovered and validate them before continuing to the build

4. **Build preview:**
   ```bash
   /build posts/2025-10-20-automated-blog-publishing/
   ```

5. **Publish to Blogger:**
   ```bash
   /publish posts/2025-10-20-automated-blog-publishing/
   ```

## Example

```
/create-quality-build-publish I want to write about automated blog publishing with Python and Blogger API
```

The post path from step 2 is passed to steps 3, 4, and 5.
