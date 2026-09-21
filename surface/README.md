# Surface kits

One directory per post, written by `/create-content`, named like the post
(`YYYY-MM-DD-slug/`). It holds the finished copy for every outlet:

| File | What | Who posts it |
|---|---|---|
| `x.md` | Tweet text, no URL; the workflow appends the link | `post-to-twitter.yml`, automatically |
| `linkedin.md` | LinkedIn text post, no URL; the link goes in the first comment | a person |
| `hn.md` | `Title:` line, blank line, author comment (claim posts) | a person |
| `reddit.md` | `Subreddit:`, `Title:`, blank line, body ending with the URL (tutorials) | a person |

No header lines inside the files. Title, URL, and shape come from the post's
frontmatter when `tools/notify_surface.py` drops the kit into Discord on
publish morning, one section per outlet, so the routine is: open Discord on
your phone, copy, paste, answer replies.

Posts from before the layout existed have only `x.md` and `linkedin.md`,
migrated from their old frontmatter.

`tools/move_post_date.py` moves the kit with the post.
`tools/verify_content.py <stem>` checks a kit is complete and within limits.

These are committed on purpose. They are the record of what was said where.
