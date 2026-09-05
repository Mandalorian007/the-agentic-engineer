import Link from "next/link";
import Image from "next/image";
import type { Metadata } from "next";
import {
  ArrowRight,
  MapPin,
  Building2,
  GraduationCap,
  Rocket,
  Sparkles,
  BookOpen,
  GitBranch,
  ExternalLink,
} from "lucide-react";
// Brand icons live outside lucide-react v1 (removed for trademark reasons);
// react-icons still ships them.
import { FaGithub, FaLinkedinIn } from "react-icons/fa6";

import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { NewsletterCta } from "@/components/newsletter-cta";
import { AUTHOR, SITE_URL } from "@/lib/site";

const CONTACT_EMAIL = AUTHOR.email;
const GITHUB_URL = AUTHOR.github;
const LINKEDIN_URL = "https://www.linkedin.com/in/matthew-fontana/";
const TAC_URL = "https://tabletopadventurecreator.com";
const REPO_URL = "https://github.com/Mandalorian007/the-agentic-engineer";

const ABOUT_TITLE = "About Matthew Fontana";
const ABOUT_DESCRIPTION =
  "Staff Software Engineer at Airbnb. I encode my own workflows into agents inside a large engineering org, and everything I write here is something I actually run.";

export const metadata: Metadata = {
  title: ABOUT_TITLE,
  description: ABOUT_DESCRIPTION,
  alternates: { canonical: "/about" },
  openGraph: {
    title: ABOUT_TITLE,
    description: ABOUT_DESCRIPTION,
    url: "/about",
    type: "profile",
    images: [{ url: "/og", width: 1200, height: 630, alt: ABOUT_TITLE }],
  },
  twitter: {
    card: "summary_large_image",
    title: ABOUT_TITLE,
    description: ABOUT_DESCRIPTION,
    images: ["/og"],
  },
};

const PERSON_JSON_LD = {
  "@context": "https://schema.org",
  "@type": "Person",
  name: AUTHOR.name,
  url: AUTHOR.url,
  image: `${SITE_URL}${AUTHOR.avatar}`,
  email: CONTACT_EMAIL,
  jobTitle: "Staff Software Engineer",
  homeLocation: {
    "@type": "Place",
    address: {
      "@type": "PostalAddress",
      addressLocality: "Hoboken",
      addressRegion: "NJ",
      addressCountry: "US",
    },
  },
  worksFor: { "@type": "Organization", name: "Airbnb" },
  alumniOf: [
    { "@type": "Organization", name: "Spotify" },
    { "@type": "Organization", name: "UPS" },
    {
      "@type": "CollegeOrUniversity",
      name: "New Jersey Institute of Technology",
    },
  ],
  sameAs: [GITHUB_URL, LINKEDIN_URL, TAC_URL, REPO_URL],
  knowsAbout: [
    "Agentic engineering",
    "Claude Code",
    "Model Context Protocol",
    "LiteLLM",
    "Developer productivity engineering",
    "Data infrastructure",
    "Spring Boot",
    "Java",
    "TypeScript",
    "Python",
  ],
};

// Passport principle: experience as scaffolded reputation. Dates do the
// long-tenure work passively; no "X years of experience" claims.
type ExperienceEntry = {
  org: string;
  role: string;
  period: string;
  note: string;
  type: "employer" | "founder" | "school";
  url?: string;
};

const EXPERIENCE: ExperienceEntry[] = [
  {
    org: "Airbnb",
    role: "Staff Software Engineer, Data Management",
    period: "2024 – present",
    note: "Productionized an internal AI agent for natural-language search and discovery across the data warehouse. Claude Code Marketplace plugin combining skills, subagents, hooks, and commands. CLI + API MCP servers with internal AuthN/AuthZ. Evaluation framework that scores business outcomes, not unit pass rates.",
    type: "employer",
  },
  {
    org: "TabletopAdventureCreator.com",
    role: "Founder",
    period: "2022 – present",
    note: "Solo-built generative-AI SaaS for tabletop RPG adventure creation. In production since 2022, before the current generative AI wave.",
    type: "founder",
    url: TAC_URL,
  },
  {
    org: "Spotify",
    role: "Staff Software Engineer, Productivity Engineering",
    period: "2022 – 2024",
    note: "Chairman of the Productivity Engineering Technical Steering Group. Led six teams across developer tooling, IAM, and employee lifecycle. Reduced non-business-focused dev cycles by 30%.",
    type: "employer",
  },
  {
    org: "Spotify",
    role: "Senior Software Engineer, Spotify for Artists",
    period: "2020 – 2022",
    note: "Two-sided marketplace work: GDPR audit system for artists, labels, and distributors. Payment provider scaling. Instructor for the internal data-science bootcamp.",
    type: "employer",
  },
  {
    org: "Spotify",
    role: "Data Engineer",
    period: "2017 – 2020",
    note: "Introduced Spring Boot to Spotify's backend. GDPR compliance on GCP BigQuery. Co-founded a Google + Spotify Special Interest Group.",
    type: "employer",
  },
  {
    org: "UPS",
    role: "Associate → Senior Application Developer",
    period: "2014 – 2017",
    note: "JVM platform work. Introduced OpenShift to enable microservices. Spring Cloud, AXON event sourcing, lambda-architecture streaming on Cassandra/Solr/Spark, JBoss Fuse / Camel / ActiveMQ.",
    type: "employer",
  },
  {
    org: "NJIT",
    role: "B.S., Information Technology",
    period: "2009 – 2013",
    note: "New Jersey Institute of Technology.",
    type: "school",
  },
];

