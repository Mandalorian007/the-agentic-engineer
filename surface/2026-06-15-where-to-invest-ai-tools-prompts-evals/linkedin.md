The model isn't the moat. Tools, prompt workflows, and an eval harness are. The vendor sits underneath all three.

Every AI provider is racing each other. First on knowledge, then reasoning, now agentics. Most companies are pouring AI budget directly into picking the racer. That bet doesn't survive the next quarter. The leader shifts, pricing changes, a better framework appears, and anything wired specifically to one vendor becomes the thing nobody wants to rip out.

I run a three-layer frame on every engagement instead. All three layers are vendor-agnostic by design.

1. The tool layer. The specific actions a person already takes inside the company, packaged so a model can take them instead. Searching the warehouse. Pulling a customer by an internal ID format. Running a deploy with the safety checks attached. Packaged as MCPs, CLIs, or APIs the agent can hit. Portable across every vendor that ever ships.

2. The prompt layer. Workflows that compose tools into how the work actually flows. Normalize the user's terminology before searching. Branch into parallel discovery paths. Reconcile what came back. Written against generic primitives (skills, sub-agents, hooks, marketplace plugins), the workflows run on whatever platform you point them at.

3. The eval layer. A rubric and a representative input set that tells you what percent of the time the system gets the right answer. AI agents are not deterministic. "We tested it once" is not a measurement. With an eval suite, every change becomes measurable: swap a model, tweak a prompt, add a tool, re-run, see if the number moved. Voting techniques (run five agents, require three to agree) drive a 60% single-shot success rate up considerably, but only once you can measure it.

The teams that build these three layers compound. The teams that don't are renting capability from someone else's roadmap.

Priority order question for other platform leads: tools first, evals first, or workflows first? Curious how the sequencing has played out in your rollouts.

Full breakdown:
