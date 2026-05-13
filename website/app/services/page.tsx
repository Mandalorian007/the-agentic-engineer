import Link from "next/link";
import type { Metadata } from "next";
import {
  ArrowRight,
  CheckCircle2,
  Compass,
  Cpu,
  GraduationCap,
  Building2,
  Landmark,
  Mail,
} from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

const CONTACT_EMAIL = "matthew.fontana@agentic-engineer.com";

const SERVICES_TITLE = "Work With Me";
const SERVICES_DESCRIPTION =
  "I help engineering organizations turn AI coding tools into production-grade developer platforms. Vendor-agnostic. Outcome-focused. Fixed-scope, fixed-fee engagements.";

export const metadata: Metadata = {
  title: SERVICES_TITLE,
  description: SERVICES_DESCRIPTION,
  alternates: { canonical: "/services" },
  openGraph: {
    title: SERVICES_TITLE,
    description: SERVICES_DESCRIPTION,
    url: "/services",
    type: "website",
    images: [{ url: "/og", width: 1200, height: 630, alt: SERVICES_TITLE }],
  },
  twitter: {
    card: "summary_large_image",
    title: SERVICES_TITLE,
    description: SERVICES_DESCRIPTION,
    images: ["/og"],
  },
};

const PHASES = [
  {
    icon: Compass,
    label: "Phase 1",
    title: "Discovery & strategy",
    duration: "2–3 weeks",
    body: "I audit how your teams actually use AI coding tools today (Claude Code, Codex, Cursor, Copilot, Windsurf, whatever you've licensed) and map adoption gaps, friction points, and security blockers. We agree on the metrics that prove the platform is working: cycle time, PR throughput, eval quality, developer satisfaction.",
    deliverables: [
      "Tool usage audit across teams",
      "Adoption + friction analysis",
      "Security and compliance review",
      "Success metrics and instrumentation plan",
    ],
  },
  {
    icon: Cpu,
    label: "Phase 2",
    title: "Platform implementation",
    duration: "8–12 weeks",
    body: "I build the platform layer around your tools: standardized configurations, a shared skill library, internal MCP servers exposing org-specific context, subagent orchestration patterns tailored to your workflows, and the codebase-specific evaluation harnesses that catch regressions before they ship.",
    deliverables: [
      "Standardized configs + skill libraries",
      "Internal MCP servers for shared context",
      "Subagent and orchestration patterns",
      "Evaluation + regression harnesses",
      "Guardrails, secrets handling, audit logging",
    ],
  },
  {
    icon: GraduationCap,
    label: "Phase 3",
    title: "Enablement",
    duration: "Overlaps phase 2",
    body: "A platform nobody uses is a sunk cost. I leave behind onboarding docs, in-house workshops, and runbooks so your team owns the system on day one. Adoption is part of the deliverable, not a hopeful side effect.",
    deliverables: [
      "Team onboarding documentation",
      "Live workshops (recorded for replay)",
      "Operating runbooks for ongoing evolution",
      "Internal champion enablement",
    ],
  },
];

const AUDIENCE = [
  {
    title: "Series B–D startups",
    body: "Scaling engineering fast, rolled out three AI tools, can't tell which are working.",
  },
  {
    title: "Mid-market enterprise",
    body: "50–500 developers across FinServ, healthcare, or SaaS. AI mandate from the top, chaos on the ground.",
  },
  {
    title: "Platform / DevEx teams",
    body: "Already own developer tooling. Need a senior partner who has shipped this before, not a deck.",
  },
  {
    title: "Federal agencies",
    body: "AI adoption mandate, existing tool licenses, no easy path to hire the internal expertise.",
  },
];

const ALTERNATIVES = [
  {
    option: "Internal eng team builds it",
    tradeoff:
      "Slow, opportunity cost, no benchmark for what good looks like.",
  },
  {
    option: "Big consultancy",
    tradeoff:
      "10× the price, generic frameworks, no hands-on platform depth.",
  },
  {
    option: "Tool vendor solution engineer",
    tradeoff:
      "Biased to one product, won't build the cross-tool platform you actually need.",
  },
  {
    option: "Hire a staff agentic engineer",
    tradeoff:
      "$400K+/year fully loaded, six-month ramp, hard to find.",
  },
];

const SERVICES_JSON_LD = {
  "@context": "https://schema.org",
  "@type": "ProfessionalService",
  name: "The Agentic Engineer",
  url: "https://agentic-engineer.com/services",
  description: SERVICES_DESCRIPTION,
  image: "https://agentic-engineer.com/the-agentic-engineer-logo.webp",
  email: CONTACT_EMAIL,
  serviceType: "Agentic developer platform engineering",
  areaServed: [
    { "@type": "Country", name: "United States" },
    { "@type": "Place", name: "Remote, worldwide" },
  ],
  provider: {
    "@type": "Person",
    name: "Matthew Fontana",
    email: CONTACT_EMAIL,
    url: "https://agentic-engineer.com",
    jobTitle: "Agentic developer platform engineer",
  },
  hasOfferCatalog: {
    "@type": "OfferCatalog",
    name: "Engagements",
    itemListElement: [
      {
        "@type": "Offer",
        itemOffered: {
          "@type": "Service",
          name: "Discovery sprint",
          description:
            "Two- to three-week audit, gap analysis, success metrics, and written platform blueprint.",
        },
      },
      {
        "@type": "Offer",
        itemOffered: {
          "@type": "Service",
          name: "Platform build",
          description:
            "Ten- to fourteen-week implementation across discovery, platform, and enablement. Fixed-scope, fixed-fee.",
        },
      },
      {
        "@type": "Offer",
        itemOffered: {
          "@type": "Service",
          name: "Retainer",
          description:
            "Ongoing platform evolution: new tools, new patterns, eval maintenance, quarterly adoption reviews.",
        },
      },
    ],
  },
};

export default function ServicesPage() {
  return (
    <div className="container py-12 md:py-20">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(SERVICES_JSON_LD) }}
      />
      {/* Hero */}
      <section className="max-w-4xl mx-auto text-center space-y-6">
        <Badge variant="outline" className="mx-auto">
          Agentic Developer Platform Engineering
        </Badge>
        <h1 className="text-4xl md:text-6xl font-bold tracking-tight">
          I build agentic developer platforms that make engineering teams measurably faster.
        </h1>
        <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
          Vendor-agnostic. Production-grade. Outcome-focused. I help engineering
          orgs turn AI coding tools into developer platforms their teams actually
          use.
        </p>
        <div className="flex flex-col sm:flex-row gap-3 justify-center pt-2">
          <Button size="lg" asChild>
            <a href={`mailto:${CONTACT_EMAIL}?subject=Platform%20engagement%20inquiry`}>
              <Mail className="w-4 h-4 mr-2" />
              Start a conversation
            </a>
          </Button>
          <Button size="lg" variant="outline" asChild>
            <Link href="/approach">
              See how I work
              <ArrowRight className="w-4 h-4 ml-2" />
            </Link>
          </Button>
        </div>
      </section>

      {/* The problem */}
      <section className="mt-24 max-w-3xl mx-auto">
        <h2 className="text-3xl font-bold mb-6">The problem you actually have</h2>
        <div className="space-y-4 text-lg text-muted-foreground leading-relaxed">
          <p>
            Your team has Claude Code, Copilot, Cursor, Codex, and three internal
            AI hackathon winners. Adoption sits at 15%. There&apos;s no
            measurement, security is anxious, and velocity hasn&apos;t moved.
          </p>
          <p>
            The tools work. What&apos;s missing is the platform around them:
            shared configurations, org-specific context, evaluations, guardrails,
            and the enablement that turns a license bill into a force
            multiplier.
          </p>
          <p className="text-foreground font-medium">
            That platform is what I build.
          </p>
        </div>
      </section>

      {/* What I deliver */}
      <section className="mt-24">
        <div className="max-w-3xl mx-auto mb-12">
          <h2 className="text-3xl font-bold mb-4">What I deliver</h2>
          <p className="text-lg text-muted-foreground">
            A typical engagement runs in three phases over 10–14 weeks. Scope
            and sequence flex to what your org needs.
          </p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {PHASES.map((phase) => {
            const Icon = phase.icon;
            return (
              <Card key={phase.title} className="h-full">
                <CardContent className="p-6 space-y-4">
                  <div className="flex items-start justify-between">
                    <div className="rounded-md bg-primary/10 p-2.5">
                      <Icon className="w-5 h-5 text-primary" />
                    </div>
                    <Badge variant="secondary" className="text-xs">
                      {phase.duration}
                    </Badge>
                  </div>
                  <div>
                    <div className="text-xs font-semibold uppercase text-muted-foreground tracking-wide">
                      {phase.label}
                    </div>
                    <h3 className="text-xl font-semibold mt-1">{phase.title}</h3>
                  </div>
                  <p className="text-muted-foreground leading-relaxed">
                    {phase.body}
                  </p>
                  <ul className="space-y-2 pt-2">
                    {phase.deliverables.map((d) => (
                      <li key={d} className="flex items-start gap-2 text-sm">
                        <CheckCircle2 className="w-4 h-4 text-primary mt-0.5 shrink-0" />
                        <span>{d}</span>
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>
            );
          })}
        </div>
      </section>

      {/* Who it's for */}
      <section className="mt-24 max-w-5xl mx-auto">
        <h2 className="text-3xl font-bold mb-12 text-center">Who this is for</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {AUDIENCE.map((aud) => (
            <Card key={aud.title}>
              <CardContent className="p-6">
                <div className="flex items-start gap-3">
                  <Building2 className="w-5 h-5 text-primary mt-1 shrink-0" />
                  <div>
                    <h3 className="font-semibold text-lg">{aud.title}</h3>
                    <p className="text-muted-foreground mt-1">{aud.body}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
        <p className="text-center text-muted-foreground mt-8 max-w-2xl mx-auto">
          Best fit: engineering orgs of <strong className="text-foreground">50–500 developers</strong>. Big enough to need the platform, small enough to act on it.
        </p>
      </section>

      {/* Why me */}
      <section className="mt-24 max-w-4xl mx-auto">
        <h2 className="text-3xl font-bold mb-4">Why me</h2>
        <p className="text-lg text-muted-foreground mb-8">
          You have alternatives. Here&apos;s the honest tradeoff against each.
        </p>
        <div className="border rounded-lg overflow-hidden">
          <div className="grid grid-cols-1 md:grid-cols-2 bg-muted/50 border-b text-sm font-semibold uppercase tracking-wide">
            <div className="p-4">What you could buy instead</div>
            <div className="p-4 border-t md:border-t-0 md:border-l">The tradeoff</div>
          </div>
          {ALTERNATIVES.map((alt, i) => (
            <div
              key={alt.option}
              className={`grid grid-cols-1 md:grid-cols-2 ${
                i < ALTERNATIVES.length - 1 ? "border-b" : ""
              }`}
            >
              <div className="p-4 font-medium">{alt.option}</div>
              <div className="p-4 text-muted-foreground border-t md:border-t-0 md:border-l">
                {alt.tradeoff}
              </div>
            </div>
          ))}
        </div>
        <p className="text-muted-foreground mt-6">
          I&apos;m the fast, deep, neutral option: a staff-level engineer who
          has shipped this pattern, working directly with your team for the
          weeks it takes to land it.
        </p>
      </section>

      {/* Federal */}
      <section className="mt-24 max-w-4xl mx-auto">
        <Card className="border-primary/30">
          <CardContent className="p-8 space-y-4">
            <div className="flex items-center gap-3">
              <Landmark className="w-6 h-6 text-primary" />
              <h2 className="text-2xl font-bold">Federal engagements</h2>
            </div>
            <p className="text-muted-foreground leading-relaxed">
              Federal agencies have AI adoption mandates, existing tool licenses,
              and procurement rules that favor specialist consultants over
              full-time hires. I work with civilian and defense agencies on
              short-form pilots and platform builds that fit within standard
              vehicles.
            </p>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2">
              <div>
                <div className="text-xs font-semibold uppercase text-muted-foreground tracking-wide mb-1">
                  NAICS codes
                </div>
                <div className="font-mono text-sm">541511 · 541512 · 541715</div>
              </div>
              <div>
                <div className="text-xs font-semibold uppercase text-muted-foreground tracking-wide mb-1">
                  Sources Sought keywords
                </div>
                <div className="text-sm">
                  AI developer productivity, generative AI tooling, agent platform,
                  agentic, LLM, Copilot enterprise, Claude
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </section>

      {/* Pricing & engagement */}
      <section className="mt-24 max-w-4xl mx-auto">
        <h2 className="text-3xl font-bold mb-4">Engagement model</h2>
        <p className="text-lg text-muted-foreground mb-8">
          Fixed-scope, fixed-fee. Scoped after a 30-minute conversation, agreed
          in writing before kickoff.
        </p>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card>
            <CardContent className="p-6 space-y-3">
              <Badge variant="secondary">Discovery sprint</Badge>
              <div className="text-3xl font-bold">2–3 weeks</div>
              <p className="text-muted-foreground text-sm">
                Audit, gap analysis, success metrics, and a written platform
                blueprint. Sometimes runs standalone for orgs that want a
                second opinion before committing.
              </p>
            </CardContent>
          </Card>
          <Card className="border-primary/40">
            <CardContent className="p-6 space-y-3">
              <Badge>Platform build</Badge>
              <div className="text-3xl font-bold">10–14 weeks</div>
              <p className="text-muted-foreground text-sm">
                Full implementation across discovery, platform, and enablement.
                Scope and fee shaped to org size, tool footprint, and
                compliance needs.
              </p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-6 space-y-3">
              <Badge variant="secondary">Retainer</Badge>
              <div className="text-3xl font-bold">Ongoing</div>
              <p className="text-muted-foreground text-sm">
                Optional follow-on for ongoing platform evolution: new tools,
                new patterns, eval maintenance, and quarterly adoption
                reviews.
              </p>
            </CardContent>
          </Card>
        </div>
      </section>

      {/* Final CTA */}
      <section className="mt-24 max-w-3xl mx-auto text-center space-y-6">
        <h2 className="text-3xl md:text-4xl font-bold">Ready to talk?</h2>
        <p className="text-lg text-muted-foreground">
          A first conversation is 30 minutes. I want to understand what
          tools you&apos;ve rolled out, where adoption stalled, and what
          shipping faster would unlock. If we&apos;re a fit, the next step is
          a discovery sprint.
        </p>
        <div className="flex flex-col sm:flex-row gap-3 justify-center pt-2">
          <Button size="lg" asChild>
            <a href={`mailto:${CONTACT_EMAIL}?subject=Platform%20engagement%20inquiry`}>
              <Mail className="w-4 h-4 mr-2" />
              {CONTACT_EMAIL}
            </a>
          </Button>
          <Button size="lg" variant="outline" asChild>
            <Link href="/approach">
              Read the methodology
              <ArrowRight className="w-4 h-4 ml-2" />
            </Link>
          </Button>
        </div>
      </section>
    </div>
  );
}
