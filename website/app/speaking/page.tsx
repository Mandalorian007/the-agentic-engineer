import Link from "next/link";
import type { Metadata } from "next";
import {
  ArrowRight,
  Mail,
  Mic,
  Podcast,
  Presentation,
  Users,
  Sparkles,
} from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { AUTHOR_NAME, CONTACT_EMAIL, CREDENTIAL_LINE } from "@/lib/bio";

const SPEAKING_TITLE = "Speaking";
const SPEAKING_DESCRIPTION =
  "Open to podcast appearances, conference CFPs, and internal engineering talks on agentic developer platforms, MCP, evaluation discipline, and the agentic SDLC.";

export const metadata: Metadata = {
  title: SPEAKING_TITLE,
  description: SPEAKING_DESCRIPTION,
  alternates: { canonical: "/speaking" },
  openGraph: {
    title: SPEAKING_TITLE,
    description: SPEAKING_DESCRIPTION,
    url: "/speaking",
    type: "website",
    images: [{ url: "/og", width: 1200, height: 630, alt: SPEAKING_TITLE }],
  },
  twitter: {
    card: "summary_large_image",
    title: SPEAKING_TITLE,
    description: SPEAKING_DESCRIPTION,
    images: ["/og"],
  },
};

const TOPIC_SEEDS = [
  "Why most AI adoption is blocked on evaluation discipline, not training or culture",
  "Tool choice (Claude Code, Codex, Cursor) matters less than platform strategy",
  "The shift from MCP servers to skills, and what each is actually good for",
  "Portable toolkits and escaping AI ecosystem lock-in",
  "What changes when an agent is a first-class user of your platform",
  "Reading evals like a senior engineer reads tests",
];

export default function SpeakingPage() {
  return (
    <div className="container py-12 md:py-20">
      {/* Hero */}
      <section className="max-w-3xl mx-auto text-center space-y-6">
        <Badge variant="outline" className="mx-auto">
          Speaking
        </Badge>
        <h1 className="text-4xl md:text-6xl font-bold tracking-tight">
          Speaking.
        </h1>
        <p className="text-xl text-muted-foreground">
          I talk publicly about agentic developer platforms, MCP, evaluation
          discipline, and the agentic SDLC. Open to guest spots, CFP
          collaborations, and internal engineering talks.
        </p>
        <p className="text-sm text-muted-foreground">
          By{" "}
          <Link
            href="/about"
            className="font-medium text-foreground underline underline-offset-4 hover:no-underline"
          >
            {AUTHOR_NAME}
          </Link>{" "}
          · {CREDENTIAL_LINE}
        </p>
        <div className="flex flex-col sm:flex-row gap-3 justify-center pt-2">
          <Button size="lg" asChild>
            <a
              href={`mailto:${CONTACT_EMAIL}?subject=Speaking%20invitation`}
            >
              <Mail className="w-4 h-4 mr-2" />
              Invite me to speak
            </a>
          </Button>
          <Button size="lg" variant="outline" asChild>
            <Link href="/blog">
              Read recent posts
              <ArrowRight className="w-4 h-4 ml-2" />
            </Link>
          </Button>
        </div>
      </section>

      {/* Podcasts */}
      <section className="mt-24 max-w-4xl mx-auto">
        <div className="flex items-center gap-3 mb-4">
          <div className="rounded-md bg-primary/10 p-2.5">
            <Podcast className="w-5 h-5 text-primary" />
          </div>
          <h2 className="text-3xl font-bold">Podcasts</h2>
        </div>
        <p className="text-lg text-muted-foreground mb-8">
          Open to guest appearances. Recent threads I&apos;ve been thinking
          about and would happily ruin a recording over:
        </p>
        <Card>
          <CardContent className="p-6">
            <ul className="space-y-3">
              {TOPIC_SEEDS.map((seed) => (
                <li key={seed} className="flex items-start gap-3">
                  <Sparkles className="w-4 h-4 text-primary mt-1 shrink-0" />
                  <span className="text-muted-foreground leading-relaxed">
                    {seed}
                  </span>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      </section>

      {/* Conferences */}
      <section className="mt-20 max-w-4xl mx-auto">
        <div className="flex items-center gap-3 mb-4">
          <div className="rounded-md bg-primary/10 p-2.5">
            <Presentation className="w-5 h-5 text-primary" />
          </div>
          <h2 className="text-3xl font-bold">Conferences</h2>
        </div>
        <p className="text-lg text-muted-foreground">
          Open to CFP collaborations and conference talks, technical or
          strategic stages. Happy to co-submit with program chairs or
          partner orgs.
        </p>
      </section>

      {/* Internal talks */}
      <section className="mt-20 max-w-4xl mx-auto">
        <div className="flex items-center gap-3 mb-4">
          <div className="rounded-md bg-primary/10 p-2.5">
            <Users className="w-5 h-5 text-primary" />
          </div>
          <h2 className="text-3xl font-bold">Internal talks &amp; workshops</h2>
        </div>
        <p className="text-lg text-muted-foreground">
          Available for engineering org talks on agentic tooling adoption,
          evaluation discipline, and developer platform strategy. Format ranges
          from a 30-minute keynote at an internal eng all-hands to a half-day
          workshop with your platform team.
        </p>
      </section>

      {/* Final CTA */}
      <section className="mt-24 max-w-3xl mx-auto text-center space-y-6">
        <div className="flex items-center justify-center gap-3">
          <Mic className="w-6 h-6 text-primary" />
          <h2 className="text-3xl md:text-4xl font-bold">Want to talk?</h2>
        </div>
        <p className="text-lg text-muted-foreground">
          Email is the fastest path. Tell me about the audience, the format,
          and the angle you&apos;re after. If it&apos;s a fit, we&apos;ll
          figure out the rest.
        </p>
        <div className="flex flex-col sm:flex-row gap-3 justify-center pt-2">
          <Button size="lg" asChild>
            <a
              href={`mailto:${CONTACT_EMAIL}?subject=Speaking%20invitation`}
            >
              <Mail className="w-4 h-4 mr-2" />
              {CONTACT_EMAIL}
            </a>
          </Button>
          <Button size="lg" variant="outline" asChild>
            <Link href="/about">
              More about me
              <ArrowRight className="w-4 h-4 ml-2" />
            </Link>
          </Button>
        </div>
      </section>
    </div>
  );
}
