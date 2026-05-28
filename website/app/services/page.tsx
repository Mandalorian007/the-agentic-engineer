import Link from "next/link";
import type { Metadata } from "next";
import {
  ArrowRight,
  Mail,
  Target,
  Layers,
  GaugeCircle,
  Search,
  ShieldCheck,
  Users,
} from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { CREDENTIAL_LINE } from "@/lib/bio";

const CONTACT_EMAIL = "matthew.fontana@agentic-engineer.com";

const SERVICES_TITLE = "Work With Me";
const SERVICES_DESCRIPTION =
  "Most of my work is building agentic developer platforms inside Airbnb. A handful of times a year I work with engineering teams on the platform layer underneath their AI tools. No fixed packages. Start a conversation.";

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
    jobTitle: "Staff Software Engineer",
  },
};

// Open-ended list of the problems I'm useful on — described as activities,
// not packaged deliverables. No timelines, no pricing, no qualification gate.
const HELP_WITH = [
  "Agentic platform strategy: turning a pile of AI tool licenses into a platform your teams actually use.",
  "MCP architecture: exposing your codebase, data, and internal services to agents under existing auth.",
  "Evaluations: codebase-specific harnesses so you can tell when an agent is helping and when it's drifting.",
  "Developer productivity: measuring the platform in terms leadership can defend to the business.",
];

// How I tend to work — principles that shape the work, not a fixed process.
const PRINCIPLES = [
  {
    icon: Target,
    title: "Outcomes over outputs",
    body: "The deliverable isn't a deck or a Notion page. It's measurable adoption and a velocity number that moves. We agree on the metric early and instrument for it.",
  },
  {
    icon: Layers,
    title: "Vendor-agnostic by design",
    body: "Codex, Copilot, Claude Code, Cursor, Windsurf are tactical. The platform layer is strategic. I build to the meta-layer so the system survives the next tool launch.",
  },
  {
    icon: GaugeCircle,
    title: "Evaluations are the missing layer",
    body: "Most rollouts skip evals because they're hard. That's why adoption stalls. Codebase-specific evaluation harnesses are non-negotiable in the work I do.",
  },
  {
    icon: Search,
    title: "Your codebase is the context",
    body: "Generic agents are weak. The moat is org-specific context: internal MCP servers, packaged skills, and subagent patterns shaped to how your teams actually ship.",
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
    body: "You work directly with me. No account team layer, no handoffs between phases.",
  },
  {
    icon: Target,
    title: "Production codebases, not pilots",
    body: "The work lands in your real repos with real teams. Pilots that never ship don't move metrics.",
  },
];

export default function ServicesPage() {
  return (
    <div className="container py-12 md:py-20">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(SERVICES_JSON_LD) }}
      />

      {/* Hero — open invitation, not a packaged offer */}
      <section className="max-w-3xl mx-auto text-center space-y-6">
        <h1 className="text-4xl md:text-6xl font-bold tracking-tight">
          Work with me
        </h1>
        <p className="text-xl text-muted-foreground">
          Most of my work is writing, building, and shipping inside Airbnb. A
          handful of times a year I work with engineering teams on the platform
          layer underneath their AI tools, when there&apos;s real fit on both
          sides.
        </p>
        <p className="text-sm text-muted-foreground">
          By{" "}
          <Link
            href="/about"
            className="font-medium text-foreground underline underline-offset-4 hover:no-underline"
          >
            Matthew Fontana
          </Link>{" "}
          · {CREDENTIAL_LINE}
        </p>
        <div className="flex justify-center pt-2">
          <Button size="lg" asChild>
            <a href={`mailto:${CONTACT_EMAIL}?subject=Platform%20engagement%20inquiry`}>
              <Mail className="w-4 h-4 mr-2" />
              Start a conversation
            </a>
          </Button>
        </div>
      </section>

      {/* What I tend to help with — activities, not deliverables */}
      <section className="mt-24 max-w-2xl mx-auto">
        <h2 className="text-3xl font-bold mb-4">What I tend to help with</h2>
        <p className="text-lg text-muted-foreground mb-8">
          Every team&apos;s situation is different, so I don&apos;t sell fixed
          packages. These are the kinds of problems I&apos;m useful on:
        </p>
        <ul className="space-y-4 text-lg text-muted-foreground">
          {HELP_WITH.map((item) => (
            <li key={item} className="flex items-start gap-3">
              <ArrowRight className="w-5 h-5 text-primary mt-1 shrink-0" />
              <span>{item}</span>
            </li>
          ))}
        </ul>
      </section>

      {/* How I tend to work — folded in from the former /approach page */}
      <section className="mt-24 max-w-5xl mx-auto">
        <h2 className="text-3xl font-bold mb-4">How I tend to work</h2>
        <p className="text-lg text-muted-foreground mb-10">
          No two engagements look the same, so this isn&apos;t a fixed process.
          It&apos;s the handful of principles that shape every piece of platform
          work I take on.
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

      {/* What's different */}
      <section className="mt-24 max-w-5xl mx-auto">
        <h2 className="text-3xl font-bold mb-4">What&apos;s different</h2>
        <p className="text-lg text-muted-foreground mb-10">
          A few things that show up whenever I work with a team, and are easy to
          miss when comparing on a website.
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

      {/* Final CTA — open-ended inquiry */}
      <section className="mt-24 max-w-2xl mx-auto text-center space-y-6">
        <h2 className="text-3xl md:text-4xl font-bold">Get in touch</h2>
        <p className="text-lg text-muted-foreground">
          No pitch deck, no qualification form. Email me what you&apos;re
          wrestling with: where adoption stalled, what shipping faster would
          unlock. We&apos;ll figure out together whether there&apos;s a fit.
        </p>
        <div className="flex justify-center pt-2">
          <Button size="lg" asChild>
            <a href={`mailto:${CONTACT_EMAIL}?subject=Platform%20engagement%20inquiry`}>
              <Mail className="w-4 h-4 mr-2" />
              {CONTACT_EMAIL}
            </a>
          </Button>
        </div>
      </section>
    </div>
  );
}
