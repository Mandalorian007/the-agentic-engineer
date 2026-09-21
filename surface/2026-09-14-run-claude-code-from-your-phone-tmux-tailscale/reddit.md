Subreddit: r/ClaudeCode
Title: I run Claude Code from my phone. Headless Mac mini, tmux, Tailscale. Here's the setup.

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
