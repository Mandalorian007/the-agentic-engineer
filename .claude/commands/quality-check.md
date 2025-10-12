# Quality Check Command

Run quality checks on blog posts including prose linting with Vale.

## Instructions

When the user runs `/quality-check <path>`:

1. **Validate the path:**
   - If path is a directory (e.g., `posts/2025-10-12-hello-world/`), append `post.md`
   - If path is already a file (e.g., `posts/2025-10-12-hello-world/post.md`), use as-is
   - If no path provided, ask the user to specify a post path

2. **Sync Vale styles:**
   - Run `vale sync` to ensure style packages are up to date
   - This is a quick operation and ensures consistency

3. **Run Vale prose linting:**
   - Execute: `vale <path-to-post.md>`
   - Show the full output to the user
   - Interpret the results:
     - 0 errors, 0 warnings = ✅ Perfect!
     - Only suggestions = 💡 Consider reviewing
     - Warnings = ⚠️ Should fix
     - Errors = ❌ Must fix

4. **Provide context:**
   - Explain any common issues found
   - Suggest fixes for warnings
   - Note that suggestions are optional for technical writing

## Notes

- Vale checks writing style, not technical accuracy
- Passive voice is sometimes clearer in technical documentation
- Code blocks and frontmatter are automatically ignored
- Configuration is in `.vale.ini`
