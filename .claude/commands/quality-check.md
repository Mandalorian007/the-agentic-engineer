# Quality Check Command

Run quality checks on blog posts: prose linting with Vale and SEO analysis.

## Instructions

When the user runs `/quality-check <path>`:

1. **Validate the path:**
   - If path is a directory, append `post.md`
   - If path is already a file, use as-is
   - If no path provided, ask the user to specify a post path

2. **Sync Vale styles:**
   - Run `vale sync` ignore in final results. Just ensures vale settings are properly updated.

3. **Run Vale prose linting:**
   - Execute: `vale <path-to-post.md>`
   - Parse the output

4. **Run SEO analysis:**
   - Execute: `uv run tools/seo_check.py <path-to-post.md>`
   - Parse the output

5. **Format and display results:**
   - Show a clean summary with two sections:
     - **Writing Issues** (from Vale)
     - **SEO Issues** (from seo_check.py)
   - For each issue, include:
     - Severity (error/warning/suggestion)
     - Line number (if applicable)
     - Description
   - If no issues, show success message for that section
