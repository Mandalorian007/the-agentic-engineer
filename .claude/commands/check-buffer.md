---
description: Check content buffer and optionally send Discord notification
---

Check the content buffer status for The Agentic Engineer blog.

This command analyzes scheduled posts in `website/content/posts/` and reports:
- Number of posts scheduled
- Weeks of buffer remaining
- Date of last scheduled post
- When new content is needed

Usage:
- `/check-buffer` - Show buffer status (no notification)
- `/check-buffer --notify` - Show status and send Discord notification

Run the buffer check tool to see the current content pipeline status.
