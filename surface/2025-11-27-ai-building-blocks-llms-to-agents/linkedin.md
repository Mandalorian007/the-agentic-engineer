Programming has always been deterministic—until now.

For decades, we've been "if/else bots," stringing business logic together. But some business requirements don't want deterministic. They want creative.

I've been exploring how to think about AI as composable building blocks, and I want to share three fundamental layers that every engineer should understand:

1. Basic LLM Calls: Text in, text out. Simple OpenAI API calls that can add dynamic, creative content anywhere in your app. Want your form fields to be less boring? Hook up a cached LLM call that refreshes hourly.

2. Structured Outputs with Zod: This is where it gets powerful. Use JSON schemas to get the LLM to return data in specific formats. It's non-deterministic but structured. This 15-line pattern is the foundation of tool chains, MCPs, and all modern AI workflows.

3. Full Agent Workflows: Script Claude Code CLI, run complex workflows, and get structured results back. Imagine iterating MVPs by scripting agent workflows—"show me version 1, then version 2, then version 3" based on your feedback.

The key insight: you don't always need the full power of agents. Sometimes a simple LLM call solves your problem. Sometimes you need structured outputs. Sometimes you need the full agent.

These small components can be hooked together into much bigger ideas. None of these are large, crazy things. They all fit in a utility file.

The future of programming isn't just deterministic logic. It's composing intelligent, creative building blocks into systems that can surprise and delight.

Full breakdown with code examples:
