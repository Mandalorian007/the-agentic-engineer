I've been wrapping coding CLIs in YOLO modes and permission guards to fake a production agent. The platforms just shipped the real thing.

Claude Code, Codex, and the Gemini CLI are built for one customer: a developer at a keyboard, steering in real time. Managed agents flip that. They're asynchronous and close to one-shot. You trigger one, it runs in a locked-down container with least-privilege access to exactly the tools and credentials it needs, and you get a result back. No mid-run hand-holding.

That one property changes the whole design. Because each agent is isolated and async, you fan out hundreds in parallel, which is exactly what you want behind an evaluation harness.

The building blocks rhyme across every provider:

→ A container with an engine inside it
→ Wiring for credentials, MCP servers, and network rules
→ A mesh of sub-agent-style nodes, each independently containerized
→ A memory layer so agents improve between runs

The MCP wiring is the part I keep coming back to. The internal agent I work on at Airbnb sits behind CLI and API MCP servers with real authentication and authorization, and getting that tool surface scoped correctly is most of the production work. Managed agents make that scoping a first-class config file instead of glue code.

To get concrete I built Frontier Brief, a code-first POC on Anthropic's platform. An orchestrator fans out to three researchers, one per provider, and assembles a weekly Markdown brief on AI releases. Every agent, environment, and memory store is a YAML or Markdown file you diff in a PR. When a source URL 404s, the agent finds the new canonical link and writes it back to memory, so it self-heals across runs.

The trajectory is clear: this becomes the standard way to package an agent and ship it, with the compliance and isolation production actually needs.

For the platform leads here: are you moving autonomous workflows onto managed agents yet, or still wrapping CLIs by hand to get there?
