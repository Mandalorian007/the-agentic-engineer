import Link from "next/link";
import Image from "next/image";
import { ArrowRight, Building2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { AUTHOR_NAME, CREDENTIAL_LINE } from "@/lib/bio";

export function AuthorBio() {
  return (
    <Card className="not-prose">
      <CardContent className="p-6 flex flex-col sm:flex-row gap-5 items-start">
        <div className="relative h-14 w-14 shrink-0 overflow-hidden rounded-full border bg-muted">
          <Image
            src="/about/matthew-fontana.jpeg"
            alt={AUTHOR_NAME}
            fill
            sizes="56px"
            className="object-cover object-center"
          />
        </div>
        <div className="flex-1 space-y-3 min-w-0">
          <div>
            <div className="flex items-center gap-2 text-xs uppercase tracking-wide text-muted-foreground font-semibold">
              <Building2 className="w-3 h-3" />
              About the author
            </div>
            <h3 className="text-lg font-semibold mt-1">{AUTHOR_NAME}</h3>
            <p className="text-sm text-muted-foreground">{CREDENTIAL_LINE}</p>
          </div>
          <p className="text-sm text-muted-foreground leading-relaxed">
            I build agentic developer platforms inside large engineering orgs
            and write here about the work.
          </p>
          <div className="flex flex-wrap gap-2 pt-1">
            <Button size="sm" asChild>
              <Link href="/about">
                More about me
                <ArrowRight className="w-3 h-3 ml-1.5" />
              </Link>
            </Button>
            <Button size="sm" variant="outline" asChild>
              <Link href="/services">
                Work with me
                <ArrowRight className="w-3 h-3 ml-1.5" />
              </Link>
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
