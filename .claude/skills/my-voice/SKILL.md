---
name: my-voice
description: Matthew Fontana's voice for posts, issues, and social copy on agentic-engineer.com. Load before drafting or editing any content.
---

# my-voice

Everything on agentic-engineer.com ships under one author. This file is the
single place the voice is defined. Commands and agents point here instead of
carrying their own copy of the rules.

## Who is writing

Matthew Fontana. Principal Engineer at Aphora Health, where he owns AI
strategy and the agentic platform. Before that a Staff Engineer at Airbnb
(Data Management) and at Spotify (Productivity Engineering, chair of the
Technical Steering Group), and an engineer at UPS. Founder of
TabletopAdventureCreator.com, a solo-built generative-AI SaaS in production
since 2022.

The source of truth for the bio and the experience timeline is
`website/app/about/page.tsx`. If this file and that page disagree, the page
wins. Every employer before Aphora is past tense.

The site's one-line self-description: "I build the systems that make a
company faster. Right now that system is agents. Everything I write here is
something I actually run."

## Hard rules

These apply to every surface: post, issue, X, LinkedIn, Hacker News, Reddit.

- **First-person practitioner.** "I built", "I run", "I watched this fail".
  Never "your team", "your VP", never trend-report essay voice. Second person
  is fine when giving a reader instructions in a tutorial.
- **No tenure claims.** No "13+ years", "a decade of", "X years in". The
  timeline on the about page does that work. Stating it in the copy reads as
  overselling.
- **No consulting language.** No "on every engagement", "my clients", "teams
  I advise", "in my consulting practice". Consulting is not on offer. Talks
  and bounded workshops are, at `/speaking`, and only when the topic earns a
  mention.
- **No em dashes, no en dashes.** They are old voice for this site. Use a
  comma, a full stop, or a colon. Hyphens inside compound words stay.
- **Keep technical compound modifiers hyphenated.** real-time, end-to-end,
  vendor-agnostic, plug-and-play, hands-on-keyboard, column-level,
  first-person.
- **Product names verbatim.** Claude Code, Codex, Cursor, Gemini CLI,
  Windsurf, Copilot, MCP, OpenRouter, Buttondown, Vercel, uv, tmux,
  Tailscale, Claude Code Marketplace plugins.
- **Concrete beats adjective.** "30% reduction in non-business-focused dev
  cycles" beats "significantly more productive". A named system beats "a
  large internal tool". If there is no number, say the specific thing that
  happened instead.
- **Admit uncertainty.** "I am still not sure this holds past three teams"
  generates replies. Confident vagueness generates nothing.

### Banned openers

Rewrite if a draft starts with any of these, on any surface:

- "Every AI vendor…"
- "Your team has…" / "Your VP of…"
- An emoji followed by a rhetorical question
- "In today's fast-paced world" and its relatives

### Banned vocabulary

leverage, unlock, harness (the verb), delve, navigate the landscape,
game-changing, revolutionary, transformative, powerful, robust, comprehensive,
critical, essential, seamless, at the end of the day, moreover, furthermore,
additionally.

Also cut: significance inflation ("this changes everything"), copula avoidance
("what we have here is a problem" for "this is a problem"), false ranges
("5-10x faster" when the number is 7x), and rule-of-three padding when two
items carry the point.

## Lived-experience anchors

A LinkedIn post, and sometimes a blog post, lands harder with one sentence
that ties the topic to real work at a named employer. Use **one** anchor per
piece at most. If the topic does not earn one, use none. Across a run of
posts the reader should see anchors used selectively, not as a tic.

| Topic | Anchor |
|---|---|
| Company-wide AI strategy, agentic platforms, non-engineers running agents, security-vulnerability remediation, PHI or regulated data in the loop | Aphora Health, where I own AI strategy and the agentic platform: marketplace plugins, engineering platforms, automated vulnerability remediation, and agentic workflows for teams that do not write code, with pharmacy benefits and PHI in the loop |
| Evaluations, agent quality, regression gates | At Airbnb I put an internal AI agent behind an eval framework that scored business outcomes, not unit pass rates |
| Internal MCP servers, AuthN/AuthZ, agent tool surfaces | At Airbnb I built CLI and API MCP servers behind a search-and-discovery agent, with internal authentication and authorization |
| Marketplace plugins, skills, sub-agents, hooks, slash commands | At Airbnb I shipped a Claude Code Marketplace plugin that combined skills, sub-agents, hooks, and commands |
| Data lineage, warehouse, column-level traversal | Airbnb Data Management: batch and real-time ingestion for column-level lineage, and a Lineage API for multi-step traversal |
| Org-scale developer productivity, measurement, portfolio management | At Spotify I chaired the Productivity Engineering Technical Steering Group: six teams, and a 30% reduction in non-business-focused dev cycles |
| Platform adoption, "the standard everyone ends up using" | The same move four times: OpenShift at UPS, Spring Boot and then Productivity Engineering at Spotify, the agent platform at Airbnb, agents at Aphora |
| Two-sided marketplaces, GDPR, data governance | At Spotify I built the GDPR audit system for Spotify for Artists: artists, labels, distributors |
| Solo founder, generative-AI products, shipping before the AI wave | TabletopAdventureCreator.com, a generative-AI SaaS I built alone and have run in production since 2022 |
| JVM, event sourcing, streaming, monolith carve-outs | At UPS: Spring Cloud, AXON event sourcing, a lambda architecture on Cassandra, Solr and Spark, and the introduction of OpenShift |

## Cadence

The canonical sample is
`website/content/posts/2026-01-19-ai-toolkit-escape-ecosystem-lock-in.mdx`.
Read its first forty lines before drafting anything longer than a tweet. Take
the sentence rhythm and the plain register ("Here's the problem."), not its
frontmatter, which predates the current layout.

What the cadence sounds like: short declaratives, one idea per sentence, a
longer sentence only when the idea needs it. Paragraphs of two to four
sentences. Headings in sentence case. No bold-header bullet lists that read
as a slide deck. No closing "In conclusion".

## Per-surface notes

**Blog post.** The durable artifact, written to be found by search in nine
months. Second person is allowed in a tutorial's instructions. The intro
states the problem in the first two sentences. The post ends when the content
ends, without a call to action paragraph.

**Newsletter issue.** A dated letter, first person, past tense. "Last week I…"
rather than "One should…". It says what the post cannot: what it felt like to
run, what you would tell a friend, what you are still unsure about. It never
summarises the post, because the sender attaches the post underneath.

**X.** One observation or lived take, under the budget the validator
enforces. The URL is the call to action, so the text does not need one. No
emoji as the first character, one emoji at most.

**LinkedIn.** The first line is the hook and has to earn the click on its own,
because the feed collapses the post at about 150 characters. Then context or
a specific example, then the anchor if one fits, then arrows or short lines
for scannability, then a closing question or a stake worth disagreeing with.
The URL goes in the first comment, never the body.

**Hacker News comment.** "Author here." Two to four sentences: what prompted
the post, the one thing you would push back on yourself, an invitation to
disagree. No marketing. Never ask for votes.

**Reddit.** A plain, specific title. Text post, not link post. The body is the
tutorial's core with one honest limitation, and the link at the end.
