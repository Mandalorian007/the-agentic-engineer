# Issue Quality Review

Quality check a newsletter issue before it ships.

## Instructions

When the user runs `/issue-quality-review <path>`:

1. **Confirm the path** points at a file under `website/content/issues/`. If it is under `content/posts/`, use `/mdx-quality-review` instead — issues and posts have different rules.

2. **Sync Vale settings** — run `vale sync` (ignore the output, this just refreshes the style packages).

3. **Prose lint** — execute:
   ```
   cat <path-to-issue.mdx> | vale --ext=.md
   ```
   The `--ext=.md` flag is required. `.vale.ini` only matches `*.md`/`*.txt`, so calling `vale <file.mdx>` directly returns "0 files" and silently passes.

   If `vale` is not installed (`command not found`), note it as optional and skip this step.

4. **Issue checks** — execute:
   ```
   uv run tools/issue_check.py <path-to-issue.mdx>
   ```
   This validates required frontmatter, subject length, description length, `archive_date` ordering, body word count, and issue-specific rules (no local images, at least one code block).

5. **Email preview** — execute:
   ```
   uv run tools/send_issue.py --dry-run --date <YYYY-MM-DD from the frontmatter>
   ```
   This composes the actual email body, including whichever post the sender attaches (the newest one published since the previous issue, if any). Read the output and check:
   - The issue reads as a letter, not as a preamble to the post
   - The attached post section renders correctly, or is correctly absent
   - No relative links survived (every URL should start with `https://`)

6. **Read the issue against the rules** — the mechanical checks cannot catch these, so read the draft yourself and flag:
   - **Redundancy with the post.** Apply the test from `/create-issue`: could this sentence appear in the blog post? If yes it does not belong here.
   - **Missing artifact.** Every issue should carry one thing a reader can paste.
   - **Manufactured failure.** If the "what broke" segment reads as invented, say so. Two honest segments beat three with a fake one.
   - **Em dashes.** They are old voice for this site. Suggest commas, full stops, or colons.

7. **Report** in three sections:
   - **Writing Issues** (from Vale)
   - **Issue Checks** (from `issue_check.py`)
   - **Editorial** (your own read against the rules in step 6)

   For each, give severity (error / warning / suggestion), line number where applicable, and a one-line description. Print a success line per section when it is clean.

## Example

```
/issue-quality-review website/content/issues/2026-09-21-three-hooks.mdx
```
