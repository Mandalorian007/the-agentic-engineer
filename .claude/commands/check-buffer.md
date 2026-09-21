---
description: Ledger of upcoming Mondays: shipped, half-shipped, or empty. Optionally post to Discord.
---

Run the buffer check to see which upcoming Mondays still need a `/create-content`.

Usage:
- `/check-buffer` — the ledger
- `/check-buffer --notify` — the ledger, posted to Discord (the Saturday workflow does this; you rarely need to)

Execute:
```
uv run tools/buffer_check.py
```

**This never posts to Discord** unless `--notify` is passed. A webhook in
`.env.local` does not change that.

## How to read it

One `/create-content` fills one Monday: a post, the issue derived from it,
and the surface kit. The ledger is one row per Monday for the next two months:

```
Mon Sep 14   Run Claude Code From Your Phone…   ✉ The agents run, I go buy shrimp
Mon Sep 21   Run Claude Code on Any Model…      ✉ …
Mon Sep 28   —
```

| Row | Meaning |
|---|---|
| post and ✉ issue | shipped |
| post with `⚠️ no issue`, or the reverse | half-shipped; the report says what to run |
| post with `⚠️ kit missing …` | the surface kit is incomplete; run `uv run tools/verify_content.py <stem>` |
| — | empty; needs a `/create-content` |

Status is how many Mondays are fully shipped before the first one that isn't:
0 is 🚨 LOW (next Monday is open), 1-2 is ⚠️ WARN, 3+ is ✅ GOOD. "Next
/create-content needed for" is the first non-shipped Monday.

Anything scheduled that does not fall on a publish day is listed under
off-cadence so a file moved to a Tuesday cannot silently vanish.

## What to do with it

If the next Monday is open: `/create-content <transcript>`. If a Monday is
half-shipped, spawn the writer the report names on that post's transcript.
To pull a later post forward into a gap: `uv run tools/move_post_date.py
<from> <to>` for the post (its surface kit moves with it) and again with
`--stream newsletter` for its issue.

## Automation

`.github/workflows/buffer-check.yml` runs this every Saturday at 12:00 UTC
with `--force` (an alias for `--notify`) and the webhook from GitHub secrets.
