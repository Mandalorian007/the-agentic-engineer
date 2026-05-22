# Generate Social Media Posts

Generate platform-optimized social media posts for an existing blog post and add them to the frontmatter.

## Task

You will:
1. Read the MDX file path from the command arguments
2. Extract the slug (filename without .mdx) to calculate actual URL length
3. Parse the blog post to understand: title, description, content, category
4. Calculate the actual URL that will be appended (https://agentic-engineer.com/blog/{slug})
5. Generate platform-specific social media posts within limits INCLUDING the URL:
   - **Twitter**: Total max 280 chars (text + URL + \n\n)
   - **LinkedIn**: Total max 3000 chars (text + URL + \n\n)
6. Apply the voice rules and humanizer patterns below during drafting (not as a separate pass)
7. Update the frontmatter with a `social:` section containing the generated posts
8. Preserve all existing frontmatter fields

## Voice & byline

These posts ship under a single author. The voice must reinforce his credentials, not flatten into generic AI-trends commentary, and not overclaim them either.

**The author:**
- Matthew Fontana — Staff Engineer at Airbnb (Data Management), ex-Staff Engineer at Spotify (Productivity Engineering, Chair of the Technical Steering Group), ex-Senior Engineer at UPS, founder of TabletopAdventureCreator.com (generative-AI SaaS, live since 2022).
- Canonical bio: `website/app/about/page.tsx`. Read the EXPERIENCE timeline and bio paragraphs before drafting if you have time.

**Voice rules:**
- **First-person practitioner.** "I built X" / "what I run on every engagement" / "I've watched this fail at engineering orgs I've worked in." NOT "your team," NOT "your VP," NOT trend-report essay voice.
- **No year-counts or tenure claims.** No "13+ years," no "a decade of," no "X years in enterprise." The byline already does that work — stating it inside the post itself reads as overselling.
- **Don't namedrop in every post.** Across a sequence of posts, the reader should see employer anchors used selectively, not as a tic. Some posts run anchor-free if the topic doesn't earn one. If the current topic does earn an anchor, use ONE — not three.
- **Concrete numbers and named systems beat adjectives.** "30% reduction in non-business-focused dev cycles" beats "significantly more productive."
- **No essay-mode second person.** Banned openers across both platforms: "Every AI vendor…", "Your team has…", "Your VP of…", any opener that starts with an emoji followed by a rhetorical question. If your draft starts this way, rewrite.

## Lived-experience anchors

Every LinkedIn post should land at least one sentence that anchors the content in real work at a real named employer (when the topic earns it). Pick the closest match from this table. Use ONE anchor per post; don't stack.

| Topic | Anchor to pull from |
|---|---|
| Evaluations, agent quality, regression gates | Airbnb internal AI agent — eval framework that scores business outcomes, not unit pass rates |
| Internal MCP servers, AuthN/AuthZ, agent tool surfaces | Airbnb — CLI + API MCP servers behind the search-and-discovery agent, with internal authentication and authorization |
| Marketplace plugins, skills, sub-agents, hooks, slash commands | Airbnb — Claude Code Marketplace plugin combining skills, sub-agents, hooks, and commands |
| Data lineage, warehouse, column-level traversal | Airbnb Data Management — batch and real-time ingestion for column-level data lineage; Lineage API for multi-step traversal |
| Org-scale developer productivity, measurement, portfolio management | Spotify — Chair of the Productivity Engineering Technical Steering Group; six teams; 30% reduction in non-business-focused dev cycles |
| Platform adoption, "the standard everyone ends up using" | Pattern across three employers: Spring Boot at Spotify, OpenShift at UPS, the Claude Code plugin at Airbnb |
| Two-sided marketplaces, GDPR, data governance | Spotify — GDPR audit system for Spotify for Artists (artists, labels, distributors) |
| Solo founder, generative-AI products, shipping pre-AI-wave | TabletopAdventureCreator.com — solo-built generative-AI SaaS in production since 2022 |
| JVM, event sourcing, streaming, monolith carve-outs | UPS — Spring Cloud, AXON event sourcing, lambda architecture on Cassandra/Solr/Spark, OpenShift introduction |

If no anchor fits the topic, do not force one. But check honestly — the strongest version of almost any post on this blog has a real-work anchor in it.

Twitter has no room for a full anchor, but the post still benefits from voice. "I run this on every engagement" reads very differently from "Your team has this problem."

## Voice humanization

Social posts must pass the same humanizer patterns the body posts pass. AI tells in a 250-character tweet are louder than AI tells in a 2000-word essay — the reader has less to absorb.

**Apply humanizer patterns during generation, not after.**

If `~/.claude/skills/humanizer` is installed, skim its pattern catalog before generating. Patterns that matter most for short-form social copy:

- **Minimize em dashes (pattern #14).** Em dashes are old voice for this site. Use periods, commas, or colons instead. Aggressive on this rule.
- **No significance inflation.** Cut "game-changing," "revolutionary," "transformative," "powerful," "robust," "comprehensive," "critical," "essential." Let the specific claim do the work.
- **No AI vocabulary.** No "leverage," "unlock," "harness" (the verb), "delve," "navigate the landscape," "in today's fast-paced world," "at the end of the day."
- **No copula avoidance.** "What we have here is a problem" → "This is a problem." Just state it.
- **No false ranges.** "5–10x faster" when you mean ~7x. Pick the number, or drop the claim.
- **No rule-of-three filler.** Don't pad to three items when two carry the point.
- **No "moreover / furthermore / additionally" tic.** Cut.

**Project-specific overrides** (these take precedence over generic humanizer defaults):

- **Preserve product names verbatim.** Claude Code, Codex, Cursor, Gemini CLI, MCP, marketplace plugins, Windsurf, Copilot.
- **Do not un-hyphenate technical compound modifiers.** Keep: real-time, end-to-end, vendor-agnostic, plug-and-play, hands-on-keyboard.
- **Voice reference for cadence.** Read the first few paragraphs of `website/content/posts/2026-01-19-ai-toolkit-escape-ecosystem-lock-in.mdx` before drafting to calibrate sentence rhythm.

## Platform Requirements

### Twitter
- **Total character limit**: 280 chars (including text + \n\n + URL)
- **URL calculation**: Extract slug from filename, build URL: `https://agentic-engineer.com/blog/{slug}`
- **URL overhead**: len(URL) + 2 chars for \n\n (typically 74-90 chars depending on slug length)
- **Available for text**: 280 - url_overhead (typically 190-206 chars)
- **Voice**: First-person, practitioner-grounded. Sound like a senior engineer talking, not a content creator hooking.
- **Emojis**: Optional, not required. Never as the first character. One max if used.
- **Banned openers**: see Voice rules. Skip the "🧠 Hook? 👇" formula.
- **Format**: Lead with the observation or lived take. The CTA can be implicit; the URL is the CTA.

### LinkedIn
- **Total character limit**: 3000 chars (including text + \n\n + URL)
- **URL calculation**: Same as Twitter
- **URL overhead**: len(URL) + 2 chars for \n\n
- **Available for text**: 3000 - url_overhead (typically 2910-2926 chars)
- **Voice**: First-person practitioner. "I built X at Y" / "what I run on every engagement" / "I've watched this fail at the orgs I've worked in." NOT "your team," NOT "your VP," NOT trend-report essay voice.
- **First-line hook (the "see more" line):** LinkedIn posts with images collapse to ~150 characters in the feed before "…see more". Every blog post on this site ships with a hero image, so assume the post is collapsed in feed. **The first line must earn the expand on its own** — without the byline, without the rest of the post.

  **Hook patterns that work:**
  - A counter-intuitive number: "Engineers ship 98% more PRs with AI. Org delivery is flat."
  - A specific, named failure mode: "The reason your AI rollout stalled at 12% isn't training. It's the eval framework nobody built."
  - A concrete claim that begs the question: "I've watched the same agent-rollout pattern stall at three engineering orgs in the last 18 months."
  - A reframe of a familiar belief: "The model isn't the moat. The three layers underneath it are."

  **Hook patterns to avoid:**
  - Generic genre-openers: "Every AI vendor is in a race…"
  - Second-person rhetorical setups: "Your VP is prepping a readout…"
  - Anything that needs line two to make sense.

- **Anchor**: Land at most one lived-experience anchor per post, using the anchors table above. Place it after the hook, not before — the hook earns the click, the anchor closes the trust loop once they're already reading.
- **Engagement closer**: Every LinkedIn post ends with one of:
  - (a) A question for the network ("how are other platform leads running this?")
  - (b) Tag-bait for a specific role ("curious if other DevEx leads have hit this")
  - (c) An opinion stake worth disagreeing with
  The goal is to give former colleagues and other senior practitioners an entry point to engage. Broadcast-only posts get algorithm-buried.
- **Emojis**: None or minimal. Arrows (→) and bullets are fine for scannability.
- **Format / sequence**: Hook (line 1, earns the expand) → context or specific example → lived-experience anchor if one fits → framework or bullets → opinion or question → URL.
- **Banned openers**: see Voice rules.

## Frontmatter Schema

Add this structure to the existing frontmatter:

```yaml
social:
  twitter:
    text: "Generated Twitter post text here"
  linkedin:
    text: "Generated LinkedIn post text here"
```

## Example Output

For a post about agent evaluation frameworks:

```yaml
social:
  twitter:
    text: "I've stopped trusting any AI rollout that doesn't have a regression suite under it. Pass-fail at launch isn't an eval. Continuous eval against business outcomes is."
  linkedin:
    text: "Your platform team is one quiet model upgrade away from a regression you'll only spot when a PM files a ticket.\n\nThe Airbnb agent I work on now ships behind an eval framework that scores business outcomes, not unit pass rates. It runs on every config change, every prompt edit, every model swap. Engineers can move on a Friday afternoon without staging a 48-hour rollback.\n\nThree patterns I see when teams skip this layer:\n\n→ The iteration set and the test set are the same. You're overfitting; the dashboard number is fiction.\n→ Pass/fail is the only signal. A regression hitting 8% of queries shows up green.\n→ The eval runs once at launch. Tuesday's model upgrade silently breaks three of the most-used flows.\n\nCurious how other platform leads are running this. Continuous eval cadence, or still treating evals as a launch artifact?\n\nFull breakdown:"
```

Notice what this example does right:
- First line works as a standalone hook (under 150 chars, intriguing without context).
- Single lived-experience anchor (Airbnb eval framework) placed after the hook.
- No "13+ years," no employer name-stacking.
- First-person ("I work on," "I see") instead of "your team."
- No em dashes; arrows for scannability.
- Closes with a question that gives senior peers an entry point.

## Instructions

1. Read the MDX file from the argument
2. Extract the slug from the filename (remove .mdx extension)
3. Calculate the actual URL: `https://agentic-engineer.com/blog/{slug}`
4. Calculate URL overhead: len(URL) + 2 (for \n\n separator)
5. Calculate available character budget:
   - Twitter: 280 - url_overhead
   - LinkedIn: 3000 - url_overhead
6. Extract title, description, and scan content for key points. Identify which (if any) employer anchor from the table applies.
7. Generate Twitter post following the Twitter Voice / banned-opener / no-tenure rules.
8. Generate LinkedIn post following the LinkedIn Voice / first-line-hook / sequence / engagement-closer rules.
9. **Voice self-check** (do this before writing frontmatter):
   - LinkedIn: does the first line work as a standalone hook with the rest collapsed? If not, rewrite.
   - Does the post claim years of experience or tenure anywhere? If yes, cut.
   - Does it namedrop an employer for credibility-padding rather than because the topic earned it? If yes, cut.
   - Could a generic AI-trends commentator have written this? If yes, it's missing voice — rewrite.
   - Is it second-person ("you/your") when it could be first-person? Convert.
   - Em dashes present? Replace with periods/commas/colons.
   - Banned vocabulary (leverage, unlock, harness, delve, game-changing, robust, comprehensive)? Cut.
   - LinkedIn: does it close with engagement bait?
   Only proceed once these check out.
10. Update the frontmatter preserving all existing fields
11. Validate TOTAL length (text + url_overhead) is within limits
12. Show the user:
    - Generated posts
    - Character counts (text length, URL overhead, total length)
    - Which anchor (if any) was used, or a one-line note that no anchor fit
    - Confirmation that posts are within limits

## Error Handling

- If the file doesn't exist, show a clear error
- If frontmatter is malformed, show a clear error
- If the file already has social posts, ask the user if they want to regenerate
- Validate character limits before writing

## Notes

- The URL will be auto-appended by the posting script, so don't include it in the text
- You MUST calculate the actual URL length based on the slug
- Example slugs and their URL lengths:
  - `2025-10-12-voice-to-blog-automation` → 75 chars total (73 for URL + 2 for \n\n)
  - `2025-10-24-packaging-expertise-context-engineering` → 90 chars total
- Focus on making the posts valuable and engaging
- Use the blog content to inform the posts but don't just copy/paste
- Twitter teases the value; LinkedIn earns the click with the hook and rewards the read
- ALWAYS show the character breakdown so the user can verify limits are respected
- ALWAYS show which anchor was used (or that none fit) so the user can spot over-namedropping across a sequence of posts
