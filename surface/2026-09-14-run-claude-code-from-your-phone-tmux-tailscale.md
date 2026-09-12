# Run Claude Code From Your Phone with tmux and Tailscale

URL: https://agentic-engineer.com/blog/2026-09-14-run-claude-code-from-your-phone-tmux-tailscale
Shape: tutorial
Post: website/content/posts/2026-09-14-run-claude-code-from-your-phone-tmux-tailscale.mdx

## LinkedIn

Paste as a text post. Put the URL in the first comment, not the body.

There is a product on sale right now that is a physical claw for holding your MacBook lid open, so your agents keep running while you walk away.

It is half a joke, and people are buying it, which is the interesting part. The tether is real. You start four agents, they work for the next forty minutes, and you sit next to the machine that is doing it.

I stopped doing that. My agents run on a Mac mini in a closet with no monitor and no keyboard. Four pieces make it work:

→ pmset so the machine never sleeps. A napping box kills long-running agents.
→ tmux for session persistence, so a dropped phone connection does not end the run.
→ Tailscale instead of a forwarded SSH port. A private WireGuard network between my own devices, nothing exposed publicly.
→ An SSH client on the phone, plus screen sharing for the occasional auth dialog that wants a real GUI.

The part I did not expect was how well voice input holds up. We are not fitting semicolons on lines to keep a compiler happy anymore. We are handing rough intent to an agent, and rough intent survives dictation fine.

What carries the quality is not prompt polish. It is the templates underneath. Skills, sub-agents, hooks and commands encode how good work gets done, so the instruction on top can be one sentence.

The question worth settling before you walk away is permissions. Tapping approve on a phone every ninety seconds defeats the point, so you will reach for auto permission mode or skip them entirely. If you skip them, put hooks and a tight allowlist underneath first. An unsupervised agent is a different risk profile than the same agent with you sitting in front of it.

I got rid of the desk when I moved. There is no desk in this apartment.

Curious whether others running agents off-desk have landed on a permission setup they actually trust, or are still babysitting approvals from a phone.

First comment: Full write-up with every command: https://agentic-engineer.com/blog/2026-09-14-run-claude-code-from-your-phone-tmux-tailscale

## Reddit

r/ClaudeCode. Text post, not a link post. Link goes at the end of the body.

Title: I run Claude Code from my phone. Headless Mac mini, tmux, Tailscale. Here's the setup.

Body:

Someone is selling a physical claw that holds your MacBook lid open so your agents keep running while you walk away. It's a joke, and people are buying it, because the problem is real: you kick off four agents, they work for forty minutes, and you sit next to the laptop.

I moved the agents to a Mac mini in a closet with no monitor or keyboard, and I drive them from my phone. Four pieces:

**1. A box that never sleeps.** A machine that naps is a machine your agent dies on.

```
sudo pmset -a sleep 0 displaysleep 0 disksleep 0
sudo pmset -a autorestart 1
```

**2. tmux.** SSH sessions from a phone drop constantly. tmux means the dropped connection doesn't end the run; you reattach and the agent is still going.

**3. Tailscale, not port forwarding.** A private WireGuard network between my own devices. Nothing is exposed to the internet, no dynamic DNS, no router config. `tailscale up` on both ends and the mini has a stable hostname from anywhere.

**4. An SSH client on the phone.** Blink or Termius. Plus screen sharing over the same tailnet for the occasional auth dialog that insists on a GUI.

The thing I didn't expect: voice input holds up. You're handing rough intent to an agent, not fitting semicolons on a line, and rough intent survives dictation fine. What carries the quality is the templates and hooks underneath, so the instruction on top can be one sentence.

The honest limitation: permissions. Tapping approve every ninety seconds on a phone defeats the point, so you'll end up in auto permission mode or skipping them. If you skip them, put hooks and a tight allowlist underneath first. An unsupervised agent is a different risk profile.

Full write-up with the rest of the setup (the harness install, the clients, what the loop actually feels like): https://agentic-engineer.com/blog/2026-09-14-run-claude-code-from-your-phone-tmux-tailscale
