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
