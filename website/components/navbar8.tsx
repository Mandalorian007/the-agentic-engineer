"use client";
import { Menu, X } from "lucide-react";
import Link from "next/link";
import Image from "next/image";
import { Dispatch, SetStateAction, useEffect, useRef, useState } from "react";
import {
  SignInButton,
  SignUpButton,
  SignedIn,
  SignedOut,
  UserButton,
} from "@clerk/nextjs";

import { Button } from "@/components/ui/button";
import {
  NavigationMenu,
  NavigationMenuItem,
  NavigationMenuLink,
  NavigationMenuList,
  navigationMenuTriggerStyle,
} from "@/components/ui/navigation-menu";
import {
  Sheet,
  SheetClose,
  SheetContent,
  SheetTitle,
} from "@/components/ui/sheet";
import { ThemeToggle } from "@/components/theme-toggle";

interface MenuItem {
  title: string;
  url: string;
}

interface MobileNavigationMenuProps {
  open: boolean;
  setOpen: Dispatch<SetStateAction<boolean>>;
}

const LOGO = {
  title: "The Agentic Engineer",
  url: "/",
};

const NAVIGATION: MenuItem[] = [
  {
    title: "Home",
    url: "/",
  },
  {
    title: "Blog",
    url: "/blog",
  },
];

const MOBILE_BREAKPOINT = 1024;

const Navbar8 = () => {
  const [open, setOpen] = useState<boolean>(false);
  const navRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth > MOBILE_BREAKPOINT) {
        setOpen(false);
      }
    };

    const handleScroll = () => {
      navRef.current?.classList.toggle("bg-background", window.scrollY > 50);
      navRef.current?.classList.toggle(
        "bg-transparent",
        !(window.scrollY > 50),
      );
    };

    handleResize();
    handleScroll();

    window.addEventListener("resize", handleResize);
    window.addEventListener("scroll", handleScroll);
    return () => {
      window.removeEventListener("resize", handleResize);
      window.removeEventListener("scroll", handleScroll);
    };
  }, []);

  useEffect(() => {
    document.body.style.overflow = open ? "hidden" : "auto";
  }, [open]);

  const handleMobileMenu = () => {
    const nextOpen = !open;
    setOpen(nextOpen);
  };

  return (
    <section>
      <div
        className="z-40 fixed top-0 w-full bg-transparent transition-colors duration-500"
        ref={navRef}
      >
        <div className="container border-b">
          <div className="flex items-center justify-between gap-3.5 py-5">
            <Link
              href={LOGO.url}
              className="flex items-center gap-3 text-lg font-semibold tracking-tight"
            >
              <Image
                src="/the-agentic-engineer-logo.webp"
                alt="The Agentic Engineer Logo"
                width={40}
                height={40}
                className="w-10 h-10"
              />
              <span>{LOGO.title}</span>
            </Link>
            <NavigationMenu className="hidden lg:flex">
              <NavigationMenuList>
                {NAVIGATION.map((item, index) => (
                  <NavigationMenuItem
                    key={`desktop-menu-item-${index}`}
                    value={`${index}`}
                    className={`${navigationMenuTriggerStyle()} bg-transparent`}
                  >
                    <NavigationMenuLink href={item.url}>
                      {item.title}
                    </NavigationMenuLink>
                  </NavigationMenuItem>
                ))}
              </NavigationMenuList>
            </NavigationMenu>
            <div className="flex items-center gap-3.5">
              <ThemeToggle />
              <SignedOut>
                <SignInButton mode="modal">
                  <Button variant="ghost" size="sm" className="hidden md:flex">
                    Log in
                  </Button>
                </SignInButton>
                <SignUpButton mode="modal">
                  <Button size="sm" className="hidden md:flex">
                    Sign up
                  </Button>
                </SignUpButton>
              </SignedOut>
              <SignedIn>
                <UserButton
                  appearance={{
                    elements: {
                      avatarBox: "size-9",
                    },
                  }}
                />
              </SignedIn>
              <div className="lg:hidden">
                <Button variant="ghost" size="icon" onClick={handleMobileMenu}>
                  <Menu className="size-5.5" />
                </Button>
              </div>
            </div>
          </div>
        </div>
      </div>
      <MobileNavigationMenu open={open} setOpen={setOpen} />
    </section>
  );
};

const MobileNavigationMenu = ({ open, setOpen }: MobileNavigationMenuProps) => {
  return (
    <Sheet open={open} onOpenChange={setOpen}>
      <SheetContent
        aria-describedby={undefined}
        side="top"
        className="z-600 bg-primary text-primary-foreground inset-0 h-dvh w-full [&>button]:hidden"
      >
        <div className="flex-1 overflow-y-auto">
          <div className="container pb-12">
            <div className="mask-clip-border absolute -m-px h-px w-px overflow-hidden whitespace-nowrap text-nowrap border-0 p-0">
              <SheetTitle className="text-primary">
                Mobile Navigation
              </SheetTitle>
            </div>
            <div className="flex justify-end pt-5">
              <SheetClose asChild>
                <Button
                  size="icon"
                  className="bg-muted/20 hover:bg-muted/20 size-9 rounded-full"
                >
                  <X className="size-5.5" />
                </Button>
              </SheetClose>
            </div>
            <div className="gap-30 flex h-full flex-col justify-between pt-24">
              <div className="flex w-full flex-col gap-8">
                {NAVIGATION.map((item, index) => (
                  <Link
                    key={`mobile-nav-link-${index}`}
                    href={item.url}
                    className="text-primary-foreground text-2xl font-medium leading-normal"
                    onClick={() => setOpen(false)}
                  >
                    {item.title}
                  </Link>
                ))}
              </div>
              <div className="flex flex-col gap-4 pt-8">
                <SignedOut>
                  <SignInButton mode="modal">
                    <Button variant="outline" size="lg">
                      Log in
                    </Button>
                  </SignInButton>
                  <SignUpButton mode="modal">
                    <Button size="lg">Sign up</Button>
                  </SignUpButton>
                </SignedOut>
                <SignedIn>
                  <div className="flex items-center gap-3">
                    <UserButton
                      appearance={{
                        elements: {
                          avatarBox: "size-10",
                        },
                      }}
                    />
                    <span className="text-primary-foreground text-lg">
                      Account
                    </span>
                  </div>
                </SignedIn>
              </div>
            </div>
          </div>
        </div>
      </SheetContent>
    </Sheet>
  );
};

export { Navbar8 };
