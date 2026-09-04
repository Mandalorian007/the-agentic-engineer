---
description: Check content buffer across both streams and optionally send a Discord notification
---

Run the buffer check to see the current content pipeline status.

Usage:
- `/check-buffer` — buffer status for both streams
- `/check-buffer --stream posts` — blog posts only
- `/check-buffer --stream newsletter` — newsletter issues only

Execute:
```
uv run tools/buffer_check.py [--stream posts|newsletter|both]
```

**This never posts to Discord.** Reporting and notifying are separate: the tool
only sends when given `--notify`, which is reserved for the scheduled workflow.
A webhook in `.env.local` does not change that, so checking the buffer while
writing cannot put a message in the channel.

## What it reports

One unified deadline at the top, then a ledger per stream
(`website/content/posts/` and `website/content/issues/`) covering the next two
months of slots. At the configured every-other-Monday cadence that is four
slots each. Every slot is listed, filled or empty, so the shape of the gap is
visible rather than summarised.

Each stream is rated on how many slots are filled *before its first gap*:

| Filled run | Status |
|---|---|
| 0 | 🚨 LOW, the very next slot is empty |
| 1-2 | ⚠️ WARN, a gap inside the next two or three slots |
| 3+ | ✅ GOOD |

Overall status is the worse of the two streams, so a healthy blog buffer cannot
mask an empty newsletter buffer. "Need content by" is the earliest gap across
both. Nothing special is needed for a post with no matching issue: it shows up
as a gap in the issues ledger on its own.

Both streams share one cadence, and each issue carries the newest post published
since the last issue went out, so an issue can carry a post from an earlier
Monday. An issue with no post to carry still sends.

Any scheduled file that does not fall on a publish day is listed separately, so
an entry moved to an off-cadence date cannot silently disappear from the report.

## Automation

`.github/workflows/buffer-check.yml` runs this every Saturday at 12:00 UTC with
`--force` (an alias for `--notify`) and the webhook from GitHub secrets. That is
the only thing that posts to Discord.
