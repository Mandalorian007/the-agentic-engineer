# Welcome email

Goes out once, after someone clicks the confirm link in the double opt-in email.
Buttondown calls this the "subscription confirmed" transactional email.

**Not live yet.** Customising transactional emails is a paid add-on, and the API
returns `403 custom_transactional_emails, required_plan: standard`. Until that is
bought, confirming subscribers get Buttondown's stock wording, and the newsletter
`description` field is the only place this voice reaches them. Full breakdown of
what is and isn't reachable: [`buttondown-api.md`](buttondown-api.md).

Once it is bought, `uv run tools/sync_newsletter_settings.py` pushes this file.
Nothing else parses it, so edit the copy freely, but keep the `**Subject:**` line
and the `---` rule above the body: the tool keys off both.

Not managed by `tools/send_issue.py`.

---

**Subject:** You're in

---

I'm Matthew Fontana, a staff engineer at Airbnb. Before that Spotify, before that UPS.

That whole time I've been working out how to hand real engineering work to machines without it going badly. I'm not done, and I don't think anyone is. This is the letter I send while I work it out.

Every other Monday you get one email: what I changed in how I work, what broke, and one thing you can paste into your own repo. Real hooks, commands, and config. Not diagrams. If nothing broke, I'll say so rather than invent something.

The first one lands on the next publishing Monday.

Before then, one ask. Hit reply and tell me what you're trying to get an agent to do reliably, and what's stopping it. I read every one. The problems people send me are where a good half of what I write comes from.

Matthew Fontana, Agentic Engineer
Hoboken, NJ
