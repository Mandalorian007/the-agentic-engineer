The harness is the bet, not the vendor. Five primitives, portable across Claude Code, Codex, Gemini CLI, and Cursor.

The AI agent I shipped at Airbnb runs as a Claude Code Marketplace plugin: skills, sub-agents, hooks, slash commands, sitting on top of CLI and API MCP servers with internal AuthN and AuthZ. That stack is where the business logic actually lives. The model underneath is a swap.

Marketplace plugins are converging into an open-ish spec, and the primitives every major agent platform either supports or is racing to support are the same five:

1. Slash commands. Named entry points the user invokes directly. /research, /dashboard, /triage.
2. Skills. Auto-invocable capability blocks the agent pulls in when relevant.
3. Sub-agents. Spawned helpers for parallel research, isolated tool permissions, or specialized roles.
4. Hooks. Interception points around lifecycle events (pre-tool-use, post-edit, session-start).
5. MCPs. Not strictly plugin-native, but plugins bundle them, and this is where the tool surface lives.

Commands and skills are how work enters. Sub-agents are how it parallelizes. Hooks are how it stays safe. MCPs are how it touches the business.

Coverage across the four platforms that matter is already strong:

→ Claude Code: full across all four primitives. The reference implementation.
→ Gemini CLI: closest match for portability.
→ Codex CLI: ports commands and skills cleanly, weak on sub-agents and hooks.
→ Cursor: strong on sub-agents and hooks, converts skills into Rules with different activation behavior.

None of the gaps are blockers. They're gotchas to track when you port. The honest rule of thumb I work to: design at the primitive level, port at the platform level. The vocabulary survives, some shimming is the cost of admission.

The pattern I see most often: a stack of MCPs and no workflows on top of them. This harness layer is where I'd invest next. Curious how other platform engineers are sequencing skills vs. sub-agents in real deployments, and where the harness has earned its keep for you.

Full breakdown and the coverage matrix:
