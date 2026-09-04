# Create Newsletter Issue

You are helping write an issue of the newsletter for The Agentic Engineer. An issue is **not** a blog post and it is **not** a summary of one. It is a short letter from Matthew about what actually changed in how he works. It ships on its own schedule and carries the newest blog post published since the last issue, if there is one. Often there will not be, and that is fine: the letter stands alone.

## What an issue is for

The blog post is the durable artifact: evergreen, structured, written to be found by search nine months later. The issue is the opposite. It is dated, first person, and says the things a post cannot hold because a post has to stay true forever.

Subscribers get the issue first. It becomes a public page at `/issues/{slug}` thirty days later.

## Your Task

1. Ask what happened since the last issue, if the user has not already said
2. Draft the issue in the three-segment structure below
3. Save it to `website/content/issues/YYYY-MM-DD-slug.mdx` with correct frontmatter

## The three segments

### 1. What changed in my setup (always present)

The recurring beat. A concrete change to how Matthew works: a new hook, a slash command he rewrote, a permission rule he tightened, a tool he dropped. Draw from real commits in this repo where possible — run `git log --oneline -20` and look for what actually moved.

This is the segment that makes the newsletter worth subscribing to, because it is the thesis in practice: encoding what you are great at so you can hand it to agents one step at a time.

### 2. What broke (include when true)

A failure, honestly reported. What was tried, what happened, what it cost. Do not manufacture one. An issue with two segments is better than an issue with an invented third.

This is the highest-trust content in the newsletter and it is rare in this genre. Most people only publish wins.

### 3. One pasteable artifact (always present)

Something the reader can drop into their own repo today. A hook, a command file, a frontmatter template, a config block, a prompt. Show it in a fenced code block and say in one line what it does and where it goes.

If the artifact needs more than about 30 lines, it is a blog post, not an issue. Link to the repo instead.

## What does NOT belong

**A summary of the attached post.** `tools/send_issue.py` appends the post's title, description and a link under a "New on the blog" rule. That is all the pointer the reader needs. Summarising the post above it is redundant and makes the issue read like content marketing.

**A promise that a post is attached.** There may not be one. The sender only attaches a post if one shipped since the last issue, so never write "the post is right below" or "more on this in today's post." Write the letter so it reads correctly alone.

The test: **could this sentence appear in the blog post?** If yes, cut it from the issue.

Also avoid:
- "In this issue..." table-of-contents openers
- Generic life updates disconnected from the work
- Curated link roundups (that genre is saturated and it is not what this list signed up for)

## Voice

Match the blog's voice. The canonical sample is `website/content/posts/2026-01-19-ai-toolkit-escape-ecosystem-lock-in.mdx`.

Specifics for issues:
- First person, past tense, dated. "Last week I..." rather than "One should..."
- Minimize em dashes. Use a comma, a full stop, or a colon.
- Admitting uncertainty is good. It generates replies, and replies are what turn a list into an audience.
- 400 to 800 words total. If it runs longer, it wants to be a post.

## Frontmatter (required at top of MDX file)

```yaml
---
title: "Three hooks and a bad assumption"
subject: "What broke this week"
description: "150-160 character summary, used on the /issues archive page"
date: "2026-09-21T11:00:00Z"
archive_date: "2026-10-19T11:00:00Z"
---
```

**Fields:**
- `title` (required) — the archive page title, plain and descriptive
- `subject` (required) — the email subject line. Aim for 50 characters or fewer; most clients truncate past that. It can be punchier than the title.
- `description` (required) — 150-160 chars for the `/issues` page meta description
- `date` (required) — the send date, ISO 8601 with quotes. Future dates queue the issue.
- `archive_date` (optional) — when the `/issues` page appears. Omit to default to `date` plus `newsletter.archive_delay_days` from `blog-config.yaml` (30 days).

Issues have **no** `category` and **no** `hashtags`. They are not part of the blog taxonomy.

## Saving to disk

**CRITICAL**: Save with the Write tool to `website/content/issues/YYYY-MM-DD-slug.mdx`

Issues carry no images. There is no image directory to create, and no `../../public/` references to write. If a visual is essential, it belongs in the blog post.

## Process

1. **Get the date** — run `uv run tools/next_publish_date.py --stream newsletter`. It reports the next open slot and whether a post is already scheduled for that date.

2. **Find what changed** — run `git log --oneline -20` and skim for real changes to `.claude/`, `tools/`, or `lib/`. Ask the user which one mattered, or what happened that is not in the log.

3. **Draft the three segments** — segment 2 only if there is a genuine failure to report.

4. **Write the artifact** — make sure the code block actually works. A broken paste destroys more trust than a missing segment.

5. **Save to disk** — `website/content/issues/YYYY-MM-DD-slug.mdx`

6. **Preview the email** — `uv run tools/send_issue.py --dry-run --date YYYY-MM-DD` shows the composed body including the attached post.

7. **Review** — run `/issue-quality-review website/content/issues/YYYY-MM-DD-slug.mdx`
