# Generate Social Media Posts

Generate platform-optimized social media posts for an existing blog post and add them to the frontmatter.

## Task

You will:
1. Read the MDX file path from the command arguments
2. Extract the slug (filename without .mdx) to calculate actual URL length
3. Parse the blog post to understand: title, description, content, category
4. Calculate the actual URL that will be appended (https://agentic-engineer.com/blog/{slug})
5. Generate platform-specific social media posts within limits INCLUDING the URL:
   - **Twitter**: Total max 280 chars (text + URL + \n\n)
   - **LinkedIn**: Total max 3000 chars (text + URL + \n\n)
6. Update the frontmatter with a `social:` section containing the generated posts
7. Preserve all existing frontmatter fields

## Platform Requirements

### Twitter
- **Total character limit**: 280 chars (including text + \n\n + URL)
- **URL calculation**: Extract slug from filename, build URL: `https://agentic-engineer.com/blog/{slug}`
- **URL overhead**: len(URL) + 2 chars for \n\n (typically 74-90 chars depending on slug length)
- **Available for text**: 280 - url_overhead (typically 190-206 chars)
- **Tone**: Casual, engaging, conversational
- **Emojis**: 1-3 relevant emojis encouraged
- **Style**: Hook in first line, value proposition, call-to-action with emoji
- **Format**: Short paragraphs, use line breaks for readability

### LinkedIn
- **Total character limit**: 3000 chars (including text + \n\n + URL)
- **URL calculation**: Same as Twitter
- **URL overhead**: len(URL) + 2 chars for \n\n
- **Available for text**: 3000 - url_overhead (typically 2910-2926 chars)
- **Tone**: Professional, thought-leadership
- **Style**: Can be longer and more detailed than Twitter
- **Format**: Introduction, key insights, conclusion, call-to-action
- **Emojis**: Minimal or none, more professional

## Frontmatter Schema

Add this structure to the existing frontmatter:

```yaml
social:
  twitter:
    text: "Generated Twitter post text here"
  linkedin:
    text: "Generated LinkedIn post text here"
```

## Example Output

For a post titled "Taming Context Windows in Claude Code":

```yaml
social:
  twitter:
    text: "🧠 Context windows filling up too fast in Claude Code?\n\nI built a hook system that keeps sessions lean and focused.\n\nHere's how 👇"
  linkedin:
    text: "Working with AI coding assistants has taught me something valuable: context management is everything.\n\nI recently built a pre-compact hook system for Claude Code that automatically manages context windows. The result? 3-5x longer coding sessions before hitting limits.\n\nIn this article, I share the patterns and code that make it work.\n\nRead the full breakdown:"
```

## Instructions

1. Read the MDX file from the argument
2. Extract the slug from the filename (remove .mdx extension)
3. Calculate the actual URL: `https://agentic-engineer.com/blog/{slug}`
4. Calculate URL overhead: len(URL) + 2 (for \n\n separator)
5. Calculate available character budget:
   - Twitter: 280 - url_overhead
   - LinkedIn: 3000 - url_overhead
6. Extract title, description, and scan content for key points
7. Generate Twitter post:
   - Start with an emoji or hook
   - Focus on the main benefit/insight
   - Stay within available character budget (280 - url_overhead)
   - Use casual, engaging language
8. Generate LinkedIn post:
   - Professional opening
   - 2-3 key insights from the article
   - Value-focused conclusion
   - Stay within available character budget (3000 - url_overhead)
9. Update the frontmatter preserving all existing fields
10. Validate TOTAL length (text + url_overhead) is within limits
11. Show the user:
    - Generated posts
    - Character counts (text length, URL overhead, total length)
    - Confirmation that posts are within limits

## Error Handling

- If the file doesn't exist, show a clear error
- If frontmatter is malformed, show a clear error
- If the file already has social posts, ask the user if they want to regenerate
- Validate character limits before writing

## Notes

- The URL will be auto-appended by the posting script, so don't include it in the text
- You MUST calculate the actual URL length based on the slug
- Example slugs and their URL lengths:
  - `2025-10-12-voice-to-blog-automation` → 75 chars total (73 for URL + 2 for \n\n)
  - `2025-10-24-packaging-expertise-context-engineering` → 90 chars total
- Focus on making the posts valuable and engaging
- Use the blog content to inform the posts but don't just copy/paste
- Twitter should tease the value, LinkedIn can go deeper
- ALWAYS show the character breakdown so user can verify limits are respected
