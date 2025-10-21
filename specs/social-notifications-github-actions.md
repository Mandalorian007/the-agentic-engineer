# Social Media Automation

**Date**: 2025-10-21
**Status**: Design spec for automated social media posting with generated content

---

## Overview

**Problem**: Social media posts are manually created and posted, reducing consistency and control over platform-specific messaging.

**Solution**: Generate platform-optimized social posts during content creation, store in frontmatter, validate during quality review, and auto-post via GitHub Actions at publish time.

**Benefits**:
- ✅ Platform-specific messaging (Twitter, LinkedIn, etc.)
- ✅ Review and edit social posts before publishing
- ✅ Automated posting at exact publish times
- ✅ Version-controlled social content alongside blog posts
- ✅ Quality validation for platform requirements

---

### Components

**New Files:**
```
.claude/commands/generate-socials.md        # Command to generate social posts
lib/social_validator.py                     # Social media validation (char limits, etc.)
tools/post_to_twitter.py                    # Twitter posting script
tools/post_to_linkedin.py                   # LinkedIn posting script (future)
.github/workflows/post-to-twitter.yml       # Twitter workflow
.github/workflows/post-to-linkedin.yml      # LinkedIn workflow (future)
```

**Modified Files:**
```
.claude/commands/mdx-quality-review.md      # Add social validation step
pyproject.toml                              # Add platform API dependencies
website/app/blog/page.tsx                   # Remove ISR Twitter logic
```

### Workflow

**1. Content Creation:**
```bash
/create-post "blog idea"           # Creates blog post
/generate-socials <path-to-post>   # Generates social posts into frontmatter
```

**2. Quality Review:**
```bash
/mdx-quality-review <path-to-post>
# Runs: Vale + SEO + Social validation
```

**3. Publishing:**
```bash
git push  # Deploys blog
# GitHub Actions run independently:
# - post-to-twitter.yml at 10:00 UTC
# - post-to-linkedin.yml at 10:05 UTC (future)
```

### Frontmatter Schema

```yaml
---
title: "Blog Post Title"
description: "SEO description..."
date: "2025-11-20T10:00:00Z"
category: "tutorials"
hashtags: ["ai", "automation"]

social:
  twitter:
    text: "🚀 Just shipped: Deep dive into agentic engineering\n\nLearn how to build AI systems that build themselves 👇"
    # Future: hashtags, media, thread, etc.

  linkedin:
    text: "I just published a comprehensive guide on agentic engineering patterns.\n\n[Professional tone, longer format]\n\nRead the full article:"
    # Future: hashtags, images, etc.
---
```

**Social Field Rules:**
- Each platform is an object with `text` property (required)
- URL auto-appended by posting script
- Platform-specific character limits validated on `text` field
- Optional: omit entire platform if you don't want to post
- Future-proof: Can add `hashtags`, `media`, `thread` properties without breaking existing posts

**Migration Path:**
- V1 (now): Only `text` property required
- V2 (future): Add `hashtags: ["tag1", "tag2"]` alongside `text`
- V3 (future): Add `media: ["image1.png"]` or `thread: [...]`
- Validator checks for `text` property existence and validates based on known properties

## Implementation Tasks

### Task 1: Create /generate-socials Command

**Create:** `.claude/commands/generate-socials.md`

Generate platform-optimized social media posts and add to existing blog post frontmatter.

**Requirements:**
- Takes path to existing MDX file as argument
- Reads blog title, description, content for context
- Generates platform-specific posts (Twitter, LinkedIn)
- Updates frontmatter `social:` field with generated content
- Follows platform best practices (character limits, tone, hashtags)

**Platform Requirements:**
- **Twitter**: 280 char max (reserve ~30 for URL), casual/engaging tone, emojis ok, 1-3 hashtags
- **LinkedIn**: 3000 char max, professional tone, detailed, can be longer

**Example Output in Frontmatter:**
```yaml
social:
  twitter:
    text: "🚀 Just shipped: Deep dive into agentic engineering\n\nLearn how to build AI systems that build themselves 👇"
  linkedin:
    text: "I just published a comprehensive guide on agentic engineering patterns..."
```

---

### Task 2: Create Social Validator

**Create:** `lib/social_validator.py`

Validate social media posts against platform requirements.

**Functions:**
- `validate_social_posts(frontmatter: dict) -> list[dict]` - Returns list of validation issues
- Platform-specific validators (Twitter, LinkedIn)
- Check character limits (accounting for auto-appended URL)
- Validate schema structure

