# Sync Publish Status

Sync publish status from Blogger API to local frontmatter files.

Run the sync tool to check all posts (or a specific post) on Blogger and update local frontmatter to match the actual published state:

```bash
# Sync all posts
uv run tools/sync_publish_status.py

# Sync specific post
uv run tools/sync_publish_status.py --post-dir $POST_DIR
```

This is useful when:
- You manually changed post status in Blogger's UI
- A scheduled post went live while you were away
- You're returning to the project after a break
- You want to verify local state matches Blogger

The sync tool will update:
- Post status (draft vs published)
- Published date
- Updated timestamp
