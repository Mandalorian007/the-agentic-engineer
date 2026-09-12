import type { Metadata } from "next";
import { CheckCircle2, XCircle, Mic, Users, Mail } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { AUTHOR } from "@/lib/site";

const CONTACT_EMAIL = AUTHOR.email;

const PAGE_TITLE = "Talks and workshops";
const PAGE_DESCRIPTION =
  "Talks and one-off workshops on running agents in production: the platform layer, what an agent may touch, and how you know it did the right thing. Bounded. Not a consulting practice.";

export const metadata: Metadata = {
  title: PAGE_TITLE,
  description: PAGE_DESCRIPTION,
  alternates: { canonical: "/speaking" },
  openGraph: {
    title: PAGE_TITLE,
    description: PAGE_DESCRIPTION,
    url: "/speaking",
    type: "website",
    images: [{ url: "/og", width: 1200, height: 630, alt: PAGE_TITLE }],
  },
  twitter: {
    card: "summary_large_image",
    title: PAGE_TITLE,
    description: PAGE_DESCRIPTION,
    images: ["/og"],
  },
};

// What I actually give talks about. Each one is a claim, not a topic, because
// a program committee books a position and an audience remembers one.
const TALKS = [
  {
    title: "Agents past the engineering org",
    body: "Running an agentic platform where the users are recruiters, pharmacists, and ops teams, and PHI is in the loop. What changes when the platform acts instead of waiting to be called.",
  },
  {
    title: "Control is how you go faster",
    body: "Hooks, permission boundaries, and evals that gate what ships. The guardrails that let you hand real work to an agent and walk away from the desk.",
  },
  {
    title: "Build the system that builds the product",
    body: "Encoding your own workflow into skills, subagents, hooks, and commands. The Claude Code plugin pattern, from one engineer's setup to a company standard.",
  },
];

const FORMATS = [
  {
    icon: Mic,
    title: "Talk",
    body: "Conference, meetup, internal tech talk, podcast. Thirty to forty-five minutes plus questions.",
    scope: "Per event",
  },
  {
    icon: Users,
    title: "Workshop",
    body: "A half day with your team, hands on keyboard, leaving with hooks and commands they can use Monday.",
    scope: "Half day, once",
  },
];

const GOOD_FIT = [
  "Engineers already using agents, no shared idea of how",
  "A team that wants to leave with something they can run Monday",
  "An audience that will argue back",
];

const NOT_A_FIT = [
  "Someone to own your AI strategy for a year",
  "A vendor pick and a procurement doc signed",
  "An ongoing retainer of any shape",
];

export default function SpeakingPage() {
  return (
    <div className="container py-12 md:py-20">
      {/* Intro */}
      <section className="max-w-3xl">
        <h1 className="text-4xl font-bold tracking-tight md:text-5xl">
          {PAGE_TITLE}
        </h1>
        <p className="mt-6 text-xl text-muted-foreground">
          I run AI strategy and the agentic platform at a healthcare startup.
          That is the job. On the side I give talks and the occasional
          workshop about how it actually works, because saying it out loud to
          a room that argues back is how I find out what I believe.
        </p>
        <p className="mt-4 text-xl text-muted-foreground">
          Bounded, by design. I show up, do the thing well, and go home.
        </p>
      </section>

      {/* Talks */}
      <section className="mt-16 max-w-3xl">
        <h2 className="text-2xl font-bold">What I talk about</h2>
        <ul className="mt-6 space-y-6">
          {TALKS.map((talk) => (
            <li key={talk.title}>
              <h3 className="text-lg font-semibold">{talk.title}</h3>
              <p className="mt-1 text-muted-foreground">{talk.body}</p>
            </li>
          ))}
        </ul>
      </section>

      {/* Formats */}
      <section className="mt-16">
        <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
          {FORMATS.map((format) => (
            <Card key={format.title} className="size-full">
              <CardContent className="flex h-full flex-col gap-4 p-6">
                <format.icon className="h-6 w-6 text-primary" />
                <h2 className="text-xl font-semibold">{format.title}</h2>
                <p className="text-muted-foreground">{format.body}</p>
                <p className="mt-auto pt-2 text-sm font-medium text-muted-foreground">
                  {format.scope}
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
            Email me the event, the audience, and the date.
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
    </div>
  );
}