**Validation Rules:**
- **Schema**: Each platform must be a dict with `text` property
- **Twitter `text`**: Max 250 chars (reserves 30 for URL + space)
- **LinkedIn `text`**: Max 2970 chars (reserves 30 for URL + space)
- **Both**: `text` must be non-empty string if platform present
- **Warning**: If no social posts defined
- **Extensible**: Ignore unknown properties (forward-compatible)

**Example Validation:**
```python
# Valid
{"twitter": {"text": "Short tweet"}}

# Valid (with future properties - ignored for now)
{"twitter": {"text": "Tweet", "hashtags": ["ai"]}}

# Invalid - missing text
{"twitter": {"hashtags": ["ai"]}}

# Invalid - text is empty
{"twitter": {"text": ""}}

# Invalid - text too long
{"twitter": {"text": "x" * 300}}
```

---

### Task 3: Update Quality Review Command

**Modify:** `.claude/commands/mdx-quality-review.md`

Add social validation as fourth check (after Vale, SEO).

**Add Step:**
```bash
uv run python -c "from lib.social_validator import validate_social_posts; from lib.frontmatter import parse_frontmatter; import sys; fm = parse_frontmatter('$POST_PATH'); issues = validate_social_posts(fm); [print(f'{i}') for i in issues]; sys.exit(1 if issues else 0)"
```

**Display:**
- Section: "Social Media Validation"
- Show warnings/errors for each platform
- Success message if all valid

---

### Task 4: Create Twitter Posting Script

**Create:** `tools/post_to_twitter.py`

Post Twitter content from frontmatter.

**Functionality:**
- Load config from `blog-config.yaml`
- Find posts where date matches today (UTC)
- Read `social.twitter.text` from frontmatter
- Skip if `social.twitter` not present or `text` empty
- Build full tweet: `{social.twitter.text}\n\n{blog_url}`
- Post using Twitter API v2
- Log success/failure
- Exit 0 if no posts or successful, exit 1 only on posting errors

**Error Handling:**
- No posts today: Exit 0, log "No posts scheduled"
- Missing `social.twitter` field: Exit 0, log "No Twitter content"
- Missing `social.twitter.text`: Exit 0, log "No Twitter text"
- Twitter API error: Exit 1, log detailed error
- Missing credentials: Exit 1, log clear error

**Future Enhancement Support:**
- Currently only reads `text` property
- Ignores other properties (`hashtags`, `media`, etc.)
- Can be enhanced later to read and use additional properties

**Dependencies:**
- `twitter-api-v2>=2.1.0`

---

### Task 5: Create LinkedIn Posting Script (Future)

**Create:** `tools/post_to_linkedin.py`

Similar to Twitter script but for LinkedIn.

**Functionality:**
- Same pattern as `post_to_twitter.py`
- Reads `social.linkedin.text` from frontmatter
- Uses LinkedIn API SDK
- Future: Can read `hashtags`, `media` properties when enhanced

**Note:** Implement when ready to add LinkedIn support.

---

### Task 6: Create Twitter Workflow

**Create:** `.github/workflows/post-to-twitter.yml`

Scheduled workflow to post Twitter content.

**Configuration:**
- Name: `Post to Twitter`
- Schedule: `0 10 * * 1,4` (Mon/Thu 10:00 UTC)
- Manual trigger: `workflow_dispatch`
- Runs: `uv run tools/post_to_twitter.py`
- Secrets:
  - `TWITTER_API_KEY`
  - `TWITTER_API_KEY_SECRET`
  - `TWITTER_ACCESS_TOKEN`
  - `TWITTER_ACCESS_TOKEN_SECRET`

**Benefits:**
- Isolated failures: Twitter issues don't affect LinkedIn
- Easy monitoring: Check Twitter workflow status directly
- Independent retry: Can re-run just Twitter if it fails
- Clear logs: All Twitter output in one workflow run

---

### Task 7: Create LinkedIn Workflow (Future)

**Create:** `.github/workflows/post-to-linkedin.yml`

Similar to Twitter workflow but for LinkedIn.

**Configuration:**
- Name: `Post to LinkedIn`
- Schedule: `5 10 * * 1,4` (Mon/Thu 10:05 UTC - 5 min after Twitter)
- Manual trigger: `workflow_dispatch`
- Runs: `uv run tools/post_to_linkedin.py`
- Secrets: LinkedIn API credentials (TBD)

**Note:** Stagger by 5 minutes to avoid simultaneous posting.

---

### Task 8: Clean Up ISR Flow

**Modify:** `website/app/blog/page.tsx`

Remove Twitter notification logic from blog listing page.

**Changes:**
- Remove `tweetNewPost` and `isRecentlyPublished` imports from `lib/twitter`
- Remove social posting loop (lines 18-34)
- Keep only blog post rendering logic

---

