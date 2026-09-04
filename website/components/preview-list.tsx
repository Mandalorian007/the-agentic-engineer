import Link from "next/link";

export interface PreviewItem {
  slug: string;
  title: string;
  href: string;
  /** The date this becomes public. */
  date: string;
}

/**
 * Scheduled content, listed only while preview mode is on.
 *
 * Kept visually separate from the real listing rather than mixed into it. The
 * whole point of looking at a scheduled post is to check it before it is live,
 * which is hard to do if you cannot tell which ones those are.
 */
export function PreviewList({
  heading,
  emptyLabel,
  items,
}: {
  heading: string;
  emptyLabel: string;
  items: PreviewItem[];
}) {
  if (items.length === 0) {
    return null;
  }

  return (
    <section className="mt-16 rounded-lg border border-dashed border-amber-500/60 bg-amber-500/5 p-6">
      <h2 className="text-sm font-semibold uppercase tracking-wide">
        {heading}
      </h2>
      <p className="mt-1 text-sm text-muted-foreground">{emptyLabel}</p>
      <ul className="mt-4 space-y-2">
        {items.map((item) => (
          <li key={item.slug} className="text-sm">
            <Link
              href={item.href}
              className="font-medium underline underline-offset-4"
            >
              {item.title}
            </Link>
            <span className="ml-2 text-muted-foreground">
              {new Date(item.date).toLocaleDateString("en-US", {
                year: "numeric",
                month: "short",
                day: "numeric",
              })}
            </span>
          </li>
        ))}
      </ul>
    </section>
  );
}
