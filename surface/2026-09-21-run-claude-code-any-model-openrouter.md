# Run Claude Code on Any Model with OpenRouter

URL: https://agentic-engineer.com/blog/2026-09-21-run-claude-code-any-model-openrouter
Shape: tutorial
Post: website/content/posts/2026-09-21-run-claude-code-any-model-openrouter.mdx

## LinkedIn

Paste as a text post. Put the URL in the first comment, not the body.

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

First comment: Full write-up with the complete shell block: https://agentic-engineer.com/blog/2026-09-21-run-claude-code-any-model-openrouter

## Reddit

r/ClaudeCode. Text post, not a link post. Link goes at the end of the body.

Title: Claude Code is a harness, not a model. Five env vars and it runs Qwen, Kimi, or GLM through OpenRouter.

Body:

Two things get bundled together in your head when you use Claude Code and they aren't the same thing: the model, and the harness (the agent loop, tool definitions, context management, permissions, subagents). When people say Claude Code is good they're mostly praising the harness. And the harness doesn't care which model is underneath.

Claude Code doesn't hardcode `api.anthropic.com`. It sends Anthropic-shaped requests to whatever `ANTHROPIC_BASE_URL` points at, because Anthropic needed that for Bedrock and Vertex. OpenRouter speaks the same wire format in front of ~400 models, so:

```zsh
_claudeq_env() {
  source ~/.config/openrouter.env          # OPENROUTER_API_KEY, chmod 600
  export ANTHROPIC_BASE_URL="https://openrouter.ai/api"
  export ANTHROPIC_AUTH_TOKEN="$OPENROUTER_API_KEY"
  export ANTHROPIC_API_KEY=                # blank on purpose, see below
  export ANTHROPIC_DEFAULT_HAIKU_MODEL="qwen/qwen3.5-35b-a3b"
}

claudeor() {
  local model="${1:?usage: claudeor <openrouter-model-slug>}"; shift
  (
    _claudeq_env
    export ANTHROPIC_DEFAULT_SONNET_MODEL="$model"
    export ANTHROPIC_DEFAULT_OPUS_MODEL="$model"
    claude --dangerously-skip-permissions --model "$model" "$@"
  )
}
```

The `( ... )` subshell is the whole design: every export dies when the command exits, so your normal `claude` in the same terminal still hits Anthropic. `ANTHROPIC_AUTH_TOKEN` becomes `Authorization: Bearer` (what OpenRouter wants); blanking `ANTHROPIC_API_KEY` is load-bearing because it sits first in the credential order and would otherwise send an Anthropic key to OpenRouter.

Two things that bit me:

**It's four slots, not one.** Main (`--model`), the Haiku slot (what background work and quick subagents reach for instead of burning your main model), and the Sonnet and Opus tiers for `/model` and pinned subagents. Treat it as a routing table: strong model on main, cheap model on the fan-out.

**Leave a tier blank and you get silently billed full rate.** A bare Anthropic model id goes upstream, OpenRouter answers 200, normalizes it to `anthropic/claude-sonnet-5`, and charges you Sonnet prices inside the session you set up to be cheap. Every slot needs a value. Verify with a request that would be obviously wrong on the model you didn't pick.

The honest limitation: `permission-mode auto` stops working because that classifier needs a Claude model. So you're running skip-permissions against a model you know less well. Put hooks under it first.

Full write-up with the complete shell block, credential handling, and how to pick a model: https://agentic-engineer.com/blog/2026-09-21-run-claude-code-any-model-openrouter
