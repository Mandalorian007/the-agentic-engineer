import Link from "next/link";
import { NewsletterForm } from "@/components/newsletter-form";
import { NEWSLETTER_NAME } from "@/lib/site";

interface NewsletterCtaProps {
  source: string;
  heading?: string;
  body?: string;
}

/**
 * Bordered newsletter block for use below content (post footers, blog index).
 * The hero on the homepage uses NewsletterForm directly, without the frame.
 */
export function NewsletterCta({
  source,
  heading = NEWSLETTER_NAME,
  body = "I\u2019m working out how to hand real engineering work to machines without it going badly. I\u2019m not done. Every other Monday: what I changed, what broke, and one thing you can paste into your own repo.",
}: NewsletterCtaProps) {
  return (
    <aside className="rounded-lg border bg-muted/40 p-6 md:p-8">
      <h2 className="text-xl font-bold md:text-2xl">{heading}</h2>
      <p className="mt-2 text-muted-foreground">{body}</p>
      <div className="mt-5 max-w-xl">
        <NewsletterForm source={source} />
        <p className="mt-2 text-sm text-muted-foreground">
          Every other Monday. Unsubscribe whenever. Your address goes to
          Buttondown and nowhere else, as described in the{" "}
          <Link href="/privacy" className="underline underline-offset-4">
            privacy policy
          </Link>
          .
        </p>
      </div>
    </aside>
  );
}
