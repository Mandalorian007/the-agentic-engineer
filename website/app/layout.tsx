import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { Navbar8 } from "@/components/navbar8";
import { Footer16 } from "@/components/footer16";
import { ThemeProvider } from "@/components/theme-provider";
import { ClerkProvider } from "@clerk/nextjs";
import { shadcn } from "@clerk/themes";
import { Analytics } from "@vercel/analytics/next";
import { SpeedInsights } from "@vercel/speed-insights/next";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "The Agentic Engineer",
  description: "Exploring AI agents, automation, and engineering with practical insights and real-world examples.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <ClerkProvider
      appearance={{
        baseTheme: shadcn,
      }}
    >
      <html lang="en" suppressHydrationWarning>
        <head>
          <link
            rel="alternate"
            type="application/rss+xml"
            title="RSS Feed for The Agentic Engineer"
            href="/feed.xml"
          />
          {/* Performance optimization: Establish early connection to CloudFront CDN for placeholder images.
              Reduces FCP/LCP by performing DNS lookup, TCP handshake, and TLS negotiation in parallel
              with HTML parsing, rather than waiting until image tags are discovered. */}
          <link rel="preconnect" href="https://deifkwefumgah.cloudfront.net" />
          <link rel="dns-prefetch" href="https://deifkwefumgah.cloudfront.net" />
        </head>
        <body
          className={`${geistSans.variable} ${geistMono.variable} antialiased flex min-h-screen flex-col`}
        >
          <ThemeProvider
            attribute="class"
            defaultTheme="system"
            enableSystem
            disableTransitionOnChange
          >
            <Navbar8 />
            <main className="flex-1 pt-20">{children}</main>
            <Footer16 />
          </ThemeProvider>
          <Analytics />
          <SpeedInsights />
        </body>
      </html>
    </ClerkProvider>
  );
}
