# Managed Agent Platforms — Research & Comparison Foundation

## 1. Platform profiles

### 1.1 Anthropic — Claude Managed Agents

**Products & status**
- **Claude Managed Agents** — Beta (GA-default access; beta header `managed-agents-2026-04-01`; engineering post Apr 08, 2026). Anthropic's hosted runtime/meta-harness running Claude as a long-horizon async autonomous agent.
- **Claude Agent SDK** — GA (Python, TypeScript). Bring-your-own-runtime complement.
- **Dreams (memory consolidation)** — Research Preview (`dreaming-2026-04-21`). Async job that reads a memory store + 1-100 past transcripts and emits a deduplicated/reorganized store.
- **MCP tunnels** — Research Preview. Lets Anthropic's control plane reach private MCP servers in your network.
- **Claude Managed Agents on Claude Platform on AWS** — Available; billed in Claude Consumption Units (some endpoints unavailable).

**How it works (building blocks)**
Hosted, async, long-horizon. Anthropic runs the agent loop ("brain" = Claude + harness) on its control plane. Sessions are stateful and long-running (minutes to hours), resume cleanly after pauses, and persist conversation history + sandbox state + outputs server-side. You define an **Agent** once (model, system prompt, tools, MCP, skills) and reference it across **Sessions**. **Outcome-oriented mode** elevates a session to "work": you define a result + markdown rubric, and the harness auto-provisions a separate-context grader that scores the artifact and feeds revisions back (default 3, max 20 iterations). Architecturally a "meta-harness" that decouples brain / hands (sandbox) / session — decoupling cut p50 TTFT ~60% and p95 >90%.

Containers: two modes. **Cloud (default)** — Anthropic-managed isolated fresh Linux container per session (sessions do NOT share filesystem state); pre-install packages cached across sessions sharing an environment. **Self-hosted sandbox** — orchestration stays on Anthropic but tool execution/filesystem/egress run on YOUR infra via a worker polling a work queue (off-the-shelf workers for Cloudflare, Daytona, Modal, Vercel Sandbox). Sandbox paths: `/workspace`, `/mnt/session/outputs`, `/mnt/memory/`.

Multiagent is first-class: a coordinator delegates to a roster (max 20 unique agents, `self` allowed), each agent context-isolated with its own model/prompt/tools but sharing the same sandbox/vault. Coordinator delegates one level deep only; max 25 concurrent threads.

Memory has two layers: per-session (stateful sandbox + durable server-side event log queried via `getEvents`/positional slices) and cross-session **Memory stores** (workspace-scoped text-document collections mounted as a directory; up to 8 per session, attached only at creation; each memory ≤100 kB/~25k tokens, ≤2,000 memories per store; every write makes an immutable version retained ~30 days). Dreams consolidate stores.

**Unique angles**
- "Decouple the brain from the hands" meta-harness with stable interfaces, explicitly modeled on OS virtualization, so the harness can be swapped as models improve.
- The durable session log lives OUTSIDE Claude's context window, avoiding irreversible compaction for long-horizon tasks.
- Built-in outcome+rubric grader in a separate context window — native eval/quality loop, not a bolt-on.
- Credentials structurally unreachable from the agent's code sandbox (Git token wired into the remote at init; MCP OAuth in a Vault behind a proxy) — mitigates prompt-injection token theft by design.

**Key facts**
- Pricing: tokens at standard model rates (identical prompt-caching multipliers) + session runtime **$0.08/session-hour** metered to the millisecond, billed only while `status=running`; web search $10/1,000. Session runtime replaces Code Execution container-hour billing.
- **NOT eligible for ZDR or HIPAA BAA** (stateful, server-side retained). Self-hosted sandboxes keep data in your network.
- Org rate limits: 300 create req/min, 600 read req/min. Networking: `unrestricted` (default) vs `limited` (docs recommend `limited` least-privilege for production).

### 1.2 OpenAI — AgentKit

**Products & status**
- **AgentKit** — launched Oct 6, 2025 (umbrella suite on the Responses API).
- **Agent Builder** — Beta. Visual drag-and-drop canvas for versioned multi-agent workflows (agent/guardrail/MCP/file-search/if-else/approval nodes; preview runs, inline evals, publish).
- **ChatKit** — GA. Embeddable OpenAI-hosted chat UI iframe; backend OpenAI-hosted (published workflow) or self-hosted.
- **Connector Registry** — Beta (select API / ChatGPT Enterprise & Edu; requires Global Admin Console).
- **Agents SDK** — GA (Mar 2025; Python + TS). Code-first self-hosted counterpart.
- **Responses API (background mode + hosted tools)** — GA. `background=true` runs long async tasks with poll-able objects; hosted tools (web search, file search, code interpreter, hosted shell, computer use).
- **Sandbox agents (SandboxAgent)** — Beta. Isolated Unix-like env; client can be Unix-local, Docker, or a hosted provider (BYO-provider).
- **Evals (expanded)** — GA. Datasets, trace grading, automated prompt optimization.
- **Workflows API + agent deployment to ChatGPT** — announced "coming soon" Oct 2025; NOT clearly confirmed GA as a discrete product as of June 2026.

**How it works**
Two tracks. **Hosted**: publish an Agent Builder workflow and OpenAI runs the chat server, stores messages/attachments, hosts the ChatKit iframe, executes on OpenAI infra. **Async**: Responses API background mode for long tasks (Codex/Deep Research pattern), data stored ~10 min for polling. **Code-first (self-hosted)**: Agents SDK where your server owns orchestration, persistence, scaling. Multi-agent via Agent Builder composition and SDK handoffs. Sandbox agents (beta) provide a managed-or-BYO sandbox; docs stress separating harness (control plane) from sandbox compute.

**Unique angles**
- Visual-first hosted authoring (drag-and-drop, versioning, inline evals, guardrail nodes, one-click publish) lets non-engineers co-build; Ramp cited 70% faster iteration.
- Tight UI-to-runtime bundle via ChatKit — OpenAI hosts the iframe AND the published-workflow backend.
- Built on the same Responses API stack that powers ChatGPT, with first-party hosted tools.

**Key facts**
- All AgentKit tools **included with standard API model pricing** — no separate fee. You pay tokens + tool-specific charges.
- Background mode is **NOT ZDR-compatible** (~10-min retention); Modified Abuse Monitoring projects can use it.
- Open-source **Guardrails** (Python/JS) masks/flags PII, detects jailbreaks; runs standalone or in Agent Builder.
- **No first-party cron/scheduler** surfaced; **no dedicated Terraform/IaC provider found**.

### 1.3 Google Cloud — Gemini Enterprise Agent Platform (formerly Vertex AI)

**Products & status** (rebranded/consolidated at Cloud Next '26, Apr 22, 2026; all former Vertex AI agent services now ship exclusively here)
- **Agent Runtime** (formerly Vertex AI Agent Engine) — GA. Serverless hosted runtime; now supports long-running agents holding state for days.
- **Agent Development Kit (ADK)** — GA / open source. Code-first single/multi-agent framework; deploys to Agent Runtime or self-host on Cloud Run/GKE.
- **Agent Memory Bank** — GA (metered billing began Jan 28, 2026). Auto-curated long-term memory with Memory Profiles.
- **Agent Sessions** — GA. Short-term conversation state; Custom Session IDs.
- **Agent Sandbox / Code Execution** — GA. Hardened sandbox + Computer Use; sub-second creation, state up to 14-day TTL.
- **Agent Studio** — GA. Low-code visual builder, exports to ADK.
- **Agent Garden** — GA. Catalog of prebuilt templates.
- **Agent Gateway / Registry / Identity** — GA governance suite (cryptographic per-agent identity, approved-tool registry, Model Armor).
- **Gemini Enterprise app** (formerly Agentspace) — GA. Employee-facing front door.

**How it works**
Hosted, fully managed serverless runtime (no BYO infra required). Sync request/response AND async via Batch & Event-driven agents (BigQuery + Pub/Sub triggered). Re-engineered runtime: sub-second cold starts, autonomous agents holding state for days, bidirectional WebSocket streaming. Five deploy paths (in-memory object, source files, Dockerfile, Artifact Registry image, Developer Connect Git). Code Execution sandbox is decoupled — usable even by agents running off-platform; **no network access, limited filesystem, cannot install custom libraries**. Multi-agent via ADK graph-based sub-agent networks; supports generative AND deterministic orchestration; native A2A.

**Unique angles**
- Deepest enterprise governance: per-agent cryptographic Identity with auditable trail, Registry, Gateway, Model Armor, Security Command Center threat/anomaly detection — designed to govern third-party agents too.
- Framework-agnostic managed runtime: hosts ADK, LangChain, LangGraph, LlamaIndex, AG2, A2A, and custom agents.
- 200+ models in Model Garden including third-party Anthropic Claude, under PSC/VPC controls.

**Key facts**
- Pricing: **$0.0864/vCPU-hour + $0.0090/GiB-hour**, billed to the nearest second; idle not billed. Free tier 50 vCPU-hours + 100 GiB-hours/mo. Sessions/Memory Bank/Code Execution separately metered since Jan 28, 2026. Model tokens separate.
- Code Execution: file I/O up to 100 MB/request, 14-day TTL, no network.
- Supports A2A, MCP (incl. managed remote MCP server), and AP2 (Agent Payments Protocol).

### 1.4 AWS — Amazon Bedrock AgentCore

**Products & status**
- **Amazon Bedrock AgentCore** — GA (Oct 13, 2025). Flagship managed platform; framework- and model-agnostic modular suite.
- **AgentCore Runtime** — GA. Serverless hosting in per-session microVMs; real-time + async up to 8 hours.
- **AgentCore Harness** — Available. Managed agent loop via one API call; each session isolated microVM with filesystem/shell (BYO container optional).
- **Amazon Bedrock Agents** — GA, older higher-level service; still available, not deprecated, but AgentCore positioned for new builds.
- **Strands Agents SDK** — open-source local dev path; deploys to AgentCore (one of several supported frameworks).

**How it works**
Hosted, serverless, any-framework/any-model. Both synchronous and async workloads up to an **8-hour** execution window per session. `InvokeAgentRuntime` API supports sync/async; persistent filesystems survive stop/resume. Each session runs in a dedicated microVM (isolated CPU/memory/filesystem) terminated and memory-sanitized at end ("deterministic security"). Separate managed sandboxes: Code Interpreter and Browser (Playwright/BrowserUse). Multi-agent via MCP or A2A; shared memory stores. **AgentCore Gateway** converts APIs/Lambda/services into MCP tools. **AgentCore Policy** uses Cedar (or natural language) to intercept every tool call before execution.

**Unique angles**
- True "any framework, any model" — runs LangGraph, CrewAI, LlamaIndex, Strands, OpenAI Agents SDK, Google ADK, Claude Agent SDK, or custom; hosts YOUR agent rather than a proprietary abstraction.
- Modular a-la-carte: 12+ loosely coupled services (Runtime, Harness, Memory, Gateway, Identity, Code Interpreter, Browser, Observability, Evaluations, Policy, Registry, Payments) usable independently.
- Per-session microVM isolation with full memory sanitization; access policies verified by automated reasoning (same tech behind IAM/S3). **AgentCore Payments** via x402 protocol.

**Key facts**
- Pricing: **~$0.0895/vCPU-hour + ~$0.00945/GB-hour**, per-second (1s min, 128 MB floor); CPU typically not billed during LLM/IO wait. Gateway ~$0.005/1,000 invocations.
- Per-session ceiling 2 vCPU / 8 GB. GA added VPC, PrivateLink, CloudFormation, tagging; 9 Regions at launch.
- IaC: CloudFormation, CDK (hotswap), Terraform. Observability emits OTEL, powered by CloudWatch.

### 1.5 LangChain — LangSmith Deployment / LangGraph / LangSmith

**Products & status**
- **LangSmith Deployment** (formerly LangGraph Platform) — GA (renamed Oct 2025; Platform GA May 2025). Framework-agnostic workflow-orchestration runtime ("Agent Server"); deploy to managed Cloud (AWS/GCP), standalone Docker/K8s, or fully self-hosted.
- **Managed Deep Agents** — Private preview (waitlist; US Cloud only; routes `/v1/deepagents`). Hosted deep-agents harness without standing up an Agent Server.
- **LangSmith Sandboxes** — Available. Isolated code-exec/filesystem with snapshots, auth proxy for credential injection, per-member permissions.
- **LangSmith Fleet** (formerly Agent Builder) — GA. No-code fleet management.
- **LangSmith Observability & Evaluation** — GA.
- **LangGraph (OSS)** — GA. The artifact you deploy (also Strands/CrewAI/Google ADK via Functional API).

**How it works**
Async, durable, long-running. Agent Server exposes **assistants** (config) + **threads** (state) + **runs** (workloads). Clients enqueue runs onto a durable task queue; workers execute and checkpoint, so interruptions resume from the last checkpoint. Durability modes: `async` (default, checkpoint per step) vs `exit`. Same runtime/APIs across Cloud, standalone, self-hosted. PostgreSQL backs three data types (core resource data, checkpoints = short-term memory, Store = long-term memory); Redis only ephemeral signaling. Multi-agent via LangGraph graphs + RemoteGraph over MCP/A2A. Cron jobs (UTC, require a Postgres checkpointer).

**Unique angles**
- Observability/eval/deployment unified under one brand (LangSmith) — tracing is the default substrate, not a bolt-on.
- Full deployment-spectrum portability with identical APIs: managed Cloud, BYO standalone (no control plane), fully self-hosted in your VPC (Enterprise, incl. airgapped).
- Durable, queue-based execution with checkpoint-resume and a strict 1-run-per-thread guarantee.

**Key facts**
- Pricing: Developer $0/seat; Plus $39/seat/mo; Enterprise custom. Production standby $0.0036/min, Dev standby $0.0007/min; additional deployment runs $0.005/run; Fleet runs $0.05/run; Engine $1.50/LCU; sandbox CPU $0.0576/vCPU-hr, memory $0.0185/GiB-hr.
- Managed Deep Agents: US only, no self-hosted/Hybrid, free workspaces capped at 1 (HTTP 409 over).
- Each queue worker defaults to 10 concurrent runs; autoscale up to 10 containers; 30-min scale-down cooldown.

### 1.6 Microsoft — Foundry Agent Service (formerly Azure AI Foundry Agent Service)

**Products & status**
- **Foundry Agent Service (Agent Runtime)** — GA (since June 2025). Overarching managed platform.
- **Prompt agents** — GA. No-code/config-only (instructions + model + tools).
- **Workflow agents** — Preview. Declarative multi-agent orchestration (portal or YAML in VS Code); branching, HITL, sequential/group-chat.
- **Hosted agents** — Public preview. Code-based (your framework, packaged as a container) on Foundry-managed per-session VM-isolated Micro VM sandboxes.
- **Microsoft Agent Framework** — GA (v1.0; OSS .NET + Python). Successor to Semantic Kernel + AutoGen.

**How it works**
Managed cloud runtime hosts prompt and Hosted agents. Hosted agents are async/session-based: the Responses protocol offers `background: true` with platform-managed polling/cancellation. **Sessions persist up to 30 days with a 15-minute idle timeout** — compute deprovisioned on idle, state restored on resume (scale-to-zero + stateful resume). Hosted agents: package as a container to Azure Container Registry, Foundry runs each session in a per-session VM-isolated Micro VM. **Fixed sandbox sizes only**: 0.5 vCPU/1 GiB, 1 vCPU/2 GiB, or 2 vCPU/4 GiB. Persistent `$HOME` and `/files` survive idle/resume. Python and C# only. Three agent-mesh layers: Connected Agents (point-to-point), Workflow agents, and code-based Hosted agents exposing/consuming A2A. Four combinable protocols: Responses, Invocations, Activity, A2A.

**Unique angles**
- Deeply embedded in Microsoft/Azure: Entra agent identity per agent, RBAC, ACR, App Insights, Cosmos DB BYO state, one-click publish to Teams / M365 Copilot / Entra Agent Registry.
- Three-tier model (no-code Prompt → declarative Workflow → code Hosted) within one platform.
- Per-session Micro VM with scale-to-zero AND stateful resume; versioned "Toolbox" exposes a curated tool set as a single MCP endpoint.

**Key facts**
- Default quota: **50 max concurrent active sessions per subscription per region** (adjustable). Billing scales with cpu+memory across all active sessions — oversizing multiplies cost by concurrency.
- No charge to create/run prompt and workflow agents; Hosted billed by vCPU-hour + GiB-hour during active sessions (specific $ region-dependent, shown N/A pending selection). Tool meters: File Search $0.11/GB/day (1 GB free), Code Interpreter $0.033/session, Web/Custom Search $14/1,000.
- IaC via azd Foundry agent extension (azure.yaml + Bicep + agent.yaml); weighted traffic split for canary/blue-green. ACR must remain publicly reachable in preview even with BYO VNet.

### 1.7 Cloudflare — Agents SDK on Durable Objects / Workers

**Products & status**
- **Cloudflare Agents SDK** — GA (Workers/Durable Objects; deployed via Wrangler, Workers Paid).
- **Project Think** — Experimental preview (announced 2026-04-15; not GA). Durable execution with fibers, sub-agents (Facets), tree-structured sessions, sandboxed code exec.
- **Cloudflare Sandboxes** — Available. Isolated Linux containers (`@cloudflare/sandbox`).
- **Dynamic Workers** — Open beta. Runtime-spawned fresh V8 isolates (~100x faster boot, up to 100x more memory-efficient than containers), zero ambient authority.
- **AI Gateway** — GA. Unified inference + observability (logs, caching, rate limiting, fallback, evals).
- **Cloudflare Workflows** — Available. Durable guaranteed-execution engine (minutes to weeks).

**How it works**
Fully managed on Cloudflare's global network. Each agent is a **Durable Object** (actor model) with its own SQLite DB, WebSockets, scheduling — wakes on event (HTTP, WebSocket, scheduled alarm, inbound email), works, then **hibernates consuming ZERO compute when idle**. Single-threaded per instance with gates and `blockConcurrencyWhile()`. Project Think adds durable execution (`runFiber`/`stash`/`onFiberRecovered`) for crash recovery and `keepAlive()`. Container spectrum ("execution ladder": workspace, isolate, npm, browser, sandbox). Sub-agents via Facets (isolated child DOs over typed RPC). First-class MCP via `McpAgent`; **Code Mode** has the LLM write one program run in a sandboxed Dynamic Worker (Cloudflare's API MCP cut ~1.17M tokens to ~1,000).

**Unique angles**
- Actor-model runtime: one DO per agent with built-in identity, SQLite, routing — eliminates the external DB/load balancer/sticky sessions other platforms force you to build.
- Zero-cost hibernation economics: "10,000 agents @1% active ≈ 100 active" makes one-agent-per-customer/task/email-thread viable at tens-of-millions scale.
- Capability-first security: Dynamic Workers start with no ambient authority (`globalOutbound: null`); capabilities granted binding-by-binding.

**Key facts**
- Pricing built on Workers Paid ($5/mo min): DO compute 1M req/mo then $0.15/M, 400,000 GB-s/mo then $12.50/M GB-s; SQLite storage 5 GB-mo then $0.20/GB-mo. Zero compute while hibernated.
- IaC via Wrangler (`wrangler.jsonc`); Terraform for surrounding resources. Observability via AI Gateway + Workers Automatic Tracing (OTLP export).

### 1.8 Vercel — Workflows / WDK + AI SDK + Vercel Sandbox

**Products & status**
- **Vercel Workflows** — GA (Apr 16, 2026; beta Oct 2025). Managed durable-execution platform for long-running resumable apps/agents in JS/TS (Python beta).
- **Workflow Development Kit (WDK)** — open source; the `use workflow`/`use step` directives; portable via "Worlds" (WDK / "workflow 5" line described as beta, no GA timeline).
- **Vercel Sandbox** — GA (Jan 30, 2026). Ephemeral Firecracker microVMs ("execution layer for agents").
- **Vercel AI SDK (Agent abstraction)** — GA; Agent in AI SDK 5; AI SDK 6 adds Agent interface + ToolLoopAgent. Self-hosted/BYO-runtime SDK.
- **Claude Managed Agent on Vercel** — reference architecture (guide updated May 15, 2026), NOT a Vercel-native managed-agent product.

**How it works**
Async, durable, not one-shot. Workflows are stateful functions that pause/resume across minutes to months via deterministic event-sourced replay, surviving deploys/crashes. Hosted: Vercel Functions execute workflow/step code, Vercel Queues enqueue/route, managed persistence stores state + event logs. BYO-runtime via WDK "Worlds." **Vercel does NOT sell its own managed agent loop** — it provides durable orchestration + Sandbox + AI SDK, and pairs with third-party managed agent runtimes (e.g., Anthropic Claude Managed Agents) or self-hosted AI SDK loops. The workflow run itself doubles as the event log/durable stream (`getReadable`/`getWritable` + SSE). Scheduled triggers via Vercel Cron Jobs (production only). **No Vercel-native multi-agent orchestrator** (child workflows; multi-agent delegated to Anthropic in the reference pattern).

**Unique angles**
- Durability as a language-level primitive: two directives turn ordinary async TS/JS into crash-safe resumable workflows — no YAML/state machines/DSL.
- Framework-defined infrastructure: Vercel auto-detects durable functions and dynamically provisions queues/persistence/routing.
- Separate best-in-class isolation layer: Vercel Sandbox (Firecracker microVMs, sub-second starts, Active CPU pricing).

**Key facts**
- Workflow pricing: Events $20/1M (50k free Hobby); Data Written $0.50/GB (1 GB free); Data Retained $0.50/GB-mo. A normal step = 3 events. Run limits: 25,000 events/run, 10,000 steps/run; "Maximum run/sleep duration: No limit." Retention after completion: Hobby 1 day, Pro 7, Enterprise 30.
- Sandbox: Pro Active CPU $0.128/vCPU-hr + memory $0.0212/GB-hr; up to 8 vCPU / 2 GB RAM per vCPU; 5-min default session, up to 5 hours Pro/Enterprise; CPU not billed during I/O/inference waits.
- **No dedicated Vercel-native eval framework found.** Egress/least-privilege specifics for Sandbox not detailed — partial.

### 1.9 Temporal — Temporal Cloud

**Products & status**
- **Temporal Cloud** — GA. Managed multi-tenant durable-execution backend (Temporal Service / control plane). **NOT a hosted agent sandbox runtime** — you still run your own workers/agent code in your environment.
- **OpenAI Agents SDK + Temporal integration (Python)** — GA (Mar 23, 2026; preview Jul 30, 2025). `OpenAIAgentsPlugin`; `activity_as_tool`.
- **Temporal AI SDKs / framework integrations** (Pydantic AI, Vercel AI SDK, Google ADK, Mastra, LangChain/Langfuse, Braintrust) — GA/varies. Self-hosted SDK pattern.
- **Durable MCP tools pattern** — documented GA building block.

**How it works**
Async, long-running durable-execution orchestration — not a hosted-sandbox model. Agents are written as Temporal **Workflows** (deterministic orchestration) with non-deterministic work (LLM/tool calls) in **Activities**. Workflows hold state for long periods (docs say even years), support HITL via Signals/Updates, replay/resume after crashes. **CRITICAL: Temporal Cloud never runs your agent code** — you host workers in your own environment; workers poll Temporal (outbound only); Temporal never connects into your environment. **BYO container/compute — no managed sandbox.** Tools wired as Activities. Triggers via SDK client, Signals/Updates, Schedules (cron-like), Nexus.

**Unique angles**
- Not a hosted runtime — it is the durable-execution orchestration LAYER. You keep full ownership of agent code, model keys, and compute. The opposite of "managed sandbox" platforms.
- Durable Execution as the core primitive: state/history/loop progress auto-persisted as replayable event history; agents resume exactly where they left off without you building state machines.
- Security for regulated/enterprise: Temporal "never sees your code or sensitive data" (Data Converter encrypts before leaving your env; self-hosted Codec Server); outbound-only workers; SOC 2 Type II, HIPAA, GDPR.

**Key facts**
- Pricing on **Actions** (2025 tiered): first 5M at $50/M, scaling to $25/M (100-200M), Contact Sales over 200M; **Actions during Replay NOT billed**. Free tier exists. You separately pay worker compute + LLM usage.
- Production proof: Replit migrated its coding-agent control plane to Temporal; Retool built Agents on it; customers include OpenAI, Snap, Coinbase, Netflix, Cloudflare, Datadog.
- IaC: Terraform provider, `tcld` CLI for namespaces/access. No console click-ops agent builder. **PCI not confirmed.**

### 1.10 CrewAI — AMP (Agent Management Platform / Enterprise)

**Products & status**
- **CrewAI AMP** — GA (free tier + custom Enterprise). Managed control plane for deploying/triggering/monitoring/governing crews and flows.
- **Automations (deployed crews/flows)** — GA. Each becomes an HTTPS REST endpoint (`/inputs`, `/kickoff`, `/status/{kickoff_id}`) with bearer token.
- **Crew Studio** — GA. No-code/low-code builder.
- **A2A on AMP** — Early release (v0.2/v0.3). Auto-provisions distributed state, multi-scheme auth, agent cards, crew-level + per-agent JSON-RPC endpoints.
- **AMP Factory** — Enterprise. Run AMP on customer infra / dedicated VPC.
- **CrewAI OSS framework** — GA. The authoring layer AMP deploys.

**How it works**
Hosted request/response automation runtime (polling/webhook completion, not long-lived persistent sessions). Author a Crew (`run()`) or Flow (`kickoff()`) in the OSS SDK, deploy to CrewAI-managed infra (or customer infra via Factory). `/kickoff` returns a `kickoff_id` you poll. Platform builds from your repo/ZIP using `uv.lock` + `pyproject.toml [tool.crewai]` — **no BYO Docker for the standard managed path**. Multi-agent core: sequential or hierarchical process (manager_llm/manager_agent delegates to workers); A2A across deployments. Native event-based **Automation Triggers** listen to Gmail/Calendar/Drive/Outlook/Teams/SharePoint/HubSpot/Salesforce/Slack/Stripe/JIRA events.

**Unique angles**
- "Bring your existing SDK code" continuity — commit `uv.lock`, the platform builds and hosts it.
- Native event-based business-app triggers as a first-class feature (toggle on/off per deployment).
- Bidirectional MCP: connect external custom MCP servers AND export any deployed crew as an MCP server or React/UI component.
- Rotation-aware, credential-free secrets via Workload Identity/OIDC to AWS/Azure/GCP (secrets minted per-execution; rotation propagates without redeploy).

**Key facts**
- Pricing: Free = 50 workflow executions/mo, CrewAI cloud only; Enterprise = Custom (connectors, private infra/dedicated VPC, 50 dev hours/mo). No public per-execution/seat rate.
- Marketing: "Used by 63% of the Fortune 500."
- Guardrails: Hallucination Guardrail + PII Redaction for Traces; OTEL export. **SOC 2/HIPAA status not confirmed in first-party docs.** Durable cross-run persistent state beyond SDK memory + execution history not separately documented. Native clock-based cron inside AMP not clearly documented (pattern: external scheduler POSTs to `/kickoff`).

### 1.11 Letta — Letta Cloud / Letta Code (formerly MemGPT)

**Products & status**
- **Letta Cloud / API Platform** (GA) — hosted multi-tenant stateful-agent server; loop + server-side tools + Postgres-backed memory run on Letta infra.
- **Letta Code** (GA, 2026 flagship) — open-source, model-agnostic agent harness; runs client-side, tightly coupled to managed cloud (Constellation).
- **Constellation** (GA) — managed state / LLM gateway / remote environments behind Letta Code. **ADE** (GA) visual dev/debug. **Letta Evals** (GA, OSS). **Conversations API** (GA, Jan 2026).

**⚠️ Currency:** A strategic pivot (Mar 16, 2026) refocused Letta on Letta Code and **deprecated much of the original MemGPT-style server platform** (server-side MCP, memory tools, filesystem, templates, sleep-time agents, tool rules — immediate to mid-April 2026). Evaluate against the current Letta Code / Constellation direction, not 2024-25 MemGPT docs.

**How it works** — Split hosting: server-side loop (Cloud API, state in Postgres) vs client-side harness (Letta Code) with managed state via Constellation. Memory-first: core memory blocks + archival memory, superseding into **Context Repositories ("MemFS")** — git-backed memory files the agent edits with bash, enabling versioned, branchable "memory swarms" via worktrees. Sleep-time compute for background consolidation. Subagents + skills are the orchestration model. Server-side custom tools run in an isolated sandbox (E2B Firecracker microVMs when self-hosted).

**Unique angles** — (1) Memory-first thesis with git-native memory (no comparable layer elsewhere). (2) Aggressively model-agnostic + OSS as a wedge against closed-lab harnesses; agents designed to outlive any model (Agent File .af portability). (3) Research-led continual learning.

**Key facts** — API pricing $20/mo + $0.10/active agent/mo + $0.00015/sec server tool CPU + PAYG tokens; BYOK all plans. #1 model-agnostic OSS agent on Terminal-Bench. Compliance (SOC2/HIPAA/ZDR): not public — request from sales.

### 1.12 Mastra — Mastra Platform / Cloud

