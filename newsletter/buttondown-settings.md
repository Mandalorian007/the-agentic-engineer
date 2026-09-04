# Buttondown settings

Copy for **Settings → General**. Kept here so it is version-controlled; update
it here and paste it across when it changes.

The description field accepts Markdown and renders on the hosted subscribe page.
On the free plan it is the only place this voice reaches a new subscriber, so it
carries more weight than a description field usually would. See
[`buttondown-api.md`](buttondown-api.md) for what else is and isn't reachable.

---

## Newsletter name

```
Agentic Engineer Journey
```

## Author (the "From" name in the inbox)

```
Matthew Fontana
```

A person's name, not a brand. It is what the recipient sees before they see the
subject line, and a human name meaningfully outperforms a publication name on
both open rate and spam placement for a list this size.

## Reply-to address

```
matthew.fontana@agentic-engineer.com
```

Must be real and monitored. The welcome email asks people to hit reply and tell
you what they are stuck on, which only works if replies land somewhere you read.

---

## Description

```markdown
I'm Matthew Fontana, a staff engineer at Airbnb. Before that Spotify, before that UPS.

That whole time I've been working out how to hand real engineering work to machines without it going badly. I'm not done, and I don't think anyone is. This is the letter I send while I work it out.

Every other Monday you get one email: what I changed in how I work, what broke, and one thing you can paste into your own repo. Real hooks, commands, and config. Not diagrams. If nothing broke, I'll say so rather than invent something.

Every other Monday. Unsubscribe whenever.
```

---

## Shorter variant

For anywhere with a length cap (directory listings, social bios).

```
Working out how to hand real engineering work to machines without it going badly. What I changed, what broke, one thing you can paste. Every other Monday.
```

## Confirmation page

After someone confirms their double opt-in, Buttondown shows a success page.

This page matters more than it looks like it should. No welcome email sends on
the free plan, so this is the last thing a new subscriber sees before two weeks
of silence. Do not promise them an email that isn't coming.

```
You're confirmed. Every other Monday.

Hit reply to any issue and tell me what you're trying to get an agent to do
reliably, and what's stopping it. I read every one.
```

The better version of this is to take it off Buttondown entirely.
`subscription_confirmation_redirect_url` is not plan-gated, so it can point at a
page on this site and the confirm click lands there instead. That page is not
built yet. Build it before setting the field, or confirming subscribers get a
404 the moment you save.

---

## Sending domain

**Not set up.** Checked September 4, 2026, against the live account and live
DNS. This is the one item on this page that affects whether mail arrives at all.

```
sending_domain_status    "none"
email_domain             ""
email_address            "matthew.fontana@agentic-engineer.com"
```

And on the domain itself:

| Record | State |
|---|---|
| MX | `smtp.google.com` (Google Workspace, receiving works) |
| SPF | none |
| DKIM | none at any common selector |
| DMARC | none |

So the From address claims `agentic-engineer.com` while the mail is signed by
Buttondown. Nothing enforces a failure today, because a domain with no DMARC
record publishes no policy to enforce, but the message earns no alignment
credit either. It is the profile of a domain a filter has no reason to trust.

Two separate problems live in that table, and only one of them is about the
newsletter:

1. **Nothing authenticates mail from this domain.** The apex has Google
   Workspace MX and no SPF, which means anyone can send mail claiming to be
   from it and most receivers will take it. That is worth fixing whether or not
   the newsletter ever sends.
2. **The newsletter is not sending from a verified domain.**

### Fixing the second one

Custom sending domains are free on Buttondown; deliverability features are not
paywalled. Their recommended path is the *managed* setup: dedicate a subdomain
to Buttondown and add two `NS` records delegating it, after which they manage
SPF and DKIM inside that subdomain themselves.

Use a subdomain, not the apex. The apex is disqualified from managed setup, and
it already carries Google Workspace MX and the site's Vercel records. A
delegation there is a bad trade for a newsletter.

Suggested: `mail.agentic-engineer.com`. Note the domain currently answers with
a wildcard pointing everything at Vercel; an explicit `NS` delegation for one
label takes precedence over that wildcard, so no other subdomain is affected.

1. Buttondown → Settings → Custom domains → add `mail.agentic-engineer.com` as
   a sending domain.
2. Add the two `NS` records it shows you at the registrar.
3. Wait for `sending_domain_status` to leave `"none"`:
   `GET /v1/newsletters` (see [`buttondown-api.md`](buttondown-api.md)).
4. Send one issue to yourself and read the raw headers. You want
   `dkim=pass` **and** `header.d=` matching the sending domain. `dkim=pass` on
   its own only proves someone signed it.

### Fixing the first one

Independent of Buttondown, and worth doing regardless:

```
agentic-engineer.com.        TXT   "v=spf1 include:_spf.google.com ~all"
_dmarc.agentic-engineer.com. TXT   "v=DMARC1; p=none; rua=mailto:matthew.fontana@agentic-engineer.com"
```

Start DMARC at `p=none`. It changes no delivery and starts the reports flowing,
which is the only honest way to find out what is already sending as this domain
before tightening to `quarantine`.

### Dead Clerk records still authorized on this domain

DNS is hosted at Vercel (`ns1.vercel-dns.com`), so all of this is editable with
`vercel dns` from the repo. Listing it turned up five records left over from
Clerk, which was cut in `688a420`:

```
clk._domainkey    CNAME  dkim1.l402x9fqenpx.clerk.services.
clk2._domainkey   CNAME  dkim2.l402x9fqenpx.clerk.services.
clkmail           CNAME  mail.l402x9fqenpx.clerk.services.
accounts          CNAME  accounts.clerk.services.
clerk             CNAME  frontend-api.clerk.services.
```

The first three matter more than the look of dead config suggests. Two of them
are DKIM selectors, which means this domain currently delegates mail-signing
authority to a tenant on a service the site no longer uses. If that tenant id is
ever released and reclaimed, whoever holds it can sign mail as
`agentic-engineer.com` and it will validate. Remove them before publishing a
DMARC record, so the policy is written against the senders that actually exist.
