# Quality Check Command

Run quality checks on blog posts: prose linting with Vale and SEO analysis.

## Instructions

When the user runs `/quality-check <path>`:

1. **Validate the path:**
   - If path is a directory in `website/content/posts/`, find the `.mdx` file
   - If path is already an `.mdx` file, use as-is
   - If no path provided, ask the user to specify a post path
   - Path should be to an MDX file in `website/content/posts/`

2. **Sync Vale styles:**
   - Run `vale sync` (ignore in final results, just ensures vale settings are updated)

3. **Run Vale prose linting:**
   - Execute: `vale <path-to-post.mdx>`
   - Parse the output
   - Vale works with MDX files (ignores code blocks and frontmatter)

4. **Run SEO analysis:**
   - Execute: `uv run tools/seo_check.py <path-to-post.mdx>`
   - Parse the output
   - Validates:
     - Title length (30-60 chars optimal)
     - Description field exists and is 150-160 chars
     - Category field exists and is valid (one of 7 hardcoded options)
     - Heading structure (single H1, proper hierarchy)
     - Content length (300+ words)
     - Image alt text
     - Links

5. **Run social media validation:**
   - Extract slug from the filename (remove .mdx extension)
   - Execute: `uv run python -c "from pathlib import Path; from lib.social_validator import validate_social_posts, print_validation_results; from lib.frontmatter import parse_frontmatter; path='<path-to-post.mdx>'; slug=Path(path).stem; fm=parse_frontmatter(path); issues=validate_social_posts(fm, slug); print_validation_results(issues); import sys; sys.exit(1 if any(i.severity == 'error' for i in issues) else 0)"`
   - Parse the output
   - Validates:
     - Twitter total length (280 chars max including actual URL)
     - LinkedIn total length (3000 chars max including actual URL)
     - Calculates actual URL based on slug: https://agentic-engineer.com/blog/{slug}
     - URL overhead is len(URL) + 2 for \n\n (typically 74-90 chars)
     - Required `text` field for each platform
     - Proper schema structure
   - Warnings if no social posts defined

6. **Format and display results:**
   - Show a clean summary with three sections:
     - **Writing Issues** (from Vale)
     - **SEO Issues** (from seo_check.py)
     - **Social Media Issues** (from social_validator.py)
   - For each issue, include:
     - Severity (error/warning/suggestion)
     - Line number (if applicable)
     - Description
   - If no issues, show success message for that section

## Example

```bash
/quality-check website/content/posts/2025-10-12-my-post.mdx
```

This runs Vale prose linting and SEO analysis on the MDX file.
