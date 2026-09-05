"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Loader2, Check } from "lucide-react";

type Status = "idle" | "loading" | "success" | "error";

export function NewsletterForm({ source = "home-hero" }: { source?: string }) {
  const [email, setEmail] = useState("");
  const [status, setStatus] = useState<Status>("idle");
  const [message, setMessage] = useState("");

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setStatus("loading");
    setMessage("");

    try {
      const response = await fetch("/api/subscribe", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, source }),
      });

      const data = await response.json();

      if (!response.ok) {
        setStatus("error");
        setMessage(data.message || "Something went wrong. Try again?");
        return;
      }

      setStatus("success");
      setMessage(data.message || "You're in.");
    } catch {
      setStatus("error");
      setMessage("Network error. Try again?");
    }
  }

  // The live region is rendered unconditionally and only its text changes.
  // A region inserted at the same moment as its content is usually missed by
  // screen readers, which is exactly what swapping the form out would do.
  const liveRegion = (
    <span className="sr-only" role="status" aria-live="polite">
      {status === "success" || status === "error" ? message : ""}
    </span>
  );

  if (status === "success") {
    return (
      <div className="flex items-center justify-center gap-2 rounded-md border border-foreground/20 bg-muted/50 px-4 py-3 text-sm">
        {liveRegion}
        <Check className="h-4 w-4 shrink-0" />
        <span>{message}</span>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="w-full">
      {liveRegion}
      <div className="flex flex-col gap-3 sm:flex-row">
        <label htmlFor={`email-${source}`} className="sr-only">
          Email address
        </label>
        <Input
          id={`email-${source}`}
          type="email"
          name="email"
          required
          autoComplete="email"
          placeholder="you@company.com"
          value={email}
          onChange={(event) => setEmail(event.target.value)}
          disabled={status === "loading"}
          className="h-11 flex-1"
        />
        <Button type="submit" size="lg" disabled={status === "loading"}>
          {status === "loading" ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Subscribing
            </>
          ) : (
            "Subscribe"
          )}
        </Button>
      </div>
      <p className="mt-1 min-h-5 text-sm text-destructive">
        {status === "error" ? message : ""}
      </p>
    </form>
  );
}
