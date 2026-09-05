---
description: Entry point for a newsletter issue. Date to committed, humanized, reviewed, dry-run-previewed MDX.
---

# Create Issue Pipeline

End-to-end workflow for shipping one issue. Mirrors `/create-post-pipeline`, which does the same job for blog posts.

This is the entry point for the newsletter stream. It chains `/create-issue`, `/humanizer`, and `/issue-quality-review`; each of those still runs standalone if you want to redo one step.

## Steps

### 1. Get the publish date

```
uv run tools/next_publish_date.py --stream newsletter
```

Parse the output for the frontmatter date.

The `Same-day post` line is informational only. The sender attaches the newest post published since the *last issue*, so an issue can carry a post that shipped on an earlier Monday. Never write the issue as though a specific post is attached; there may be none.

### 2. Draft the issue

Use `/create-issue` with the user's raw material. Use the date from step 1 in the frontmatter.

Before drafting, run `git log --oneline -20` to find what actually changed in the repo. The "what changed in my setup" segment should be grounded in real commits, not invented.

### 3. Humanize

```
/humanizer
Humanize the issue at <issue-path>.
Use my writing style from website/content/posts/2026-01-19-ai-toolkit-escape-ecosystem-lock-in.mdx as a reference.

Output rules:
- Preserve the YAML frontmatter exactly.
- Do NOT modify code blocks. The pasteable artifact must stay byte-identical.
- Minimize em dashes (pattern #14 — em dashes are old voice for this site).
- Do NOT un-hyphenate technical compound modifiers like real-time, end-to-end, vendor-agnostic, plug-and-play, hands-on-keyboard.
- Preserve all product names (Claude Code, Codex, Cursor, MCP, etc.).
- Keep it in first person and past tense. This is a letter, not an article.
```

**Voice sample path** above is the canonical voice anchor for this blog. Update it when a stronger-voice post lands.

### 4. Review

```
/issue-quality-review <issue-path>
```

Runs Vale, `issue_check.py`, and an email preview. Resolve any reasonable issues found.

### 5. Preview the actual email

```
uv run tools/send_issue.py --dry-run --date <YYYY-MM-DD>
```

Read the composed body one more time as the subscriber will receive it. This is the last point where the attached post and the issue can be read together.

### 6. Commit

```
git add .
git commit -m "Add newsletter issue: <subject>"
git push origin main
```

## Notes

- Nothing sends at commit time. `.github/workflows/send-issue.yml` runs daily at 12:00 UTC and creates the Buttondown email on the issue's `date`.
- The scheduled workflow sends the issue for real at 12:00 UTC on its date. There is no draft step, so `uv run tools/send_issue.py --dry-run --date <date>` is the last chance to read it before subscribers do.
- The issue becomes a public page at `/issues/{slug}` after `newsletter.archive_delay_days`.
