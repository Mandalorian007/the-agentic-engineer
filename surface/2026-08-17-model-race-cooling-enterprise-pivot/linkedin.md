OpenAI killed Sora to fund Codex. Anthropic shipped role-based access controls. Neither lab led the first half of 2026 with a model.

I went back through what actually shipped in the first half of this year, and almost none of it was frontier capability. Sora went dark on April 26 with the API following in September. Claude Cowork went GA in April, Claude Design a week later, and by August Cowork was in beta on web and mobile wrapped in group spend limits, OpenTelemetry observability, and admin usage analytics.

Role-based access control is not model research. It is the plumbing you build when your buyer is a procurement committee instead of a developer with a credit card.

The coding agent moved too. It used to be the headline. Now it is a component sitting underneath an enterprise offering, on both sides.

Two things are happening at once, and together they matter more than any single release:

→ Frontier upgrades stopped selling themselves. Fable 5 has not displaced Opus for everyday engineering work, and Sonnet 5 is strong enough at its price that "always use the best model" turned into a budgeting question.
→ The open-weight gap collapsed. Epoch AI now puts the average lag behind the closed frontier at about four months, down from close to a year. DeepSeek V4, Kimi K2.7 Code, Qwen 3.6 Plus, and GLM-5.2 are running in real pipelines, served through OpenAI-compatible endpoints.

My read: the labs keep moving toward enterprise deployment and solutions work, selling the expertise to run this well instead of a permanent seat in an infinite model race. That is the better business. A model lead lasts a quarter. A Fortune 100 deployment relationship lasts years.

It is also good news for everyone who wants real model choice. I have been running TabletopAdventureCreator, a generative-AI SaaS, in production since 2022, and the thing I have learned paying that inference bill every month is that the model is a line item you renegotiate, not a foundation you pour.

The harness is the part you have muscle memory for. Codex and Claude Code both speak to API-compatible endpoints, so the model behind them is a configuration value. Build on the portable pieces: MCP and open tool interfaces, plugin and skill architecture, and the expensive tier routed only to the calls that actually need judgment.

The last few years rewarded whoever picked the winning model. The next few reward whoever built so the answer does not matter much.

Where are other platform leads landing? Standardizing on one provider for the support relationship, or keeping the harness model-agnostic and eating the integration cost?

Full breakdown:
