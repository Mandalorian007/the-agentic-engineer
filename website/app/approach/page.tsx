import Link from "next/link";
import type { Metadata } from "next";
import {
  ArrowRight,
  CheckCircle2,
  Target,
  Layers,
  GaugeCircle,
  Users,
  Search,
  ShieldCheck,
} from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

export const metadata: Metadata = {
  title: "Approach | The Agentic Engineer",
  description:
    "How I run an agentic developer platform engagement: discover, standardize, instrument, enable. Methodology, deliverables, and the principles behind the work.",
};

const PRINCIPLES = [
  {
    icon: Target,
    title: "Outcomes over outputs",
    body: "The deliverable isn't a deck or a Notion page — it's measurable adoption and a velocity number that moves. We agree on the metric in week one and instrument for it.",
  },
  {
    icon: Layers,
    title: "Vendor-agnostic by design",
    body: "Claude Code, Codex, Cursor, Copilot, Windsurf — these are tactical. The platform layer is strategic. I build to the meta-layer so the system survives the next tool launch.",
  },
  {
    icon: GaugeCircle,
    title: "Evaluations are the missing layer",
    body: "Most rollouts skip evals because they're hard. That's why adoption stalls. Codebase-specific evaluation harnesses are non-negotiable in every engagement I run.",
  },
  {
    icon: Search,
    title: "Your codebase is the context",
    body: "Generic agents are weak. The moat is org-specific context — internal MCP servers, packaged skills, and subagent patterns shaped to how your teams actually ship.",
  },
];

const PHASES = [
  {
    number: "01",
    title: "Discover",
    duration: "2–3 weeks",
    summary:
      "I start by understanding what you actually have — telemetry, interviews, and a frank assessment of where the platform isn't yet built.",
    activities: [
      {
        title: "Tool usage telemetry",
        body: "Which seats are active, which tools touch real codebases, where the drop-off happens between license and daily use.",
      },
      {
        title: "Developer interviews",
        body: "10–15 conversations across teams. Where are people working around the AI? Where would they pay for better tooling?",
      },
      {
        title: "Security & compliance review",
        body: "Audit logging, secrets handling, data residency, model approval policies — what's in place, what needs to be.",
      },
      {
        title: "Platform readiness assessment",
        body: "Monorepo vs. polyrepo realities, CI/CD shape, existing internal tooling, the org's appetite for shared infrastructure.",
      },
    ],
    output:
      "Written platform blueprint, prioritized roadmap, and a metrics plan you can defend to leadership.",
  },
  {
    number: "02",
    title: "Standardize",
    duration: "Weeks 3–8",
    summary:
      "I build the shared platform layer that turns scattered tool licenses into a developer platform.",
    activities: [
      {
        title: "Standardized configurations",
        body: "Settings, hooks, permission policies, and safety guardrails packaged as version-controlled defaults — applied across tools, not per-developer.",
      },
      {
        title: "Skill libraries",
        body: "Org-specific skills packaged for reuse: deployment runbooks, codebase navigation, code review patterns, incident response, internal API recipes.",
      },
      {
        title: "Internal MCP servers",
        body: "Shared context servers exposing codebase docs, runbooks, observability data, and internal API specs to every agent in the org.",
      },
      {
        title: "Subagent and orchestration patterns",
        body: "Composition patterns tuned to your topology — monorepo, microservices, frontend/backend splits, monolith carve-outs.",
      },
    ],
    output:
      "A working platform deployed to real teams. Configs, skills, and MCP servers checked into your infrastructure, not mine.",
  },
  {
    number: "03",
    title: "Instrument",
    duration: "Runs alongside phase 2",
    summary:
      "Nothing ships without evaluations. This is what separates a platform from a license bill.",
    activities: [
      {
        title: "Codebase-specific eval harnesses",
        body: "Regression tests for agents against your real code, your real PRs, your real bugs. Run on every config change.",
      },
      {
        title: "Ship/no-ship quality gates",
        body: "Automated signals that tell the platform team when an upgrade is safe to roll forward — and when to hold.",
      },
      {
        title: "Adoption telemetry",
        body: "Usage by team, by tool, by task type. Where is the platform working? Where is friction killing adoption?",
      },
      {
        title: "Cost & quality dashboards",
        body: "Token spend, eval pass rates, time-to-merge, PR throughput — the numbers leadership actually wants to see.",
      },
    ],
    output:
      "Dashboards and gates your team operates. Decisions become data-driven, not vibes-driven.",
  },
  {
    number: "04",
    title: "Enable",
    duration: "Weeks 8–12",
    summary:
      "A platform nobody uses is sunk cost. Adoption is part of the deliverable — never a hopeful side effect.",
    activities: [
      {
        title: "Team onboarding",
        body: "One-day workshop per team, recorded for replay. Hands-on patterns, not demos.",
      },
      {
        title: "Internal champions",
        body: "2–3 senior engineers trained as platform owners. They leave the engagement able to extend it without me.",
      },
      {
        title: "Operating runbooks",
        body: "Documented procedures for model upgrades, new tool integration, eval maintenance, and quarterly adoption reviews.",
      },
      {
        title: "Executive briefing",
        body: "A clean readout for leadership: what shipped, what moved, what comes next, and the case for the retainer if it makes sense.",
      },
    ],
    output:
      "Your team owns the platform. I'm available on retainer if you want it — but the engagement stands on its own.",
  },
];

const DIFFERENTIATORS = [
  {
    icon: ShieldCheck,
    title: "Hands on keyboard",
    body: "I write the configs, ship the MCP servers, and run the evals. No subcontractors, no junior associates billing my rate.",
  },
  {
    icon: Users,
    title: "Single senior point of contact",
    body: "You work directly with me from discovery through enablement. No account team layer, no handoffs between phases.",
  },
  {
    icon: Target,
    title: "Production codebases, not pilots",
    body: "The work lands in your real repos with real teams. Pilots that never ship don't move metrics.",
  },
];

export default function ApproachPage() {
  return (
    <div className="container py-12 md:py-20">
      {/* Hero */}
      <section className="max-w-4xl mx-auto text-center space-y-6">
        <Badge variant="outline" className="mx-auto">
          Methodology
        </Badge>
        <h1 className="text-4xl md:text-6xl font-bold tracking-tight">
          How I run an engagement
        </h1>
        <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
          Four phases, 10–14 weeks, fixed fee. Built like an engineer would
          build it — instrumented, evaluated, and owned by your team on
          day one.
        </p>
      </section>

      {/* Operating principles */}
      <section className="mt-24 max-w-5xl mx-auto">
        <h2 className="text-3xl font-bold mb-4">Operating principles</h2>
        <p className="text-lg text-muted-foreground mb-10">
          These aren&apos;t marketing lines. They shape every decision inside
          the engagement.
        </p>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {PRINCIPLES.map((p) => {
            const Icon = p.icon;
            return (
              <Card key={p.title}>
                <CardContent className="p-6 space-y-3">
                  <div className="flex items-center gap-3">
                    <div className="rounded-md bg-primary/10 p-2">
                      <Icon className="w-5 h-5 text-primary" />
                    </div>
                    <h3 className="text-lg font-semibold">{p.title}</h3>
                  </div>
                  <p className="text-muted-foreground leading-relaxed">
                    {p.body}
                  </p>
                </CardContent>
              </Card>
            );
          })}
        </div>
      </section>

      {/* Phases */}
      <section className="mt-24 max-w-5xl mx-auto">
        <h2 className="text-3xl font-bold mb-4">The four phases</h2>
        <p className="text-lg text-muted-foreground mb-12">
          Each phase has a clear scope, deliverables, and exit criteria. Phases
          overlap where the work calls for it — engineering, not theater.
        </p>
        <div className="space-y-10">
          {PHASES.map((phase) => (
            <Card key={phase.number} className="overflow-hidden">
              <CardContent className="p-0">
                <div className="grid grid-cols-1 lg:grid-cols-[200px_1fr]">
                  <div className="bg-muted/40 p-6 lg:p-8 flex flex-col justify-between border-b lg:border-b-0 lg:border-r">
                    <div>
                      <div className="text-5xl font-bold text-primary/60">
                        {phase.number}
                      </div>
                      <h3 className="text-2xl font-bold mt-2">
                        {phase.title}
                      </h3>
                    </div>
                    <Badge variant="secondary" className="w-fit mt-4">
                      {phase.duration}
                    </Badge>
                  </div>
                  <div className="p-6 lg:p-8 space-y-6">
                    <p className="text-lg text-muted-foreground leading-relaxed">
                      {phase.summary}
                    </p>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {phase.activities.map((a) => (
                        <div key={a.title} className="space-y-1">
                          <div className="flex items-start gap-2">
                            <CheckCircle2 className="w-4 h-4 text-primary mt-1 shrink-0" />
                            <div>
                              <div className="font-semibold text-sm">
                                {a.title}
                              </div>
                              <div className="text-sm text-muted-foreground mt-0.5">
                                {a.body}
                              </div>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                    <div className="border-t pt-4">
                      <div className="text-xs font-semibold uppercase text-muted-foreground tracking-wide mb-1">
                        Phase output
                      </div>
                      <div className="text-sm">{phase.output}</div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </section>

      {/* Differentiators */}
      <section className="mt-24 max-w-5xl mx-auto">
        <h2 className="text-3xl font-bold mb-4">What&apos;s different</h2>
        <p className="text-lg text-muted-foreground mb-10">
          A few things that show up in every engagement and are easy to miss
          when comparing on a website.
        </p>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {DIFFERENTIATORS.map((d) => {
            const Icon = d.icon;
            return (
              <Card key={d.title}>
                <CardContent className="p-6 space-y-3">
                  <div className="rounded-md bg-primary/10 p-2 w-fit">
                    <Icon className="w-5 h-5 text-primary" />
                  </div>
                  <h3 className="text-lg font-semibold">{d.title}</h3>
                  <p className="text-muted-foreground leading-relaxed text-sm">
                    {d.body}
                  </p>
                </CardContent>
              </Card>
            );
          })}
        </div>
      </section>

      {/* CTA */}
      <section className="mt-24 max-w-3xl mx-auto text-center space-y-6">
        <h2 className="text-3xl md:text-4xl font-bold">
          Want this for your team?
        </h2>
        <p className="text-lg text-muted-foreground">
          The services page covers scope, pricing, and how to start.
        </p>
        <div className="flex flex-col sm:flex-row gap-3 justify-center pt-2">
          <Button size="lg" asChild>
            <Link href="/services">
              See the offer
              <ArrowRight className="w-4 h-4 ml-2" />
            </Link>
          </Button>
          <Button size="lg" variant="outline" asChild>
            <Link href="/blog">Read the blog</Link>
          </Button>
        </div>
      </section>
    </div>
  );
}
