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

**Live.** Checked September 4, 2026, against the live account and live DNS.

```
email_domain             "mail.agentic-engineer.com"
email_address            "matthew.fontana@mail.agentic-engineer.com"
sending_domain_status    "valid"
reply_to_address         "matthew.fontana@agentic-engineer.com"
```

The status went `awaiting_ssl` to `valid` on its own within a few hours. That
step was Buttondown provisioning a certificate for the link-tracking host, not
anything wrong with the records. `track.mail.agentic-engineer.com` now serves
HTTPS 200, which is the observable proof the certificate landed.

All four records resolve on 1.1.1.1:

```
20260904163845pm._domainkey.mail  TXT    k=rsa; p=MIGfMA0GCSqGSIb3DQEBAQUAA4GNA...
_dmarc.mail                       TXT    v=DMARC1; p=quarantine; rua=...@inbound.postmarkapp.com
pm-bounces.mail                   CNAME  pm.mtasv.net.
track.mail                        CNAME  webhook-consumer.buttondown.email.
```

`dig NS mail.agentic-engineer.com` now returns nothing, so the orphaned
`ns1.onbuttondown.com` zone left over from the torn-down managed setup has
aged out. That zone was what made Buttondown's own checker report
`_dmarc.mail` as invalid earlier in the day, against a record that was correct
the whole time. No action was ever needed on it.

Note the status string. Buttondown reports **`valid`**, not `verified`.
`tools/send_issue.py` originally accepted only `("verified", "active")`, so its
unverified-domain warning would have fired on every send forever against a
domain that was fine. Fixed: see `VERIFIED_DOMAIN_STATUSES`.

Two things about this shape are worth understanding, because they change what
the apex still needs.

**The newsletter sends from a subdomain, and the apex is now Google's alone.**
Buttondown signs and bounces inside `mail.agentic-engineer.com`. Nothing about
the newsletter depends on an apex SPF record, which means the apex record only
has to describe Google Workspace. That was the open question before the
delegation existed, and it is now closed.

**The subdomain publishes its own DMARC, so an apex policy will not reach it.**
A receiver evaluating mail from `mail.agentic-engineer.com` looks for
`_dmarc.mail.agentic-engineer.com` first and stops when it finds one. Buttondown
put one there. So tightening the apex later, even to `p=reject`, cannot
quarantine your own newsletter. The two policies are independent on purpose.

The visible From address now reads `matthew.fontana@mail.agentic-engineer.com`.
That `mail.` prefix is the standard trade for reputation isolation: the
newsletter builds its own sending history without a bad month there touching
whatever Google Workspace sends from the apex. Replies still land in the real
inbox, because `reply_to_address` is the apex address and every client honors
it.

### Remaining

One thing, and it can only be done by sending. Send the first issue to yourself
and read the raw headers. You want `dkim=pass` **and**
`header.d=mail.agentic-engineer.com`. `dkim=pass` alone only proves somebody
signed it; the `d=` is what proves the signature is ours rather than
Buttondown's shared one. This is the same check that confirmed apex DKIM, and
it is the only way to know the delegation works end to end.

## Authenticating the apex

**Done.** Published September 4, 2026. Verified authoritative at Vercel and on
8.8.8.8 and 1.1.1.1, with no literal quote characters stored.

```
agentic-engineer.com.        TXT   "v=spf1 include:_spf.google.com ~all"
_dmarc.agentic-engineer.com. TXT   "v=DMARC1; p=none; rua=mailto:matthew.fontana@agentic-engineer.com"
```

Before this the apex published neither, so anyone could send mail claiming to be
from it and most receivers would take it.

`p=none` requests no action on failure. It is not "reporting mode" as such:
reports come from the `rua` tag, and the two are independent. The record is safe
to publish immediately because nothing enforces on it.

The SPF record is the half that touches delivery. Apex mail moves from an SPF
result of "none" to softfail for any sender outside Google's ranges. Only Google
Workspace sends from the apex today, so nothing changes in practice.

Neither record reaches the newsletter. `mail.agentic-engineer.com` publishes its
own DMARC record, and RFC 7489 discovery stops at the first one it finds rather
than walking up to the apex.

### Before `p` is ever raised

Three things are true today that make enforcement unsafe. None of them matter at
`p=none`. All of them matter the moment it changes.

**1. Google Workspace DKIM: active and verified.** Key published and
authentication started September 4, 2026. Confirmed end to end by sending from
the Workspace account to an outside mailbox and reading the received headers:

```
DKIM-Signature: d=agentic-engineer.com; s=google
Authentication-Results: mx.google.com;
  dkim=pass  header.i=@agentic-engineer.com header.s=google
  spf=pass   smtp.mailfrom=matthew.fontana@agentic-engineer.com
  dmarc=pass (p=NONE sp=NONE dis=NONE) header.from=agentic-engineer.com
```

`d=agentic-engineer.com` is the part that matters. The signature is our domain's
rather than the `*.gappssmtp.com` fallback, so apex mail is now DKIM-aligned and
no longer depends on SPF alone. That is what makes alignment survive forwarding.

The record is 410 characters, over the 255-character cap on a single TXT string,
so Vercel stores it as two. Verified the two reassemble byte-identically to what
the admin console issued.

**2. `sp=` is absent, and defaults to whatever `p` is.** Raising `p` silently
enforces on every subdomain that lacks its own DMARC record, in the same edit.
Set `sp=` explicitly at that point rather than letting it ride.

**3. The newsletter's DMARC record belongs to Buttondown, not to us.** If they
remove `_dmarc.mail.agentic-engineer.com`, apex `sp` starts governing newsletter
mail. Harmless while `p=none`.

### If the newsletter From ever moves to the apex

Do not do this without changing the SPF record first. `include:_spf.google.com`
does not cover Postmark. Moving the From address to `@agentic-engineer.com`
drops the newsletter out from under the `mail.` subdomain's DMARC record, puts it
under the apex record, and softfails apex SPF. Invisible at `p=none` and fatal
under enforcement. The record would need `include:spf.mtasv.net` added.

### Report volume

Apex `rua` collects reports for apex mail only: personal correspondence and
spoofing attempts. The newsletter's reports go to Postmark. Expect roughly 5-20
gzipped XML attachments a day from Google, Microsoft, Yahoo and others, none of
them readable by hand. Currently pointed at the primary inbox so the reports are
guaranteed to arrive. Move `rua` to a dedicated alias or a parser once one
exists.

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
`agentic-engineer.com` and it will validate. Remove them before publishing the
DMARC record above, so the policy is written against the senders that actually
exist.
