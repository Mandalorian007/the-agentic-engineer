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

> Currently set to `Matt Fontana` on the live account. Every other surface says
> Matthew. Pick one and make them match.

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
