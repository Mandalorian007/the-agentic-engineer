import { ArrowRight } from "lucide-react";
import Image from "next/image";

import { AspectRatio } from "@/components/ui/aspect-ratio";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";

interface BlogCardProps {
  category: string;
  title: string;
  summary: string;
  link: string;
  cta: string;
  thumbnail: string;
  readingTime?: string;
  isPrimary?: boolean;
}

export const BlogCard = ({ category, title, thumbnail, summary, link, cta, readingTime, isPrimary = false }: BlogCardProps) => {
  /**
   * Format category ID to display name
   * Examples:
   *   "case-studies" -> "Case Studies"
   *   "tutorials" -> "Tutorials"
   *   "problem-solution" -> "Problem Solution"
   */
  const formatCategory = (cat: string): string => {
    return cat
      .split('-')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

  return (
    <a href={link} className="block h-full w-full">
      <Card className="size-full rounded-lg border py-0">
        <CardContent className="p-0">
          <div className="text-muted-foreground border-b p-2.5 text-sm font-medium leading-[1.2]">
            {formatCategory(category)}
          </div>
          <AspectRatio ratio={1.520833333} className="overflow-hidden">
            <Image
              src={thumbnail}
              alt={title}
              fill
              className="object-cover object-center"
              priority={isPrimary}
              sizes={isPrimary ? "(max-width: 1024px) 100vw, 440px" : "(max-width: 768px) 100vw, (max-width: 1024px) 50vw, 33vw"}
            />
          </AspectRatio>
          <div className="flex w-full flex-col gap-5 p-5">
            <h2 className="text-lg font-medium leading-tight md:text-xl">
              {title}
            </h2>
            <div className="w-full max-w-[20rem]">
              <p className="text-muted-foreground text-sm font-medium leading-[1.4]">
                {summary}
              </p>
            </div>
            <div className="flex items-center justify-between">
              <Button size="sm" variant="outline">
                {cta}
                <ArrowRight />
              </Button>
              {readingTime && (
                <span className="text-xs text-muted-foreground">
                  {readingTime}
                </span>
              )}
            </div>
          </div>
        </CardContent>
      </Card>
    </a>
  );
};
