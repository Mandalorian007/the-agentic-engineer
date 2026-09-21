The model and the agent harness are two different products. Most people buy them as one.

The harness is the agent loop, the tool definitions, the context management, the permission system, the subagents. That is the part I actually value in Claude Code, and the part I have invested in: skills, sub-agents, hooks, and commands on top of it.

The model underneath is a separate decision. Claude Code never hardcoded api.anthropic.com, because Anthropic needed it to reach Bedrock and Vertex. Anything speaking the same wire format works, and OpenRouter speaks it in front of roughly 400 models.

Five environment variables and a shell function later, you choose what runs.

The part most people miss is that Claude Code does not run on one model. It fills four slots, and each is a separate decision:

→ Main, your session and the top-level loop
→ Small and fast, which is what a subagent reaches for when it spins up to grep a repo instead of burning your main model on a search
→ Sonnet tier and Opus tier, for /model calls and pinned subagents

That is a routing table, not a config chore. Strong model on main for the reasoning, something cheap underneath for the fan-out, each job billed at a rate that matches what it needs.

It also bites if you ignore it. Leave the tier slots blank and a bare Anthropic model id goes upstream. OpenRouter answers 200, quietly normalizes it to anthropic/claude-sonnet-5, and bills you full rate inside the session you set up to be cheap. Every slot needs a value.

The honest tradeoff: permission-mode auto stops working, because that classifier needs a Claude model. You are left running skip-permissions against a model you know less well than Claude, so put hooks under it.

Curious whether others running mixed setups are routing slots deliberately, or just pointing everything at one model and moving on.
