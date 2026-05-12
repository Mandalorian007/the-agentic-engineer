import type { Metadata } from "next";
import { Open_Sans } from "next/font/google";
import "./globals.css";
import { Navbar8 } from "@/components/navbar8";
import { Footer16 } from "@/components/footer16";
import { ThemeProvider } from "@/components/theme-provider";
import { ClerkProvider } from "@clerk/nextjs";
import { shadcn } from "@clerk/themes";
import { Analytics } from "@vercel/analytics/next";
import { SpeedInsights } from "@vercel/speed-insights/next";

const openSans = Open_Sans({
  variable: "--font-open-sans",
  subsets: ["latin"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "The Agentic Engineer",
  description:
    "I build agentic developer platforms that make engineering teams measurably faster. Vendor-agnostic platform engineering for private industry and federal agencies.",
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
        </head>
        <body
          className={`${openSans.variable} antialiased flex min-h-screen flex-col`}
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
