---
description: Transcript in; cleaned transcript, post, issue, surface kit, verify table, pushed commit out.
argument-hint: <transcript path or pasted text> [--date YYYY-MM-DD] [--no-push]
---

# Create content

`/create-content <transcript>` is the one entry point. A spoken or dictated
transcript goes in. Out come, for a single Monday: the cleaned transcript,
the blog post with its hero image, the newsletter issue, the surface kit
(tweet, LinkedIn, and Hacker News or Reddit copy), a verify table proving
every piece landed, and a pushed commit.

You are the orchestrator. You clean the transcript yourself, because that is
the only step that may need to ask the user something. Everything after that
is done by subagents you spawn with the Agent tool, in the order below. You
never write a post, issue, or social copy yourself.

| Artifact | Path | Made by |
|---|---|---|
| Cleaned transcript | `transcripts/<stem>.md` | you |
| Blog post | `website/content/posts/<stem>.mdx` | `blog-writer` |
| Hero image | `website/public/blog/<stem>/hero-*.webp` | `blog-writer` |
| Newsletter issue | `website/content/issues/<stem>.mdx` | `newsletter-writer` |
| Tweet | `surface/<stem>/x.md` | `x-writer` |
| LinkedIn, plus HN or Reddit | `surface/<stem>/linkedin.md`, `hn.md` or `reddit.md` | `linkedin-writer` |
| Fixes | in place | `post-qc`, `issue-qc`, `social-qc` |
| Verify table | printed | `tools/verify_content.py` |

`<stem>` is `YYYY-MM-DD-slug` and is the same for every file.

## The preamble

Every subagent prompt you send starts with these lines, verbatim:

```
Load the following skills for consistency: <my-voice> <humanizer>
Use the Skill tool for each. If the Skill tool does not list them, Read
.claude/skills/my-voice/SKILL.md and .claude/skills/humanizer/SKILL.md and follow them.
You are running non-interactively. Never call AskUserQuestion. When something is
ambiguous, decide and list the decision under "Decisions:" in your final message.
The file you write is the deliverable. Apply humanizer patterns while drafting; do
not print draft/audit/final versions in your reply.
```

## Steps

### 0. Arguments and preflight

Parse `$ARGUMENTS`. Take `--date YYYY-MM-DD` and `--no-push` out if present.
What remains is either a path to a transcript file or the transcript text
itself.

Preflight in one Bash call:

```
which aitk vale; git branch --show-current; git status --porcelain | wc -l
```

- If `aitk` is missing, stop and say so. Nothing else runs without it.
- If the branch is not `main`, stop and say so.
- If the working tree is dirty, warn and continue.

### 1. Date

Without `--date`: `uv run tools/next_publish_date.py` and use the reported
date. With `--date`: confirm it is a publish day and that no
`website/content/posts/<date>-*.mdx` exists.

### 2. Clean the transcript (you, not a subagent)

Read the transcript in full. Then produce the cleaned version:

- Remove um, uh, erm, false starts, doubled words, and "you know", "kind of",
  "sort of", "like" where they carry nothing.
- Resolve mis-heard technical terms, product names, CLIs, env vars, and
  email addresses to what was meant: Claude Code, Codex, Cursor, MCP,
  OpenRouter, uv, tmux, Tailscale, `ANTHROPIC_BASE_URL`. When unsure, keep
  the spoken form and add `[sic?]`.
- Keep first person, the speaker's order, and every number, name, and
  specific. Paragraph breaks where the speaker paused. One heading at the
  top: `# <working title>`. No other headings.
- Do not summarise, reorder, or improve the argument. Target 85 to 100
  percent of the raw word count.
- Choose the slug: three to six lowercase hyphenated words from the topic,
  no dates, no stopwords. `<stem>` is `<date>-<slug>`.

