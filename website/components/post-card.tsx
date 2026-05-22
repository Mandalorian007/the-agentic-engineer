import Link from "next/link";
import Image from "next/image";

interface PostCardProps {
  slug: string;
  title: string;
  description: string;
  date: string;
  categoryLabel: string;
  readingTime: string;
  heroImage?: string;
  priority?: boolean;
}

const DATE_FORMAT = new Intl.DateTimeFormat("en-US", {
  month: "short",
  day: "numeric",
  year: "numeric",
});

export function PostCard({
  slug,
  title,
  description,
  date,
  categoryLabel,
  readingTime,
  heroImage,
  priority = false,
}: PostCardProps) {
  const formattedDate = DATE_FORMAT.format(new Date(date));

  return (
    <Link
      href={`/blog/${slug}`}
      className="group relative block aspect-[4/3] overflow-hidden rounded-md ring-1 ring-border transition-all duration-300 hover:ring-foreground/30 hover:shadow-lg"
    >
      {/* Background image */}
      {heroImage ? (
        <Image
          src={heroImage}
          alt={title}
          fill
          priority={priority}
          sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 25vw"
          className="object-cover transition-transform duration-700 group-hover:scale-[1.05]"
        />
      ) : (
        <div className="absolute inset-0 bg-gradient-to-br from-muted via-muted/60 to-muted" />
      )}

      {/* Bottom gradient — extends on hover to make room for description */}
      <div className="absolute inset-x-0 bottom-0 h-1/2 bg-gradient-to-t from-black/95 via-black/55 to-transparent transition-[height] duration-300 group-hover:h-[78%]" />

      {/* Top-left category badge (always visible) */}
      <span className="absolute left-3 top-3 inline-flex items-center rounded-full bg-black/40 px-2.5 py-1 text-[10px] font-semibold uppercase tracking-[0.08em] text-white ring-1 ring-white/20 backdrop-blur-sm">
        {categoryLabel}
      </span>

      {/* Top-right reading time badge (always visible) */}
      <span className="absolute right-3 top-3 inline-flex items-center rounded-full bg-black/40 px-2.5 py-1 text-[10px] font-semibold uppercase tracking-[0.08em] text-white/90 ring-1 ring-white/20 backdrop-blur-sm">
        {readingTime}
      </span>

      {/* Bottom content stack */}
      <div className="absolute inset-x-0 bottom-0 p-4 sm:p-5">
        <h3 className="text-base font-semibold leading-snug text-white line-clamp-2 decoration-1 underline-offset-4 group-hover:underline sm:text-lg">
          {title}
        </h3>

        <div className="mt-1.5 flex items-end justify-between gap-3">
          <p className="line-clamp-1 flex-1 text-xs leading-relaxed text-white/85 transition-[max-height] duration-300 group-hover:line-clamp-none sm:text-[13px]">
            {description}
          </p>
          <time
            dateTime={date}
            className="shrink-0 text-[10px] font-semibold uppercase tracking-[0.08em] text-white/70"
          >
            {formattedDate}
          </time>
        </div>
      </div>
    </Link>
  );
}