type PublicWorkEntry = {
  // Accepts both lucide-react and react-icons components. Both expose a
  // className prop, which is all we use at render time.
  icon: React.ComponentType<{ className?: string }>;
  title: string;
  body: string;
  href: string;
  cta: string;
  external: boolean;
};

const PUBLIC_WORK: PublicWorkEntry[] = [
  {
    icon: GitBranch,
    title: "This site, as source",
    body: "The blog and the pipeline that publishes it. Commands, safety hooks, prose linting, scheduling, and every post as raw MDX.",
    href: REPO_URL,
    cta: "Read the repo",
    external: true,
  },
  {
    icon: Sparkles,
    title: "Tabletop Adventure Creator",
    body: "Solo-built generative-AI SaaS for tabletop RPG adventure creation. Live since 2022, before the current AI wave.",
    href: TAC_URL,
    cta: "Visit the product",
    external: true,
  },
  {
    icon: FaGithub,
    title: "@Mandalorian007 on GitHub",
    body: "Public repos including aitk (the portable AI CLI toolkit), claude-code-toolkit, claude-tmux-manager, and other Claude Code tooling.",
    href: GITHUB_URL,
    cta: "Browse the repos",
    external: true,
  },
  {
    icon: BookOpen,
    title: "The Agentic Engineer blog",
    body: "Field notes on handing real work to agents without losing control of your codebase. Patterns, tooling, things that broke.",
    href: "/blog",
    cta: "Read the blog",
    external: false,
  },
];

export default function AboutPage() {
  return (
    <div className="container py-12 md:py-20">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(PERSON_JSON_LD) }}
      />

      {/*
        HERO — Passport "user card" pattern.
        Photo + identity block side-by-side. Visible verifications (employer,
        GitHub, LinkedIn) make the page feel like a profile, not a brochure.
      */}
      <section className="mx-auto grid max-w-5xl grid-cols-1 items-start gap-10 md:grid-cols-[260px_1fr]">
        <div className="space-y-4">
          <div className="relative aspect-square w-full overflow-hidden rounded-lg border bg-muted">
            <Image
              src="/about/matthew-fontana.webp"
              alt="Matthew Fontana"
              fill
              priority
              className="object-cover object-center"
              sizes="(max-width: 768px) 100vw, 260px"
            />
          </div>
          <div className="flex flex-wrap gap-2 text-xs">
            <Badge variant="secondary" className="gap-1.5">
              <Building2 className="h-3 w-3" />
              Staff Engineer · Airbnb
            </Badge>
            <Badge variant="secondary" className="gap-1.5">
              <MapPin className="h-3 w-3" />
              Hoboken, NJ
            </Badge>
          </div>
        </div>

        <div className="space-y-6">
          <div className="space-y-3">
            <Badge variant="outline">About</Badge>
            <h1 className="text-4xl font-bold tracking-tight md:text-5xl">
              Hi, I&apos;m Matthew Fontana.
            </h1>
            <p className="text-xl text-muted-foreground">
              Staff engineer at Airbnb. Before that Spotify, before that UPS.
              I&apos;ve spent that whole time inside big engineering orgs
              working out how to hand real work to machines without it going
              badly.
            </p>
            <p className="text-xl text-muted-foreground">
              Everything I write here is something I actually run.
            </p>
          </div>

          <div className="flex flex-wrap gap-3">
            <Button variant="outline" asChild>
              <a href={GITHUB_URL} target="_blank" rel="noopener noreferrer">
                <FaGithub className="mr-2 h-4 w-4" />
                GitHub
              </a>
            </Button>
            <Button variant="outline" asChild>
              <a href={LINKEDIN_URL} target="_blank" rel="noopener noreferrer">
                <FaLinkedinIn className="mr-2 h-4 w-4" />
                LinkedIn
              </a>
            </Button>
          </div>
        </div>
      </section>

      {/*
        PROOF — the strongest credibility artifact is the site itself, which
        is produced by the workflow the site describes. Show, don't claim.
      */}
      <section className="mx-auto mt-24 max-w-3xl">
        <h2 className="text-3xl font-bold">This site is the argument</h2>
        <p className="mt-4 text-lg text-muted-foreground">
          You&apos;re reading the output of the method. Posts come out of a
          voice pipeline I built. Images are generated. Prose gets linted before
          it ships. Publishing is scheduled and automated. A safety hook blocks
          agent commands I don&apos;t want run, and it has stopped me more than
          once.
        </p>
        <p className="mt-4 text-lg">
          It&apos;s all one public repo. The method is the repo.
        </p>
        <div className="mt-6">
          <Button asChild>
            <a href={REPO_URL} target="_blank" rel="noopener noreferrer">
              <GitBranch className="mr-2 h-4 w-4" />
              See how this site is built
            </a>
          </Button>
        </div>
      </section>

      {/* Newsletter */}
      <section className="mx-auto mt-20 max-w-3xl">
        <NewsletterCta source="about" />
      </section>

      {/*
        EXPERIENCE — Passport principle: dates do the long-tenure work
        passively. No "X years of experience" claims.
      */}
      <section className="mx-auto mt-24 max-w-4xl">
        <h2 className="mb-4 text-3xl font-bold">Experience</h2>
        <p className="mb-10 text-lg text-muted-foreground">
          Roles, employers, years. The rest is in the bio above.
        </p>
        <ol className="relative ml-4 space-y-8 border-l border-border">
          {EXPERIENCE.map((e) => {
            const Icon =
              e.type === "school"
                ? GraduationCap
                : e.type === "founder"
                  ? Rocket
                  : Building2;
            const isFounder = e.type === "founder";
            const orgClass = isFounder ? "text-primary" : "text-muted-foreground";
            const dotClass = isFounder
              ? "bg-primary/10 border-primary/40"
              : "bg-background border-border";
            const iconClass = isFounder ? "text-primary" : "text-muted-foreground";
            return (
              <li key={`${e.org}-${e.period}`} className="ml-6">
                <span
                  className={`absolute -left-3 flex h-6 w-6 items-center justify-center rounded-full border ${dotClass}`}
                >
                  <Icon className={`h-3 w-3 ${iconClass}`} />
                </span>
                <div className="mb-1 flex flex-wrap items-baseline justify-between gap-2">
                  <h3 className="text-lg font-semibold">
                    {e.role}{" "}
                    <span className={`font-normal ${orgClass}`}>
                      ·{" "}
                      {e.url ? (
                        <a
                          href={e.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="underline underline-offset-4 hover:no-underline"
                        >
                          {e.org}
                        </a>
                      ) : (
                        e.org
                      )}
                    </span>
                    {isFounder && (
                      <Badge
                        variant="outline"
                        className="ml-2 border-primary/40 text-[10px] uppercase tracking-wide text-primary"
                      >
                        Founder track
                      </Badge>
                    )}
                  </h3>
                  <span className="font-mono text-sm text-muted-foreground">
                    {e.period}
                  </span>
                </div>
                <p className="leading-relaxed text-muted-foreground">{e.note}</p>
              </li>
            );
          })}
        </ol>
      </section>

      {/*
        SELECTED PUBLIC WORK — Passport "show, don't tell" principle.
        Concrete artifacts a reader can click into and verify the claims
        on the rest of the page.
      */}
      <section className="mx-auto mt-24 max-w-5xl">
        <h2 className="mb-4 text-3xl font-bold">Selected public work</h2>
        <p className="mb-10 text-lg text-muted-foreground">
          Things you can open and check for yourself.
        </p>
        <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
          {PUBLIC_WORK.map((entry) => (
            <Card key={entry.title} className="size-full">
              <CardContent className="flex h-full flex-col gap-3 p-6">
                <entry.icon className="h-5 w-5 text-primary" />
                <h3 className="min-w-0 break-words text-lg font-semibold leading-tight">
                  {entry.title}
                </h3>
                <p className="text-muted-foreground">{entry.body}</p>
                <div className="mt-auto pt-2">
                  {entry.external ? (
                    <Button variant="outline" size="sm" asChild>
                      <a
                        href={entry.href}
                        target="_blank"
                        rel="noopener noreferrer"
                      >
                        {entry.cta}
                        <ExternalLink className="ml-2 h-3.5 w-3.5" />
                      </a>
                    </Button>
                  ) : (
                    <Button variant="outline" size="sm" asChild>
                      <Link href={entry.href}>
                        {entry.cta}
                        <ArrowRight className="ml-2 h-3.5 w-3.5" />
                      </Link>
                    </Button>
                  )}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </section>

      {/* Hire me, demoted to match the homepage */}
      <section className="mx-auto mt-24 max-w-5xl border-t pt-8">
        <div className="flex flex-col items-start justify-between gap-3 text-sm text-muted-foreground sm:flex-row sm:items-center">
          <p>Want me to come talk to your team?</p>
          <Link
            href="/services"
            className="font-medium text-foreground underline underline-offset-4"
          >
            Hire me
          </Link>
        </div>
      </section>
    </div>
  );
}
