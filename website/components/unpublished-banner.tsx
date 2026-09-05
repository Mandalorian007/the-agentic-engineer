/**
 * Shown above content that is only visible because preview mode is on.
 *
 * Without it a scheduled post looks identical to a live one, which is the
 * quickest way to believe something shipped when it has not.
 */
export function UnpublishedBanner({
  label,
  date,
}: {
  label: string;
  date: string;
}) {
  const when = new Date(date).toLocaleDateString("en-US", {
    year: "numeric",
    month: "long",
    day: "numeric",
  });

  return (
    <div className="mb-8 rounded-lg border border-dashed border-amber-500/60 bg-amber-500/10 px-4 py-3 text-sm">
      <strong className="font-semibold">Preview.</strong> {label} {when}. This
      page is not public and is not indexed.
    </div>
  );
}
