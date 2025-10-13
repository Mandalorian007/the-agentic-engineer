import Link from "next/link";
import Image from "next/image";
import { RssIcon } from "lucide-react";

import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";

const NAVIGATION = [
  {
    title: "Content",
    links: [
      { name: "Home", href: "/" },
      { name: "Blog", href: "/blog" },
    ],
  },
  {
    title: "Legal",
    links: [
      { name: "Privacy", href: "/privacy" },
      { name: "Terms", href: "/terms" },
    ],
  },
];

const Footer16 = () => {
  const currentYear = new Date().getFullYear();

  return (
    <section className="bg-background pt-32">
      <footer className="container">
        <div className="grid gap-10 pb-6 md:grid-cols-2 md:pb-0">
          <div className="flex flex-col justify-start gap-8">
            {/* Logo/Brand */}
            <Link href="/" className="flex items-center gap-3">
              <Image
                src="/the-agentic-engineer-logo.webp"
                alt="The Agentic Engineer Logo"
                width={48}
                height={48}
                className="w-12 h-12"
              />
              <span className="text-2xl font-bold">The Agentic Engineer</span>
            </Link>
            <p className="text-muted-foreground text-sm max-w-md">
              Exploring AI agents, automation, and engineering with practical insights and real-world examples.
            </p>
            <Link
              href="/feed.xml"
              className="text-muted-foreground hover:text-foreground flex items-center gap-2 text-sm font-medium transition-colors duration-200 ease-in-out"
              target="_blank"
              rel="noopener noreferrer"
            >
              <RssIcon className="h-5 w-5" />
              Subscribe via RSS
            </Link>
          </div>
          <div>
            <div className="hidden md:flex md:gap-10 lg:gap-24 xl:gap-32">
              {NAVIGATION.map((section) => (
                <div className="flex flex-col gap-4" key={section.title}>
                  <h6 className="text-foreground mb-2 text-sm font-semibold uppercase">
                    {section.title}
                  </h6>
                  {section.links.map((link) => (
                    <Link
                      className="text-muted-foreground hover:text-foreground text-sm font-medium transition-colors duration-200 ease-in-out"
                      key={link.name}
                      href={link.href}
                    >
                      {link.name}
                    </Link>
                  ))}
                </div>
              ))}
            </div>
            <div className="md:hidden">
              <Accordion type="single" collapsible className="w-full">
                {NAVIGATION.map((section, i) => (
                  <AccordionItem value={`item-${i}`} key={section.title}>
                    <AccordionTrigger className="text-foreground py-4 text-sm uppercase hover:no-underline">
                      {section.title}
                    </AccordionTrigger>
                    <AccordionContent className="flex flex-col gap-2">
                      {section.links.map((link) => (
                        <Link
                          className="text-muted-foreground hover:text-foreground text-sm font-medium transition-colors duration-200 ease-in-out"
                          key={link.name}
                          href={link.href}
                        >
                          {link.name}
                        </Link>
                      ))}
                    </AccordionContent>
                  </AccordionItem>
                ))}
              </Accordion>
            </div>
          </div>
        </div>
        <div className="border-t mt-12 pt-8 pb-8">
          <p className="text-muted-foreground text-center text-sm">
            © {currentYear} The Agentic Engineer. All rights reserved.
          </p>
        </div>
      </footer>
    </section>
  );
};

export { Footer16 };