**Products & status** (Mastra Platform GA'd Apr 9, 2026, on the Apache-2.0 TypeScript framework)
- **Mastra Server** (GA) — deploys agents/workflows/tools as a production REST API (OpenAPI).
- **Mastra Studio** (GA) — cloud control plane: evals, logs, traces, datasets, experiments, no-code Agent Editor, RBAC.
- **Memory Gateway** (GA) — standalone managed long-term "Observational Memory" usable from any framework/language.

**How it works** — `mastra build` → self-contained Hono/Node server; `mastra server deploy` builds a **Docker image deployed to Railway** behind a stable URL with autoscaling (ephemeral FS → remote DB required). Same artifact self-hostable anywhere or on-prem/VPC (Enterprise). HTTP timeout 3 min default; durable resumable workflows + background task manager for long work. **A2A native by default** (@mastra/core 1.33.1) + `.network()` routing. Three-tier memory (working + semantic recall + Observational Memory). Full MCP client + server.

**Unique angles** — (1) OSS-first with a portable escape hatch: identical build artifact runs managed, self-hosted, or in-VPC. (2) Managed long-term memory sold à la carte (Memory Gateway), usable from any stack. (3) TypeScript-native (built on Vercel AI SDK by the Gatsby team) — the TS-ecosystem agent platform vs Python-centric LangChain/CrewAI.

**Key facts** — CPU-hour billing ($0.25-0.35/hr) + $100/project persistent server; memory billed separately. Observational Memory 94.87% on LongMemEval. Production users: Replit, Sanity, SoftBank, WorkOS, Elastic. SOC2 on Teams tier; VPC/on-prem on Enterprise; HIPAA/ZDR unknown.

### 1.13 Adjacent categories (not core developer build-your-own runtimes)

Per validator notes, these are managed/production-grade but fall outside the "developer platform you build agents on" comparison: **Cognition/Devin** and **Replit Agent** (vertical autonomous-coding products); **Salesforce Agentforce** (CRM/business-user-oriented). **Letta** and **Mastra** are flagged as OSS frameworks that now ship managed runtimes and merit follow-up research — they were named as additions but full structured profiles were not provided in this batch (see §6). Excluded on the high bar: Hugging Face smolagents (library only), Inngest AgentKit (orchestration layer, borderline).

## 2. What makes them the same (commonality)

Despite different brands and entry points, every platform converges on the same mental model: **separate the "brain" (the model + agent loop) from the "hands" (a sandboxed execution environment) from the "spine" (durable state/orchestration), then sell you the parts you don't want to run yourself.** Anthropic states this explicitly ("decouple the brain from the hands"); OpenAI, AWS, and Microsoft all publish near-identical "harness vs. compute" / control-plane-vs-execution-plane guidance; Temporal and Vercel sell the spine alone.

The universal building blocks recur across all nine:

- **Hosted/async runtime for long-horizon work.** Every platform supports long-running async execution that outlives a single request — Anthropic sessions (hours), AWS (8-hour window), Microsoft (30-day sessions, 15-min idle), Google (state for days), Cloudflare/Vercel/Temporal/LangChain (durable, minutes to months/years). One-shot chat is the floor, not the ceiling.
- **An isolated container/sandbox for model-generated code.** Per-session microVMs or containers are near-universal: AWS microVM-per-session with memory sanitization, Microsoft VM-isolated Micro VM, Vercel Firecracker, Google hardened sandbox, Anthropic fresh container per session, Cloudflare Sandboxes/Dynamic Workers, LangSmith Sandboxes. Temporal is the lone exception (BYO compute).
- **A sub-agent mesh.** Coordinator/sub-agent or A2A patterns appear everywhere (Anthropic coordinator roster, OpenAI handoffs, Google ADK graphs, AWS A2A, LangGraph RemoteGraph, Microsoft Connected/Workflow agents, Cloudflare Facets, CrewAI hierarchical + A2A, Temporal child workflows). Vercel is the weakest here (child workflows, no native orchestrator).
- **Two-tier memory.** Short-term per-session/thread state + long-term cross-session memory is the dominant pattern (Anthropic memory stores, Google Memory Bank + Sessions, AWS short/long-term, Microsoft managed Memory, LangChain checkpoints + Store, Cloudflare SQLite + Sessions). Temporal/Vercel persist event history but push semantic memory to BYO datastores.
- **MCP as the tool-wiring standard.** First-class MCP support is now table stakes on every platform, alongside function calling and (usually) A2A. Several also let you export your agent AS an MCP server (Cloudflare, CrewAI).
- **Least-privilege / credential isolation.** A shared theme: keep secrets out of the model's reach. Vaults/proxies (Anthropic, Vercel), auth-proxy credential injection (LangChain), capability bindings (Cloudflare), Cedar policy (AWS), Entra identity + Key Vault (Microsoft), cryptographic agent identity (Google), encrypt-before-egress (Temporal).
- **Consumption-based pricing on compute-time + tokens.** Almost everyone bills vCPU-hour + GiB-hour (or session-hour) plus separate model tokens, with idle/wait time often discounted (AWS active-CPU, Vercel/AWS no-bill-during-IO, Anthropic running-only, Cloudflare zero-while-hibernated, Temporal replay-free).
- **Triggers via API + webhooks; cron is uneven.** All are API/SDK-invokable with webhook event support, but native scheduling is inconsistent (LangChain Crons, Cloudflare alarms, Vercel Cron, Temporal Schedules have it; Anthropic, OpenAI, AWS, Microsoft, CrewAI mostly defer to external schedulers).
- **Code-first deployment with optional click-ops.** Config-as-code (CLI/SDK/IaC) is the spine; visual builders (OpenAI Agent Builder, Google Agent Studio, Microsoft portal, LangSmith Fleet, Crew Studio) are layered on top for non-engineers.

## 3. What makes each unique (differentiation)

- **Anthropic** — (1) Meta-harness designed to swap the underlying harness as models improve, with the session log living outside the context window. (2) Native outcome+rubric grader (separate-context, auto-iterating) — eval as a runtime primitive. (3) Credentials structurally unreachable from the agent's code sandbox by design.
- **OpenAI** — (1) Tightest UI-to-runtime bundle (Agent Builder → ChatKit-hosted iframe + backend) so a team ships an embedded production agent without writing frontend/backend. (2) Built on the same Responses API/hosted-tool stack as ChatGPT. (3) Visual-first authoring for non-engineers, all included in standard model pricing (no platform fee).
- **Google** — (1) Deepest enterprise governance (cryptographic per-agent identity, Registry, Gateway, Model Armor, SCC threat detection) extending to third-party agents. (2) Framework-agnostic managed runtime + 200+ models (incl. Claude) in one place. (3) Days-long autonomous agents paired with managed Memory Bank.
- **AWS** — (1) Most aggressively modular ("12+ a-la-carte services; use Gateway/Memory without Runtime"). (2) Per-session microVM with full memory sanitization + automated-reasoning-verified policies + Cedar tool-call interception. (3) AgentCore Payments (x402) for agent microtransactions.
- **LangChain** — (1) Observability/eval/deployment unified under LangSmith — tracing as default substrate. (2) Full portability with identical APIs from managed Cloud to airgapped self-host. (3) Durable queue-based checkpoint-resume with a 1-run-per-thread guarantee.
- **Microsoft** — (1) Deepest enterprise-Microsoft embedding (Entra identity, Teams/M365 Copilot publish, Cosmos BYO state). (2) Three-tier model (Prompt → Workflow → Hosted) in one platform. (3) Scale-to-zero with stateful resume (30-day sessions) — but uniquely constrained by fixed sandbox sizes and a 50-concurrent-session default quota.
- **Cloudflare** — (1) Actor-model (one Durable Object per agent) eliminates the external DB/LB/sticky-session plumbing. (2) Zero-cost hibernation economics enabling one-agent-per-customer at tens-of-millions scale. (3) Code Mode + capability-first Dynamic Workers (no ambient authority; 99.9% token reduction example).
- **Vercel** — (1) Durability as a language-level primitive (two directives, no DSL) with framework-defined infra. (2) Explicitly does NOT sell an agent loop — it sells the durable spine + Sandbox and pairs with others' runtimes. (3) Sleep-for-months with zero compute cost (priced on events/data, not wall-clock).
- **Temporal** — (1) Not a runtime at all — a managed durable-execution control plane that never sees your code/data/keys; you keep full ownership. (2) Replayable event-history durability under any framework/language. (3) Strongest regulated-enterprise security posture (encrypt-before-egress, outbound-only workers, SOC 2/HIPAA/GDPR) + proven coding-agent scale (Replit).
- **CrewAI** — (1) "Bring your existing SDK code, we build and host it" continuity. (2) Native event-based business-app triggers (Gmail/Salesforce/Slack/etc.) as a first-class feature. (3) Rotation-aware credential-free secrets via OIDC federation; self-hostable control plane (AMP Factory).
- **Letta** — (1) Memory-first architecture with git-native memory (Context Repositories / "MemFS") and "memory swarms" via worktrees — unique among all platforms. (2) Model-agnostic OSS harness positioned explicitly against closed-lab runtimes, with .af portability so agents outlive any model. (3) Research-led continual learning.
- **Mastra** — (1) Identical build artifact runs managed / self-hosted / in-VPC — a portable escape hatch most closed runtimes lack. (2) Managed long-term memory sold à la carte (Memory Gateway), usable from any framework. (3) TypeScript-native on Vercel's AI SDK — the TS-ecosystem play vs Python-centric peers.

## 4. Comparison dimensions (the table skeleton)

**Proposed discriminating dimensions (rows):**
1. Hosting model (who runs the agent loop / code)
2. Managed sandbox (per-session isolation type)
3. Max session/run duration & state-on-resume
4. Sub-agent / A2A support
5. Memory (short + long-term managed?)
6. MCP / tool wiring
7. Native scheduling (cron)
8. Credential/least-privilege model
9. Code-first / IaC story
10. Native eval/observability
11. Compute pricing unit
12. Compliance (ZDR/HIPAA/SOC2)
13. Framework/model lock-in
14. Best-fit buyer

| Platform | Hosting model | Managed sandbox | Max duration / resume | Sub-agent / A2A | Managed memory (short+long) | MCP | Native cron | Credential isolation | IaC | Native eval | Compute price unit | Compliance | Lock-in | Best-fit buyer |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **Anthropic Managed Agents** | Hosted loop (or self-host sandbox) | Fresh Linux container/session | Hours; clean resume | Coordinator roster (20), 1-deep; no A2A named | Yes (versioned memory stores) | Core (+tunnels, export n/a) | No (webhooks/BYO) | Vault + Git-token-at-init, sandbox-unreachable | API/SDK + `ant` CLI | Outcome+rubric grader (native) | $0.08/session-hr + tokens | **No ZDR/HIPAA BAA** | Claude-only | Teams wanting Anthropic's own long-horizon harness |
| **OpenAI AgentKit** | Hosted (published workflow) or SDK | Sandbox agents (beta; managed or BYO) | Async via background mode (~10-min poll retention) | Builder compose + SDK handoffs | Server-side state; SDK RunState | Strong (Connector Registry) | No (webhooks) | Guardrails + provider secrets | Builder + SDK (no Terraform found) | Expanded Evals (trace grading) | Tokens + tool charges (no platform fee) | Background mode **not ZDR** | OpenAI-centric | Product teams shipping embedded chat fast |
| **Google Gemini Ent. Agent Platform** | Hosted serverless | Hardened Code Exec (no net, 14-day TTL) | Days; long-running | ADK graphs + A2A | Yes (Sessions + Memory Bank) | Native + managed remote MCP | Via Pub/Sub + Cloud Scheduler | Cryptographic agent identity, Gateway, Model Armor, PSC/VPC | Terraform (source deploy) + Git | Simulation + Evaluation + Observability | $0.0864/vCPU-hr + $0.0090/GiB-hr | Enterprise GCP programs | Framework-agnostic (200+ models) | Regulated GCP enterprises needing governance |
| **AWS Bedrock AgentCore** | Hosted serverless | microVM/session (sanitized) | 8-hr window; FS survives stop/resume | A2A + sub-agents | Yes (short + long) | First-class (Gateway converts APIs) | No (EventBridge→Lambda pattern) | Cedar policy + IAM-grade automated reasoning | CFN/CDK/Terraform | AgentCore Evaluations (OTEL) | ~$0.0895/vCPU-hr + ~$0.00945/GB-hr | AWS compliance programs | **Any framework, any model** | AWS shops wanting modular, framework-agnostic |
| **LangChain LangSmith Deployment** | Hosted Cloud / standalone / self-host | LangSmith Sandboxes | Long-running; checkpoint-resume | LangGraph graphs + RemoteGraph (MCP/A2A) | Yes (checkpoints + Store) | Strong (static + OAuth) | Yes (Crons, UTC) | Auth-proxy injection, secrets store | langgraph CLI + GitHub | LangSmith (default tracing + Engine) | Standby/min + $0.005/run + sandbox hrs | Self-host incl. airgapped (Enterprise) | Framework-agnostic via Functional API | Teams that live in tracing/eval; portability needs |
| **Microsoft Foundry Agent Service** | Hosted (Prompt/Workflow) + Hosted (your container) | VM-isolated Micro VM (**fixed sizes**) | 30-day session, 15-min idle; stateful resume | Connected + Workflow + A2A | Yes (managed Memory) | First-class (+Toolbox MCP endpoint) | No (Logic Apps/Functions) | Entra identity + Key Vault, VNet | azd + Bicep + agent.yaml | App Insights + agent evaluators | vCPU-hr + GiB-hr (rates region-dependent, partly N/A) | Azure compliance | Framework-agnostic container (Py/C# only) | Microsoft/Azure enterprises |
| **Cloudflare Agents SDK** | Hosted (Durable Objects, edge) | Sandboxes + Dynamic Workers | Long via fibers (Project Think, experimental) | Facets (sub-agents) + MCP | Yes (SQLite + Sessions, tree) | First-class (McpAgent, Code Mode) | Yes (alarms/cron) | Capability bindings, zero ambient authority | Wrangler + Terraform | AI Gateway + Auto Tracing | DO compute + SQLite rows ($5/mo min) | unknown (not detailed) | Model-neutral (Vercel AI SDK) | Massive-scale, one-agent-per-X economics |
| **Vercel Workflows** | Hosted durable orchestration (no agent loop sold) | Vercel Sandbox (Firecracker) | No limit (months); event-sourced resume | None native (child workflows; defers to partners) | Event log persisted; semantic = BYO | Via AI SDK / partner runtime | Yes (Vercel Cron, prod only) | Sandbox isolation + vaults (egress detail partial) | FdI (directives) + vercel.json | Built-in run observability; **no native eval** | Events $20/1M + data; Sandbox CPU/mem | Retention tiers; deeper compliance unknown | No lock-in (open Worlds) | JS/TS teams wanting durable spine, BYO loop |
| **Temporal Cloud** | Managed control plane only (**you run workers**) | None (BYO compute) | Years; replay/resume | Child workflows + handoffs | Event-history persistence; semantic = BYO | Pattern (MCP-as-workflow) | Yes (Schedules) | Encrypt-before-egress, outbound-only, Codec Server | Terraform + tcld (code-first) | Web UI + replay; ecosystem evals (Langfuse/Braintrust) | Actions (replay free) + your compute | **SOC2 II, HIPAA, GDPR**; PCI unconfirmed | Framework/language-agnostic durability | Regulated orgs wanting orchestration, not ceding code |
| **CrewAI AMP** | Hosted (or AMP Factory on your infra) | Managed build-and-run (no BYO Docker) | Request/response (poll kickoff_id) | Hierarchical crew + A2A (early) | SDK memory + execution history (durable cross-run unclear) | Bidirectional (connect + export) | Not clearly native (external scheduler) | OIDC secrets (rotation-aware), RBAC | crewai CLI + GitHub auto-deploy | Traces/Metrics + guardrails; no dataset eval found | Free (50 runs/mo) / Enterprise custom | **SOC2/HIPAA unconfirmed** | CrewAI SDK | Teams already on CrewAI SDK; event-driven automations |
| **Letta (Cloud / Letta Code)** | Split: server-side loop (Cloud API) or client-side harness (Letta Code) + managed state (Constellation) | Per-tool sandbox; E2B Firecracker microVMs (self-host); no per-session microVM | No fixed max; persistent stateful, resume from Postgres/git memory | Subagents + skills (git-worktree "memory swarms"); no formal A2A | Yes — memory blocks + Context Repositories (git-backed "MemFS"); core differentiator | Supported, but server-side MCP being deprecated for client-side skills | Yes (letta cron + scheduling API) | API key + BYOK; RBAC/SSO (Ent); scoped sandbox env vars | Py/TS SDK, CLI, lettactl, Agent File (.af) portability; no Terraform | Letta Evals (OSS, CI-gating) + ADE traces | Credits: $20/mo + $0.10/agent/mo + $0.00015/sec tool CPU + PAYG tokens | **No public SOC2/HIPAA/ZDR** | Deliberately low (model-agnostic, OSS, .af); soft on Constellation | Long-lived memory-first agents that outlive models; anti-lab-lock-in |
| **Mastra (Platform)** | mastra build → Docker to Railway (managed) or self-host / VPC | None (container/deploy boundary; ephemeral FS) — app hosting, not microVM | HTTP 3-min default; background tasks 5-min; durable resumable workflows | Native A2A by default (@mastra/core 1.33.1) + .network() routing | Yes — working + semantic recall + Observational Memory (standalone Memory Gateway) | Full client + server (expose agents as MCP) | Yes (schedule.cron on workflows) | Env-var based; secrets redacted from streams; no built-in vault | CLI + Client SDK + CI-on-push; .mastra-project.json; no Terraform | First-class via Studio (traces, datasets, experiments) | CPU-hours ($0.25-0.35/hr) + $100/project persistent server; memory billed separately | SOC2 (Teams); VPC/on-prem (Ent); HIPAA/ZDR unknown | Low on models; portable artifact escapes managed runtime | TS/JS teams wanting managed REST API + memory + obs, with self-host escape |

## 5. Key insights & framings for the article

**Where the field is converging.** The architecture has standardized faster than anyone expected. Every serious platform now ships the same primitives — hosted async runtime, per-session microVM/container, two-tier memory, sub-agent mesh, MCP, least-privilege credentials, consumption pricing. MCP and A2A have won as the interop standards. The "harness vs. compute" decoupling is now industry consensus, articulated almost identically by Anthropic, OpenAI, AWS, and Microsoft. For an engineering leader, this means **the build-vs-buy question is settled in favor of buy** — and the real decision is which managed layer, not whether to hand-roll a harness.

**Where the real trade-offs are.**
1. **Who owns the code and data.** A spectrum from "Anthropic/OpenAI run the loop on their infra and retain state" (so NOT ZDR/HIPAA-eligible) → "Google/AWS/Microsoft run it inside your cloud boundary with enterprise compliance" → "Temporal never touches your code/keys at all; Vercel sells only the spine." This is the single sharpest fault line and it tracks directly to regulatory posture.
2. **Runtime philosophy.** Three camps: (a) hosted agent loop you rent (Anthropic, OpenAI, Google, AWS, Microsoft, CrewAI); (b) durable orchestration spine you bring your own loop to (Vercel, Temporal); (c) actor/edge model that re-economizes scale (Cloudflare). These are not interchangeable.
3. **Lock-in.** Model-vendor-native platforms (Anthropic = Claude-only, OpenAI = OpenAI-centric) trade flexibility for tight integration; framework-agnostic hosts (AWS, Google, LangChain, Microsoft, Temporal) hedge against model/framework churn — increasingly attractive when the model leaderboard reshuffles quarterly.
4. **Pricing models that look similar but bill differently.** Active-CPU-only (AWS, Vercel), session-hour-while-running (Anthropic), zero-while-hibernated (Cloudflare), and replay-free Actions (Temporal) produce wildly different bills for the same wait-heavy workload. Microsoft's billing-scales-with-concurrent-sessions plus fixed sandbox sizes is a notable cost trap if you oversize.

**How a leader should choose.** Start from constraints, not features: (1) compliance/data-residency requirements eliminate half the field immediately (if you need HIPAA/ZDR, Anthropic Managed Agents and OpenAI background mode are out; Temporal/Google/AWS/Microsoft are in). (2) Existing cloud commitment usually dominates — you will likely default to your hyperscaler (AWS AgentCore / Google / Microsoft) unless a capability gap forces otherwise. (3) If you already have a framework investment, AWS/LangChain/Temporal let you keep it. (4) If you want the least engineering and fastest UI-to-prod, OpenAI AgentKit. (5) If your workload is wait-heavy or one-agent-per-entity at huge scale, Cloudflare's economics are structurally different.

**Candidate framings/angles:**
- **"Everyone agrees on the architecture now — the fight is over who holds your data."** Lead with the convergence, pivot to the data-ownership/compliance fault line as the real decision axis.
- **"Brain, hands, and spine: a buyer's map to the three things you can rent separately."** Use the decoupling thesis to give readers a clean mental model, then slot each vendor into which parts they sell.
- **"The hyperscalers vs. the model vendors vs. the durability layer."** Three-camp framing that maps to how procurement actually thinks.
- **"The pricing fine print that determines your bill"** — active-CPU vs. session-hour vs. hibernation vs. Actions, with a worked wait-heavy example. Highly practical, under-covered angle.
- **"Lock-in is the real product decision"** — model-native tight integration vs. framework-agnostic hedging, timed to a market where the model leaderboard turns over quarterly.

## 6. Open questions / gaps to verify

- **Letta and Mastra**: ✅ now researched and folded in (profiles §1.11–1.12, table rows added). Remaining unknowns: Letta's public compliance posture (no SOC2/HIPAA/ZDR found) and hard run-duration limits; Mastra's HIPAA/BAA and formal ZDR status; Terraform providers for either (none found). Also note both are fast-moving — Letta's Mar 2026 pivot and Mastra's Apr 2026 GA mean re-verify at publish time.
- **Compliance confirmations**: CrewAI SOC 2 Type II / HIPAA status (not in first-party docs); Temporal PCI (not confirmed); Cloudflare Agents-specific compliance posture (not detailed); Vercel Sandbox egress/least-privilege specifics and deeper compliance (partial).
- **Anthropic**: confirm whether native A2A exists vs. only the internal coordinator/roster model; whether GA-default beta status changes before article publish.
- **OpenAI**: whether a discrete "Workflows API" / agent-deployment-to-ChatGPT ever shipped as GA (announced "coming soon" Oct 2025, unconfirmed June 2026); whether any Terraform/IaC provider now exists.
- **Microsoft**: exact $ rates for Hosted-agent vCPU-hour/GiB-hour (shown "N/A pending selection"); whether fixed sandbox sizes have expanded; whether the 50-concurrent-session default is still current.
- **CrewAI**: whether native clock-based cron now exists inside AMP; durable cross-run persistent agent state on the managed runtime beyond SDK memory + execution history; published per-tier concurrency/quota numbers and real Enterprise pricing.
- **Vercel**: whether a Vercel-native eval/scoring framework exists; whether a Vercel-native multi-agent orchestrator has shipped; the WDK / "workflow 5" GA timeline.
- **Pricing currency**: several rates carry "~" or were cited from blog/community sources (LangChain's older $0.001/node vs. current run pricing; CrewAI's unofficial ~$60K/yr estimate) — re-verify against live pricing pages at publish time.
- **Adjacent products**: decide whether Devin/Replit Agent/Agentforce get a "not in scope / adjacent category" callout box.

## Sources

**Anthropic** — platform.claude.com/docs/en/managed-agents/{overview, environments, multi-agent, memory, tools, permission-policies, vaults, webhooks, define-outcomes, dreams, self-hosted-sandboxes, skills, reference}; platform.claude.com/docs/en/about-claude/pricing; anthropic.com/engineering/managed-agents; code.claude.com/docs/en/agent-sdk/overview

**OpenAI** — openai.com/index/introducing-agentkit/; developers.openai.com/api/docs/guides/{agents, agents/sandboxes, background, agent-builder, chatkit, custom-chatkit, tools-connectors-mcp}; developers.openai.com/api/docs/pricing; developers.openai.com/api/docs/changelog; openai.github.io/openai-agents-python/tracing/; openai.github.io/openai-guardrails-python/; platform.openai.com/docs/guides/agents/connector-registry

**Google** — docs.cloud.google.com/gemini-enterprise-agent-platform/{scale, scale/runtime/deploy-an-agent, scale/sandbox/code-execution-overview, reference/use-agent-platform-mcp, overview}; cloud.google.com/blog/products/ai-machine-learning/{introducing-gemini-enterprise-agent-platform, vertex-ai-memory-bank-in-public-preview}; cloud.google.com/products/gemini-enterprise-agent-platform{, /pricing}; cloud.google.com/gemini-enterprise-agent-platform/generative-ai/pricing

**AWS** — aws.amazon.com/bedrock/agentcore/{, pricing/}; docs.aws.amazon.com/bedrock-agentcore/latest/devguide/{what-is-bedrock-agentcore, agents-tools-runtime, runtime-invoke-agent, runtime-long-run, bedrock-agentcore-limits}.html; aws.amazon.com/about-aws/whats-new/2025/10/amazon-bedrock-agentcore-available/; aws.amazon.com/blogs/aws/introducing-amazon-bedrock-agentcore-...; aws.amazon.com/blogs/machine-learning/build-ai-agents-with-amazon-bedrock-agentcore-using-aws-cloudformation/; builder.aws.com/content/.../choosing-between-managed-vs-modular-ai-agents-...

**LangChain** — docs.langchain.com/langsmith/{deployment, agent-server, deploy-managed-deep-agent, managed-deep-agents-mcp, sandboxes, cron-jobs, data-plane, fleet}; langchain.com/langsmith/deployment; langchain.com/pricing; changelog.langchain.com/announcements/{product-naming-changes-langsmith-deployment-and-langsmith-studio, agent-builder-is-now-langsmith-fleet}; langchain.com/blog/langgraph-platform-ga

**Microsoft** — learn.microsoft.com/en-us/azure/foundry/agents/{overview, concepts/hosted-agents, concepts/workflow, how-to/virtual-networks, how-to/deploy-hosted-agent, quickstarts/quickstart-hosted-agent}; learn.microsoft.com/en-us/azure/developer/azure-developer-cli/extensions/azure-ai-foundry-extension; azure.microsoft.com/en-us/pricing/details/foundry-agent-service/; devblogs.microsoft.com/foundry/{introducing-the-new-hosted-agents-..., introducing-microsoft-agent-framework-...}; github.com/microsoft/agent-framework; infoq.com/news/2025/05/azure-ai-foundry-agents-ga/

**Cloudflare** — developers.cloudflare.com/agents/{, concepts/agent-class/, concepts/long-running-agents/, api-reference/durable-execution/, api-reference/sub-agents/, api-reference/sessions/, api-reference/mcp-agent-api/, model-context-protocol/}; blog.cloudflare.com/{project-think/, code-mode/, code-mode-mcp/, dynamic-workers/, ai-gateway-is-generally-available/}; cloudflare.com/products/sandboxes/; developers.cloudflare.com/{dynamic-workers/usage/egress-control/, workers/reference/security-model/, durable-objects/platform/pricing/, workers/platform/pricing/, workers/wrangler/configuration/, ai-gateway/observability/, durable-objects/best-practices/rules-of-durable-objects/}; github.com/cloudflare/agents

**Vercel** — vercel.com/docs/workflows{, /concepts, /pricing}; vercel.com/blog/{introducing-workflow, vercel-sandbox-is-now-generally-available, a-new-programming-model-for-durable-execution, ai-sdk-6}; vercel.com/kb/guide/claude-managed-agent-vercel; vercel.com/docs/cron-jobs; workflow-sdk.dev/; ai-sdk.dev/docs/agents/loop-control; platform.claude.com/docs/en/managed-agents/overview

**Temporal** — temporal.io/{solutions/ai, ai/agentic-ai, cloud, security}; temporal.io/blog/{announcing-openai-agents-sdk-integration, temporal-cloud-pricing-update, temporal-cloud-is-now-hipaa-compliant}; temporal.io/changelog/open-ai-agents-sdk-integration-pp; docs.temporal.io/{ai-cookbook/openai-agents-sdk-python, cloud/pricing, cloud/actions, cloud/security}; github.com/temporalio/sdk-python/tree/main/temporalio/contrib/openai_agents; temporal.io/resources/case-studies/replit-...; learn.temporal.io/tutorials/ai/building-mcp-tools-with-temporal/introducing-mcp-temporal/

**CrewAI** — docs.crewai.com/en/enterprise/{introduction, guides/deploy-to-amp, features/automations, guides/automation-triggers, guides/kickoff-crew, features/a2a, features/rbac, guides/custom-mcp-server, features/secrets-manager/overview, features/secrets-manager/verify-rotation, features/pii-trace-redactions, features/hallucination-guardrail, features/sso, guides/capture_telemetry_logs}; docs.crewai.com/en/{mcp/overview, concepts/memory, concepts/processes, learn/kickoff-async}; crewai.com/{pricing, agent-management-platform}; docs.crewai.com/llms.txt


**Letta** — letta.com/blog/{our-next-phase, context-repositories, agent-memory, sleep-time-compute, letta-code, letta-evals, introducing-the-agent-development-environment}; docs.letta.com/{guides/build-with-letta/pricing, letta-code/pricing, letta-code/constellation, guides/agents/tool-execution-overview, guides/selfhosting, guides/core-concepts/tools/mcp-tools, guides/agents/scheduling, letta-code/cli-reference}; github.com/letta-ai/letta

**Mastra** — mastra.ai/blog/{announcing-mastra-platform, introducing-agent-to-agent-support, observational-memory}; mastra.ai/{pricing, models, ai-gateway, research/observational-memory}; mastra.ai/docs/{mastra-platform/server, deployment/mastra-server, agents/a2a, workflows/scheduled-workflows, reference/configuration}; mastra.ai/learn/deploy-to-mastra-platform
