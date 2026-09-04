import type { Metadata } from "next";
import { CheckCircle2, XCircle, Mic, Users, Sparkles, Mail } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { AUTHOR, SITE_NAME, SITE_URL } from "@/lib/site";

const CONTACT_EMAIL = AUTHOR.email;

const SERVICES_TITLE = "Hire me for something specific";
const SERVICES_DESCRIPTION =
  "Speaking, team training, and one-off advisory on encoding your own expertise into agent workflows. Bounded engagements, not twelve-week transformations.";

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

const OFFERINGS = [
  {
    icon: Mic,
    title: "Speaking",
    body: "Conferences, internal tech talks, podcasts. Usually on encoding your expertise into agent workflows.",
    scope: "Per event",
  },
  {
    icon: Users,
    title: "Team training",
    body: "A working session with your team on encoding your own workflows into agents.",
    scope: "Half day to two",
  },
  {
    icon: Sparkles,
    title: "Something else",
    body: "An advisory call, a review of what you've built, a weird problem nobody else wants. Ask.",
    scope: "Depends",
  },
];

const GOOD_FIT = [
  "Engineers already using agents, no shared idea of how",
  "You want the team leaving with something they can use Monday",
  "You can name the thing that's actually slow",
];

const NOT_A_FIT = [
  "You want someone to own your AI strategy for a year",
  "You want a vendor pick and a procurement doc signed",
  "You're hoping headcount goes down",
];

// Structured data for the hire-me page. Carried over from the previous
// /speaking + /services pair, retargeted at the bounded engagements below.
const SERVICES_JSON_LD = {
  "@context": "https://schema.org",
  "@type": "ProfessionalService",
  name: SITE_NAME,
  url: `${SITE_URL}/services`,
  description: SERVICES_DESCRIPTION,
  image: `${SITE_URL}/the-agentic-engineer-logo.webp`,
  email: CONTACT_EMAIL,
  // Explicit rather than derived from OFFERINGS: "Something else" is a fine
  // heading for a human and useless as a machine-readable service type.
  serviceType: [
    "Conference and podcast speaking",
    "Engineering team training",
    "Technical advisory",
  ],
  areaServed: [
    { "@type": "Country", name: "United States" },
    { "@type": "Place", name: "Remote, worldwide" },
  ],
  provider: {
    "@type": "Person",
    name: AUTHOR.name,
    email: AUTHOR.email,
    url: AUTHOR.url,
    jobTitle: AUTHOR.role,
    sameAs: [AUTHOR.linkedin, AUTHOR.github],
  },
};

export default function ServicesPage() {
  return (
    <div className="container py-12 md:py-20">
      {/* Intro */}
      <section className="max-w-3xl">
        <h1 className="text-4xl font-bold tracking-tight md:text-5xl">
          Hire me for something specific
        </h1>
        <p className="mt-6 text-xl text-muted-foreground">
          I have a day job I like. I&rsquo;m not going to run a twelve-week
          transformation for you. What I will do is show up for something
          bounded, do it well, and go home.
        </p>
      </section>

      {/* Offerings */}
      <section className="mt-16">
        <div className="grid grid-cols-1 gap-6 md:grid-cols-3">
          {OFFERINGS.map((offering) => (
            <Card key={offering.title} className="size-full">
              <CardContent className="flex h-full flex-col gap-4 p-6">
                <offering.icon className="h-6 w-6 text-primary" />
                <h2 className="text-xl font-semibold">{offering.title}</h2>
                <p className="text-muted-foreground">{offering.body}</p>
                <p className="mt-auto pt-2 text-sm font-medium text-muted-foreground">
                  {offering.scope}
                </p>
              </CardContent>
            </Card>
          ))}
        </div>
      </section>

      {/* Fit */}
      <section className="mt-20">
        <div className="grid grid-cols-1 gap-10 md:grid-cols-2 md:gap-16">
          <div>
            <h2 className="text-2xl font-bold">A good fit</h2>
            <ul className="mt-6 space-y-4">
              {GOOD_FIT.map((item) => (
                <li key={item} className="flex gap-3">
                  <CheckCircle2 className="mt-0.5 h-5 w-5 shrink-0 text-primary" />
                  <span>{item}</span>
                </li>
              ))}
            </ul>
          </div>
          <div>
            <h2 className="text-2xl font-bold">Not a fit</h2>
            <ul className="mt-6 space-y-4">
              {NOT_A_FIT.map((item) => (
                <li key={item} className="flex gap-3">
                  <XCircle className="mt-0.5 h-5 w-5 shrink-0 text-muted-foreground" />
                  <span className="text-muted-foreground">{item}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </section>

      {/* Contact */}
      <section className="mt-20 border-t pt-12">
        <div className="mx-auto max-w-2xl text-center">
          <h2 className="text-2xl font-bold">
            Email me and describe the problem in a paragraph.
          </h2>
          <div className="mt-6">
            <Button size="lg" asChild>
              <a href={`mailto:${CONTACT_EMAIL}`}>
                <Mail className="mr-2 h-4 w-4" />
                {CONTACT_EMAIL}
              </a>
            </Button>
          </div>
          <p className="mt-6 text-muted-foreground">
            I answer everything. If it&rsquo;s not a fit I&rsquo;ll say so and
            try to point you at someone better.
          </p>
        </div>
      </section>

      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(SERVICES_JSON_LD) }}
      />
    </div>
  );
}
