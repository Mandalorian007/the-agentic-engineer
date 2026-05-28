import Link from "next/link";
import Image from "next/image";
import type { Metadata } from "next";
import {
  ArrowRight,
  Mail,
  Rss,
  MapPin,
  Building2,
  GraduationCap,
  Rocket,
  Bot,
  Network,
  GaugeCircle,
  Layers,
  Sparkles,
  BookOpen,
  ExternalLink,
} from "lucide-react";
// Brand icons live outside lucide-react v1 (removed for trademark reasons);
// react-icons/fa6 is the project's established pattern (see share-buttons.tsx).
import { FaGithub, FaLinkedinIn } from "react-icons/fa6";

import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  CONTACT_EMAIL,
  GITHUB_URL,
  LINKEDIN_URL,
  TAC_URL,
  TENURE_YEARS,
} from "@/lib/bio";

const ABOUT_TITLE = "About Matthew Fontana";
const ABOUT_DESCRIPTION =
  "Staff Software Engineer at Airbnb. I write at agentic-engineer.com about agentic developer platforms, MCP, and the agentic SDLC, and help a handful of engineering teams a year build theirs.";

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

// If you edit EXPERIENCE below, update worksFor / alumniOf / knowsAbout here too.
const PERSON_JSON_LD = {
  "@context": "https://schema.org",
  "@type": "Person",
  name: "Matthew Fontana",
  url: "https://agentic-engineer.com/about",
  image: "https://agentic-engineer.com/the-agentic-engineer-logo.webp",
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
  sameAs: [GITHUB_URL, LINKEDIN_URL, TAC_URL],
  knowsAbout: [
    "Agentic developer platforms",
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
    role: "Staff Software Engineer",
    period: "2024 – present",
    note: "Core member of the taskforce taking Airbnb's data warehouse agent-native. Integrated the metadata systems with MCP under device-derived, user-scoped access. Shipped a vendor-agnostic marketplace plugin (skills, subagents, commands) bringing natural-language search, discovery, and analytics into Claude Code, Codex, and Gemini CLI. Hardened lineage into column-level extraction for governance and GDPR visibility.",
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
    note: "Chair of the Technical Steering Group. Led technical direction across six teams spanning device endpoint management, vendor integrations, access and identity, and employee lifecycle. Extended Spotify's quality framework to cover the tribe's systems and mentored six engineers into tech-leadership roles, all promoted.",
    type: "employer",
  },
  {
    org: "Spotify",
    role: "Senior Software Engineer, Spotify for Artists",
    period: "2020 – 2022",
    note: "Two-sided marketplace work: GDPR-compliant audit system for shared artist accounts across labels and distributors; technical owner of the team-management layer; internal payments wrapped as an enterprise payment provider with tax collection. Taught the internal data-science bootcamp.",
    type: "employer",
  },
  {
    org: "Spotify",
    role: "Data Engineer",
    period: "2017 – 2020",
    note: "Drove the working group evolving Spotify's Apollo framework toward Spring Boot. Brought GDPR compliance to data engineering on GCP BigQuery. Co-founded a Google + Spotify Special Interest Group. Built an automated regional ad-generation system that lifted acquisition 15%.",
    type: "employer",
  },
  {
    org: "UPS",
    role: "Associate → Senior Application Developer",
    period: "2013 – 2017",
    note: "JVM platform work across four years. Introduced OpenShift to enable microservices. Spring Cloud Data Flow, AXON event sourcing, lambda-architecture streaming on Cassandra/Solr/Spark, JBoss Fuse / Camel / ActiveMQ.",
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

const WORK_AREAS = [
  {
    icon: Bot,
    title: "Agentic developer platforms",
    body: "Skills, subagents, hooks, slash commands, and the eval harnesses that keep them honest in production. Your team adopts the platform without having to own every primitive.",
  },
  {
    icon: Network,
    title: "MCP servers and provider-portable routing",
    body: "CLI and API MCP servers that expose your codebase, data, and internal services to AI agents under existing AuthN/AuthZ. LiteLLM-style routing keeps the platform portable across Anthropic, OpenAI, Google, and self-hosted models, so the work survives the next provider launch.",
  },
  {
    icon: GaugeCircle,
    title: "Developer productivity at org scale",
    body: "As chair of Spotify's Productivity Engineering steering group, I turned scattered tooling into a measurable platform that engineering leaders can defend to the business.",
  },
  {
    icon: Layers,
    title: "The standard everyone ends up adopting",
    body: "Pattern across three employers: I introduce the platform layer (Spring Boot at Spotify, OpenShift at UPS, Claude Code plugin at Airbnb) and it propagates because it earns adoption, not because it's mandated.",
  },
];

// Selected public work: the show-don't-tell layer. Concrete artifacts a
// reader can click into and verify the claims on the rest of the page.
// Icon type accepts both lucide-react and react-icons components — both
// expose a className prop, which is all we use at render time.
type PublicWorkEntry = {
  icon: React.ComponentType<{ className?: string }>;
  title: string;
  body: string;
  href: string;
  cta: string;
  external: boolean;
};

const PUBLIC_WORK: PublicWorkEntry[] = [
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
    body: "Field notes from inside production engineering. Patterns, tooling, lessons learned. Published weekly.",
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
      <section className="grid grid-cols-1 md:grid-cols-[260px_1fr] gap-10 items-start max-w-5xl mx-auto">
        <div className="space-y-4">
          <div className="relative aspect-square w-full overflow-hidden rounded-lg border bg-muted">
            <Image
              src="/about/matthew-fontana.jpeg"
              alt="Matthew Fontana"
              fill
              priority
              sizes="(max-width: 768px) 100vw, 260px"
              className="object-cover object-center"
            />
          </div>
          <div className="flex flex-wrap gap-2 text-xs">
            <Badge variant="secondary" className="gap-1.5">
              <Building2 className="w-3 h-3" />
              Staff Engineer · Airbnb
            </Badge>
            <Badge variant="secondary" className="gap-1.5">
              <GraduationCap className="w-3 h-3" />
              {TENURE_YEARS} yrs in enterprise software
            </Badge>
            <Badge variant="secondary" className="gap-1.5">
              <MapPin className="w-3 h-3" />
              Hoboken, NJ
            </Badge>
          </div>
        </div>

        <div className="space-y-6">
          <div className="space-y-3">
            <Badge variant="outline">About</Badge>
            <h1 className="text-4xl md:text-5xl font-bold tracking-tight">
              Hi, I&apos;m Matthew Fontana.
            </h1>
            <p className="text-xl text-muted-foreground">
              I build agentic developer platforms inside large engineering
              orgs, write about the work here, and take on a few outside
              engagements a year.
            </p>
          </div>

          <div className="flex flex-wrap gap-3">
            <Button variant="outline" asChild>
              <a href={GITHUB_URL} target="_blank" rel="noopener noreferrer">
                <FaGithub className="w-4 h-4 mr-2" />
                GitHub
              </a>
            </Button>
            <Button variant="outline" asChild>
              <a href={LINKEDIN_URL} target="_blank" rel="noopener noreferrer">
                <FaLinkedinIn className="w-4 h-4 mr-2" />
                LinkedIn
              </a>
            </Button>
            <Button variant="outline" asChild>
              <Link href="/feed.xml">
                <Rss className="w-4 h-4 mr-2" />
                RSS
              </Link>
            </Button>
          </div>
        </div>
      </section>

      {/*
        NARRATIVE BIO — Passport "humanize aggressively" principle.
        First-person, warm, concrete. Walks the career arc without bragging.
        Tenure is shown, not announced. Specific metrics are woven into the
        prose rather than broken out as standalone cards; numbers feel earned
        when they sit inside the role that produced them.
      */}
      <section className="mt-20 max-w-3xl mx-auto space-y-5 text-lg leading-relaxed">
        <p>
          I&apos;m a Staff Software Engineer at Airbnb, on the taskforce taking
          our data warehouse agent-native. That&apos;s the platform layer that
          makes warehouse metadata addressable by coding agents, not just
          humans. I integrated the metadata systems with MCP so agents get
          structured access to discovery, querying, and administration, with
          device-derived access tokens injected into every request so the agent
          inherits the user&apos;s existing permissions. That alignment is what
          unblocked agent access to sensitive data. On top of it I shipped a
          vendor-agnostic marketplace plugin of skills, subagents, and commands
          that brings natural-language search, discovery, and analytics into
          Claude Code, Codex, and Gemini CLI. I also hardened the lineage
          infrastructure into column-level extraction for governance and GDPR
          visibility into personal-data flows.
        </p>
        <p>
          Before Airbnb I spent seven years at Spotify. I left as Staff in
          Productivity Engineering and Chair of the Technical Steering Group.
          Six teams under me spanned device endpoint management, vendor
          integrations, access and identity, and employee lifecycle. As TSG
          Chair I extended Spotify&apos;s quality framework to cover the
          hundreds of systems the tribe owned, and the six engineers I mentored
          into tech-leadership roles were all promoted. Earlier in that run I
          introduced Spring Boot to Spotify&apos;s backend, ran GDPR work inside
          the data engineering org, and built the GDPR-compliant audit system
          for the Spotify-for-Artists two-sided marketplace.
        </p>
        <p>
          Before Spotify, four years at UPS shipping Spring Cloud, OpenShift,
          and lambda-architecture streaming systems on top of the JVM.
          That&apos;s where the platform-engineering instinct started: the
          work that pays off is rarely the work in the ticket. It&apos;s the
          layer underneath.
        </p>
        <p>
          I&apos;ve also run{" "}
          <a
            href={TAC_URL}
            target="_blank"
            rel="noopener noreferrer"
            className="font-medium text-primary underline underline-offset-4 hover:no-underline"
          >
            TabletopAdventureCreator.com
          </a>{" "}
          since 2022. It&apos;s a generative-AI SaaS I built and still ship
          solo. Evidence that I was building production AI products before the
          current AI wave.
        </p>
      </section>

      {/*
        KILL LINE — pulled out of the bio so the page's strongest sentence
        gets its own visual moment. Acts as the punctuation between the
        narrative and the practice-area cards that follow.
      */}
      <section className="mt-16 max-w-3xl mx-auto">
        <Card className="border-primary/30 bg-primary/5">
          <CardContent className="p-8 md:p-10 text-center space-y-3">
            <p className="text-xs uppercase tracking-wider text-muted-foreground font-semibold">
              The work behind the writing
            </p>
            <p className="text-2xl md:text-3xl font-semibold leading-snug text-balance">
              The platform I write about here is the platform I&apos;m
              shipping in production every week.
            </p>
          </CardContent>
        </Card>
      </section>

      {/*
        WHAT I WORK ON — concrete domains. Replaces vague claims with named
        practice areas a reader can match against their actual problem.
        Icons added for visual congruence with /services.
      */}
      <section className="mt-24 max-w-5xl mx-auto">
        <h2 className="text-3xl font-bold mb-4">What I work on</h2>
        <p className="text-lg text-muted-foreground mb-10">
          Four areas the work tends to land in. They overlap more than they
          don&apos;t.
        </p>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {WORK_AREAS.map((area) => {
            const Icon = area.icon;
            return (
              <Card key={area.title}>
                <CardContent className="space-y-3">
                  <div className="flex items-start gap-3">
                    <div className="rounded-md bg-primary/10 p-2 shrink-0">
                      <Icon className="w-5 h-5 text-primary" />
                    </div>
                    <h3 className="text-lg font-semibold leading-tight min-w-0 break-words">
                      {area.title}
                    </h3>
                  </div>
                  <p className="text-muted-foreground leading-relaxed text-sm">
                    {area.body}
                  </p>
                </CardContent>
              </Card>
            );
          })}
        </div>
      </section>

      {/*
        EXPERIENCE TIMELINE — long-tenure signal delivered passively.
        Founder-track entry (TAC) gets its own icon (Rocket) and accent
        color so the parallel founder/employee tracks read clearly.
      */}
      <section className="mt-24 max-w-4xl mx-auto">
        <h2 className="text-3xl font-bold mb-4">Experience</h2>
        <p className="text-lg text-muted-foreground mb-10">
          Roles, employers, years. The rest is in the bio above.
        </p>
        <ol className="relative border-l border-border ml-4 space-y-8">
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
                  className={`absolute -left-3 flex items-center justify-center w-6 h-6 rounded-full border ${dotClass}`}
                >
                  <Icon className={`w-3 h-3 ${iconClass}`} />
                </span>
                <div className="flex flex-wrap items-baseline justify-between gap-2 mb-1">
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
                        className="ml-2 border-primary/40 text-primary text-[10px] uppercase tracking-wide"
                      >
                        Founder track
                      </Badge>
                    )}
                  </h3>
                  <span className="text-sm text-muted-foreground font-mono">
                    {e.period}
                  </span>
                </div>
                <p className="text-muted-foreground leading-relaxed">{e.note}</p>
              </li>
            );
          })}
        </ol>
      </section>

      {/*
        SELECTED PUBLIC WORK — Passport "show, don't tell" principle.
        Concrete artifacts a reader can click into and verify the claims
        on the rest of the page. Replaces the previous standalone blog
        pointer; blog is included as one of the cards.
      */}
      <section className="mt-24 max-w-5xl mx-auto">
        <h2 className="text-3xl font-bold mb-4">Selected public work</h2>
        <p className="text-lg text-muted-foreground mb-10">
          Don&apos;t take the resume on faith. Click in.
        </p>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {PUBLIC_WORK.map((work) => {
            const Icon = work.icon;
            return (
              <Card key={work.title} className="flex flex-col">
                <CardContent className="space-y-3 flex flex-col grow">
                  <div className="flex items-start gap-3">
                    <div className="rounded-md bg-primary/10 p-2 shrink-0">
                      <Icon className="w-5 h-5 text-primary" />
                    </div>
                    <h3 className="text-lg font-semibold leading-tight min-w-0 break-words">
                      {work.title}
                    </h3>
                  </div>
                  <p className="text-muted-foreground leading-relaxed text-sm grow">
                    {work.body}
                  </p>
                  <Button variant="outline" size="sm" asChild className="w-fit mt-2">
                    {work.external ? (
                      <a
                        href={work.href}
                        target="_blank"
                        rel="noopener noreferrer"
                      >
                        {work.cta}
                        <ExternalLink className="w-3 h-3 ml-2" />
                      </a>
                    ) : (
                      <Link href={work.href}>
                        {work.cta}
                        <ArrowRight className="w-3 h-3 ml-2" />
                      </Link>
                    )}
                  </Button>
                </CardContent>
              </Card>
            );
          })}
        </div>
      </section>

      {/* FINAL CTA */}
      <section className="mt-24 max-w-3xl mx-auto text-center space-y-6">
        <h2 className="text-3xl md:text-4xl font-bold">Get in touch</h2>
        <p className="text-lg text-muted-foreground">
          Email is the fastest way to reach me. Glad to hear from anyone
          building in this space.
        </p>
        <div className="flex flex-col sm:flex-row gap-3 justify-center pt-2">
          <Button size="lg" asChild>
            <a href={`mailto:${CONTACT_EMAIL}`}>
              <Mail className="w-4 h-4 mr-2" />
              {CONTACT_EMAIL}
            </a>
          </Button>
          <Button size="lg" variant="outline" asChild>
            <Link href="/speaking">
              Invite me to speak
              <ArrowRight className="w-4 h-4 ml-2" />
            </Link>
          </Button>
        </div>
      </section>
    </div>
  );
}
