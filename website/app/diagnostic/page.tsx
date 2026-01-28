import { Metadata } from "next";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { AlertTriangle, CheckCircle2 } from "lucide-react";
import { WaitlistForm } from "@/components/waitlist-form";

export const metadata: Metadata = {
  title: "AI Workflow Reliability Diagnostic | Agentic Engineer",
  description:
    "8 mechanism-level questions that surface where your workflow can safely automate—and where it can't. Constraint-driven analysis for AI reliability.",
};

export default function DiagnosticPage() {
  return (
    <div className="container py-12 md:py-20">
      <div className="max-w-3xl mx-auto">
        {/* Header */}
        <div className="mb-12">
          <h1 className="text-3xl md:text-4xl font-bold tracking-tight mb-4">
            AI Workflow Reliability Diagnostic
          </h1>
          <p className="text-xl text-muted-foreground">
            A practical framework for understanding where automation is safe—and
            where it isn&apos;t.
          </p>
        </div>

        {/* Core Principle */}
        <section className="mb-12">
          <h2 className="text-xl font-semibold mb-4">Core Principle</h2>
          <p className="text-muted-foreground mb-6">
            Reliable AI automation is constrained by mechanics, not beliefs.
            This diagnostic extracts those constraints directly:
          </p>
          <div className="grid gap-3 sm:grid-cols-2">
            {[
              "Irreversibility",
              "Detection speed",
              "Retry safety",
              "Unwritten knowledge",
              "Recovery mechanics",
            ].map((constraint) => (
              <div key={constraint} className="flex items-center gap-2">
                <CheckCircle2 className="h-4 w-4 text-primary shrink-0" />
                <span className="text-sm">{constraint}</span>
              </div>
            ))}
          </div>
        </section>

        {/* The 8 Questions */}
        <section className="mb-12">
          <h2 className="text-xl font-semibold mb-6">
            The 8 Questions
          </h2>
          <div className="space-y-6">
            <QuestionCard
              number={1}
              title="Irreversibility"
              question="What is the first irreversible action in the workflow?"
              examples="Schema change, prod deploy, data rewrite, API contract break"
              insight="This defines the hard stop for autonomous execution."
            />
            <QuestionCard
              number={2}
              title="Error Detection"
              question="What signal tells you an irreversible mistake occurred?"
              examples="Automated validation, monitoring/alerts, customer impact, none until later"
              insight="This reveals how long mistakes stay hidden."
            />
            <QuestionCard
              number={3}
              title="Drift Window"
              question="How many steps typically occur between the mistake and detection?"
              examples="0-1, 2-5, 10+"
              insight="This quantifies how far AI can drift before correction."
            />
            <QuestionCard
              number={4}
              title="Retry Safety"
              question="Which specific step cannot be safely retried without human intervention?"
              examples="Name the step explicitly"
              insight="This shows where humans must approve before continuing."
            />
            <QuestionCard
              number={5}
              title="Unwritten Knowledge"
              question="What information does a human reviewer rely on that is not written down anywhere?"
              examples="Architectural intent, historical exceptions, business constraints, informal conventions"
              insight="This finds what AI cannot see."
            />
            <QuestionCard
              number={6}
              title="Recovery Mechanics"
              question="When this workflow fails today, what is the actual recovery action?"
              examples="Revert, patch forward, manual correction, full rollback"
              insight="This determines whether automation failure is survivable."
            />
            <QuestionCard
              number={7}
              title="Throughput Bottleneck"
              question="Which step causes the longest delay, even when nothing goes wrong?"
              examples="Waiting for review, reruns/flakiness, debugging, coordination"
              insight="This separates throughput pain from correctness risk."
            />
            <QuestionCard
              number={8}
              title="Likely Failure Mode"
              question="If this workflow ran unattended for 100 steps, what would fail first?"
              examples="Correctness, safety, trust, performance"
              insight="This reveals the true limiting factor of automation."
            />
          </div>
        </section>

        {/* What You Get */}
        <section className="mb-12">
          <h2 className="text-xl font-semibold mb-6">Diagnostic Insights</h2>
          <div className="space-y-4">
            <InsightCard
              title="Automation Boundary"
              description="Clear understanding of where autonomous execution must stop. All prior steps must be stateless and reversible."
            />
            <InsightCard
              title="Mandatory Checkpoints"
              description="If mistakes take more than one step to catch, one-shot attempts become unsafe. You need multiple runs and comparison."
            />
            <InsightCard
              title="Unwritten Knowledge"
              description="Knowledge that only exists in people's heads blocks full automation. Those rules need to be captured earlier in the process."
            />
            <InsightCard
              title="Recovery Cost Analysis"
              description="Manual recovery makes silent failure unacceptable. When uncertain, AI should hold back rather than act and break things."
            />
            <InsightCard
              title="Trust Bottleneck Identification"
              description="Even correct outputs stall without predictable behavior. Human confidence, not model accuracy, limits throughput."
            />
          </div>
        </section>

        {/* CTA */}
        <section className="border rounded-lg p-6 bg-muted/30">
          <div className="flex items-start gap-3 mb-4">
            <AlertTriangle className="h-5 w-5 text-amber-500 mt-0.5 shrink-0" />
            <div>
              <p className="font-medium mb-2">
                This diagnostic doesn&apos;t ask what you believe AI can do.
              </p>
              <p className="text-muted-foreground">
                It asks: &ldquo;Where does reality refuse to let automation
                proceed safely?&rdquo; That answer is sufficient to design a
                reliable system.
              </p>
            </div>
          </div>
          <div className="mt-6 pt-6 border-t space-y-4">
            <p className="font-medium">
              Get notified when the framework launches
            </p>
            <WaitlistForm />
          </div>
        </section>
      </div>
    </div>
  );
}

function QuestionCard({
  number,
  title,
  question,
  examples,
  insight,
}: {
  number: number;
  title: string;
  question: string;
  examples: string;
  insight: string;
}) {
  return (
    <Card>
      <CardHeader className="pb-3">
        <div className="flex items-center gap-3">
          <span className="flex items-center justify-center h-7 w-7 rounded-full bg-primary text-primary-foreground text-sm font-medium">
            {number}
          </span>
          <CardTitle className="text-lg">{title}</CardTitle>
        </div>
      </CardHeader>
      <CardContent className="space-y-3">
        <p className="font-medium">{question}</p>
        <p className="text-sm text-muted-foreground">
          <span className="font-medium">Examples:</span> {examples}
        </p>
        <p className="text-sm text-muted-foreground border-l-2 border-primary/50 pl-3 italic">
          {insight}
        </p>
      </CardContent>
    </Card>
  );
}

function InsightCard({
  title,
  description,
}: {
  title: string;
  description: string;
}) {
  return (
    <div className="flex gap-3">
      <CheckCircle2 className="h-5 w-5 text-primary mt-0.5 shrink-0" />
      <div>
        <p className="font-medium">{title}</p>
        <p className="text-sm text-muted-foreground">{description}</p>
      </div>
    </div>
  );
}
