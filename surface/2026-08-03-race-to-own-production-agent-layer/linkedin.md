I spent a week in the docs for twelve platforms that want to run your AI agents in production, expecting to map who's ahead. What I found instead: they've nearly all converged on the same architecture.

Anthropic, OpenAI, the three hyperscalers, the durability layer underneath them, the open-source projects coming up fast. Strip the branding and each one is selling some arrangement of three parts: a brain (the model and its agent loop), a pair of hands (an isolated sandbox where the model's code can run safely), and a spine (durable state that outlives a single request).

Anthropic puts it plainly: 'decouple the brain from the hands.' AWS, OpenAI, and Microsoft publish versions of the same control-plane-versus-execution-plane diagram. Temporal and Vercel skip the brain and sell the spine by itself.

Underneath, the same primitives repeat: long-running async runtimes instead of one-shot chat, a per-session microVM so untrusted code stays contained, two-tier memory, a coordinator handing work to sub-agents, least-privilege credential isolation. MCP and A2A have settled the interop question.

Two years ago we were all doing this by hand. The internal agent I work on at Airbnb runs behind CLI and API MCP servers with their own authentication and authorization, and scoping that tool surface was most of the real work. What the platforms ship now is the productionized version of what I assembled from spare parts. When twelve teams independently land on the same brain/hands/spine model, that's the shape hardening into a standard, the way containers did a decade ago.

I'm not going to tell you who wins. The architecture is settling, and that's the signal worth acting on. Build against the shared primitives: a brain you can swap, hands you can move, a spine you keep. Don't bolt your stack to whichever vendor is ahead this quarter.

How are other platform leads playing this? Committing to a runtime now, or holding to the portable primitives until the field shakes out?

Full breakdown:
