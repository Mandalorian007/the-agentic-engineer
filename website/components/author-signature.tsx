import Image from "next/image";
import Link from "next/link";
import { AUTHOR, AUTHOR_SIGNATURE } from "@/lib/site";

/**
 * Sign-off block for the end of a post.
 *
 * A reader who just spent ten minutes inside an argument should be able to see
 * whose argument it was without hunting for the nav. This is the web version;
 * the email version of the same sign-off lives in the Buttondown template,
 * since the feed only carries post body content.
 */
export function AuthorSignature() {
  return (
    <div className="flex items-center gap-4">
      <Link href="/about" className="shrink-0" aria-label={`About ${AUTHOR.name}`}>
        <span className="relative block size-14 overflow-hidden rounded-full border bg-muted">
          <Image
            src={AUTHOR.avatar}
            alt={AUTHOR.name}
            fill
            sizes="56px"
            className="object-cover object-center"
          />
        </span>
      </Link>
      <div className="space-y-1">
        <Link href="/about" className="font-semibold hover:underline">
          {AUTHOR_SIGNATURE}
        </Link>
        <p className="text-sm text-muted-foreground">
          {AUTHOR.role}, writing from {AUTHOR.location}. Everything here is
          something I actually run.
        </p>
      </div>
    </div>
  );
}