**Sensitivity scan, before writing anything.** The repo is public. List
every candidate: third-party personal names, email addresses, phone numbers,
employer or client internals (system names, unreleased work, customer
names), compensation, health details, anything the speaker marked as off the
record, credentials or hostnames. If the list is empty, say so in one line
and continue. If not, ask once with `AskUserQuestion` (multi-select), one
option per item, each labelled with the phrase and your proposed treatment:
keep verbatim, abstract to a role ("a colleague", "an internal service", "a
large marketplace company"), or cut the sentence. Apply the answers. This is
the only question the whole command asks.

Write `transcripts/<stem>.md`. Record how many items were abstracted for the
report; never record what they were.

### 3. Blog post (sequential)

Spawn `blog-writer` with the Agent tool (`subagent_type: blog-writer`) and
wait for it. The prompt is the preamble, then:

```
Transcript: transcripts/<stem>.md
Stem: <stem>
Date: <date>
Post: website/content/posts/<stem>.mdx
Images: website/public/blog/<stem>/
URL: https://agentic-engineer.com/blog/<stem>
```

When it returns, Read the first twelve lines of the post and take `title`,
`shape`, and `description` from the file, not from the return block.

**If the return block says `IMAGES: FAILED`, stop here.** Spawn nothing
else. Print the aitk command and its error verbatim, the post path (it is
written), and the likely fix: `aitk config`, credentials, network. End your
turn. When the user says it is fixed, re-spawn `blog-writer` with the same
prompt plus "The post exists. Generate only the images it references, then
return." and continue at step 4.

### 4. Issue and socials (parallel)

Spawn `newsletter-writer`, `x-writer`, and `linkedin-writer` in one message,
three Agent calls, so they run concurrently. Each prompt is the preamble,
then:

```
Transcript: transcripts/<stem>.md
Post: website/content/posts/<stem>.mdx
Stem: <stem>
Date: <date>
Title: <title>
Shape: <shape>
URL: https://agentic-engineer.com/blog/<stem>
Output: <that agent's file or files>
```

Do nothing else until all three have returned.

### 5. Quality control (parallel)

Spawn `post-qc`, `issue-qc`, and `social-qc` in one message. Each gets the
preamble and the paths it needs (post path and stem; issue path, stem, post
path, and date; kit directory, stem, post path, shape, title, and URL).
Collect each `STATUS:` and `ITEM:` line.

### 6. Verify

```
uv run tools/verify_content.py <stem>
```

Exit 0: go to step 7.

Exit 1: read the `RE-RUN:` line. Spawn exactly the writers it names, in one
message if several, each with the preamble, its original inputs, and:

```
Fix only these rows. Do not rewrite the file.
<the failing rows for that owner, pasted verbatim from the table>
```

Then run verify again. At most two such loops. On a third failure, skip step
7 and report the table as it stands.

Rows P9 and P10 (images) are never re-run. A failure there is external
breakage; report it to the user with the detail column.

### 7. Commit and push

Only when verify exited 0 and `--no-push` was not given:

```
git add transcripts/<stem>.md website/content/posts/<stem>.mdx website/public/blog/<stem>/ website/content/issues/<stem>.mdx surface/<stem>/
git commit -m "Ship: <title>"
git push origin main
```

With `--no-push`, print those three lines instead and say the files are in
place.

Nothing goes live at push. Vercel publishes the post at the frontmatter
date, `send-issue.yml` sends the issue that morning, `post-to-twitter.yml`
tweets `x.md` and drops the surface kit into Discord.

### 8. Report

In this order, readable on a phone:

- **Post:** title, date, shape, category, path
- **Transcript:** path, and how many items were abstracted
- **Issue:** subject, path
- **Surface:** which platform file was written, and that Discord receives the
  kit on the morning of
- **Verify:** the full table, verbatim, in a fenced block
- **QC:** any `unfixable` items from step 5, or "clean"
- **Loops:** how many verify re-runs
- **Pushed:** yes, or no and why

## What is deliberately not automated

Submitting to Hacker News, posting to Reddit, and posting on LinkedIn. A
person does those on the morning of, from the surface kit in Discord.
Automating them gets accounts banned, and platforms distribute posts from
people who show up in the thread.