### Task 9: Remove Old Twitter Integration Files

**Delete:** `website/lib/twitter.ts`

Remove the entire Next.js Twitter integration file.

**File contains (to be deleted):**
- `getTwitterClient()` - Twitter API client factory
- `tweetNewPost(post)` - Tweeting function (lines 26-54)
- `isRecentlyPublished(postDate)` - ISR timing helper (lines 60-66)

**Rationale:** This entire file is replaced by the Python-based approach. The old ISR-based Twitter integration is no longer needed.

---

### Task 10: Remove twitter-api-v2 from Next.js Dependencies

**Modify:** `website/package.json`

Remove `twitter-api-v2` from Next.js dependencies.

**Changes:**
- Remove line 44: `"twitter-api-v2": "^1.27.0"`
- Run `cd website && pnpm install` to update lockfile

**Rationale:** The `twitter-api-v2` package was only used by the old `lib/twitter.ts` file. The new Python-based approach uses `twitter-api-v2` as a Python dependency instead.

---

### Task 11: Add Python Dependencies

**Modify:** `pyproject.toml`

Add social media API clients for Python tools.

**Dependencies:**
- `twitter-api-v2>=2.1.0`

Run `uv sync` after updating.

**Note:** This is a Python dependency, separate from the removed Next.js dependency.

---

### Task 12: Update Documentation

**Modify:** `docs/architecture.md`, `README.md`

**Architecture Changes:**
- Replace ISR social posting section with GitHub Actions flow
- Document `/generate-socials` command
- Document social validation in quality review
- List platform requirements
- Document per-platform workflows and scripts

**README Updates:**
- Add `/generate-socials` to workflow
- Add GitHub secrets configuration per platform
- Document social frontmatter schema
- List separate workflows for each platform

---

## Validation

### Quality Checks

**Frontmatter Parsing:**
```bash
uv run python -c "from lib.frontmatter import parse_frontmatter; print(parse_frontmatter('website/content/posts/test.mdx')['social'])"
```

**Social Validation:**
```bash
uv run python -c "from lib.social_validator import validate_social_posts; from lib.frontmatter import parse_frontmatter; print(validate_social_posts(parse_frontmatter('website/content/posts/test.mdx')))"
```

**Twitter Posting Script:**
```bash
uv run tools/post_to_twitter.py  # Should handle no posts gracefully
```

**LinkedIn Posting Script (Future):**
```bash
uv run tools/post_to_linkedin.py  # Should handle no posts gracefully
```

### Manual Testing

- [ ] Generate social posts for existing blog post
- [ ] Validate social posts pass validation
- [ ] Validate social posts fail with bad data (too long, wrong type)
- [ ] Run quality review with social validation
- [ ] Test Twitter script locally with test credentials
- [ ] Test LinkedIn script locally (when implemented)
- [ ] Verify ISR flow has no social logic
- [ ] Trigger Twitter workflow manually via GitHub UI
- [ ] Trigger LinkedIn workflow manually (when implemented)
- [ ] Check workflow logs for clear success/failure messages

---

## Success Criteria

**Content Creation:**
- [ ] `/generate-socials` generates platform-specific posts
- [ ] Social posts stored in frontmatter under `social:` key
- [ ] Generated content respects platform character limits

**Quality Assurance:**
- [ ] Social validator catches character limit violations
- [ ] Quality review includes social validation step
- [ ] Clear error messages for validation failures

**Automation:**
- [ ] Each platform has dedicated workflow and script
- [ ] Twitter workflow posts at 10:00 UTC on Mon/Thu
- [ ] LinkedIn workflow posts at 10:05 UTC (when implemented)
- [ ] Scripts read social content from frontmatter
- [ ] Scripts append blog URL to social posts
- [ ] Platform failures are isolated (Twitter fail ≠ LinkedIn fail)
- [ ] Workflow logs clearly show which platform failed

**Monitoring:**
- [ ] GitHub Actions UI shows separate status per platform
- [ ] Can retry individual platforms without affecting others
- [ ] Failure notifications tie directly to platform (e.g., "Twitter posting failed")

**Cleanup:**
- [ ] Old ISR Twitter logic removed from `website/app/blog/page.tsx`
- [ ] `website/lib/twitter.ts` file deleted
- [ ] `twitter-api-v2` removed from `website/package.json`
- [ ] No references to old ISR-based Twitter posting remain
- [ ] Next.js codebase has no social media posting logic

**Documentation:**
- [ ] Platform requirements documented
- [ ] Per-platform workflows documented in README
- [ ] Architecture docs updated with separate tools approach
- [ ] GitHub secrets setup documented per platform
- [ ] Migration from ISR to GitHub Actions documented
