---
description: The one entry point. Idea in; post, issue, socials, surface kit, and a pushed commit out.
---

# Ship

`/ship <idea>` is the only command you need to run. Everything below happens
in order without stopping to ask, unless a step fails or the topic is
sensitive enough that you'd want to read the diff. Each step is still a
standalone command if one needs redoing.

One `/ship` produces, for a single Monday:

| Artifact | Where | Made by |
|---|---|---|
| Blog post | `website/content/posts/<date>-<slug>.mdx` | `/create-post` + `/humanizer` |
| Newsletter issue, derived from the post | `website/content/issues/<date>-<slug>.mdx` | `/create-issue --from-post` + `/humanizer` |
| Twitter + LinkedIn copy | post frontmatter `social:` | `/generate-socials` |
| Surface kit (what the human pastes on Monday) | `surface/<date>-<slug>.md` | this command |
| Commit on `main`, pushed | git | this command |

The post and the issue publish the same Monday. The tweet goes out on its own
and the surface kit lands in Discord that morning so the manual part (HN,
Reddit, LinkedIn) is a copy-paste from a phone.

## Steps

### 1. Date

```
uv run tools/next_publish_date.py
```

Use the reported date for both the post and the issue. If the user named a
date or asked to fill an earlier gap, use that instead and check it is a
Monday with `/check-buffer`.

### 2. Post

Run `/create-post` with the user's idea and the date. Note the path.

Decide the post's **shape** while writing and remember it for step 6:

- **tutorial**: a how-to someone would search for. Surfaces on Reddit.
- **claim**: a position someone could disagree with. Surfaces on Hacker News.

### 3. Humanize the post

```
/humanizer
Humanize the post at <post-path>.
Use my writing style from website/content/posts/2026-01-19-ai-toolkit-escape-ecosystem-lock-in.mdx as a reference.

Output rules:
- Do NOT modify image references.
- Preserve the YAML frontmatter exactly.
- Minimize em dashes (apply pattern #14 — em dashes are old voice for this site).
- Do NOT un-hyphenate technical compound modifiers like real-time, end-to-end, vendor-agnostic, plug-and-play, hands-on-keyboard.
- Preserve all product names (Claude Code, Codex, Cursor, MCP, etc.).
```

### 4. Issue, from the post

```
/create-issue --from-post <post-path>
```

Same date as the post. This is the letter version of the post: what the post
changed in how Matthew works, told in first person; what broke, only if the
post has a real failure in it; the post's own pasteable artifact. The sender
attaches the post link automatically, so the issue never summarises it.

Then humanize the issue:

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

### 5. Socials

```
/generate-socials <post-path>
```

### 6. Surface kit

Write `surface/<date>-<slug>.md`. This is the copy the human pastes on
Monday, so it must be finished text, not notes. Format:

```markdown
# <post title>

URL: https://agentic-engineer.com/blog/<slug>
Shape: tutorial | claim
Post: <post-path>

## LinkedIn

Paste as a text post. Put the URL in the first comment, not the body.

<the social.linkedin.text from the frontmatter, with the URL line removed>

## Hacker News            <- claim posts only

Submit between 8 and 10am Eastern. Title verbatim. Do not ask anyone to upvote.

Title: <post title, exactly>
URL: <post URL>

First comment (post it yourself, right after submitting):

Author here. <two to four sentences: what prompted the post, the one thing
you'd push back on yourself, and an invitation to disagree. First person,
no marketing.>

## Reddit                 <- tutorial posts only

r/ClaudeAI (or r/ClaudeCode if it is Claude Code specific). Text post, not a
link post. Link goes at the end of the body.

Title: <plain, specific, no clickbait; usually the post title minus any colon>

Body:

<the tutorial's core, 200-400 words, rewritten as a Reddit post: what it does,
the steps or the key snippet, one honest limitation. End with:
"Full write-up with the rest of the setup: <post URL>">
```

Include only the section that matches the shape, plus LinkedIn always.

### 7. Review

```
/mdx-quality-review <post-path>
/issue-quality-review <issue-path>
```

Fix anything reasonable. The issue review's email preview is the last read of
the issue and the attached post together.

### 8. Commit and push

```
git add website/content/posts/<date>-<slug>.mdx website/public/blog/<date>-<slug>/ website/content/issues/<date>-<slug>.mdx surface/<date>-<slug>.md
git commit -m "Ship: <post title>"
git push origin main
```

Nothing goes live at push. Vercel publishes the post at the frontmatter date,
`send-issue.yml` sends the issue that morning, `post-to-twitter.yml` tweets
and drops the surface kit into Discord. If the user said "preview only" or
"don't push", stop before this step and say where the files are.

### 9. Report

Four lines, readable on a phone:

- Post: title, date, shape, path
- Issue: subject
- Surface: which outlet, and that the kit is in Discord Monday morning
- Pushed, or not, and why

## What is deliberately not automated

Submitting to Hacker News, posting to Reddit, and posting on LinkedIn. These
are done by a person, on the morning of, from the surface kit. Automating
them gets accounts banned and, more to the point, doesn't work: platforms
distribute posts from people who show up in the thread.
