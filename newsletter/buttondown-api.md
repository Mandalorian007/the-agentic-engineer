# What the Buttondown API will and won't let you do

Notes from wiring this account up, all verified against the live API in
September 2026 rather than read off the docs. The docs are accurate about
shapes and silent about permissions, which is where the whole afternoon went.

If you are here because something returned 403, skip to
[Reading a 403](#reading-a-403).

## There are two API keys, and they are not interchangeable

This is the part that costs you an hour if you don't know it.

| Key | Where it comes from | What it can do |
|---|---|---|
| Account key | Buttondown → Settings → API | Subscribers, emails, automations |
| Newsletter key | The `api_key` field in `GET /v1/newsletters` | All of the above, plus newsletter settings |

The account key cannot `PATCH /v1/newsletters/{id}`. Not "cannot change the
paid fields". Cannot change *any* field. Setting `timezone` to the value it
already holds fails:

```
PATCH /v1/newsletters/{id}   {"timezone": "America/New_York"}
Authorization: Token <account key>

403 {"detail": "You do not have permission to access this resource."}
```

The same request with the newsletter key returns 200.

The error text gives you nothing to work with. It is the generic DRF
permission string, identical for a scope problem and a billing problem, and it
carries no `code` or `metadata`. So when a newsletter write 403s, **try the
other key before you conclude anything about your plan.** We nearly bought an
add-on we did not need because the first 403 looked like a paywall.

### Keep them separate on purpose

The website's subscribe route only ever needs to create a subscriber, so it
gets the account key. That is the key sitting in Vercel and GitHub, exposed to
the largest attack surface, and it is structurally incapable of rewriting your
transactional email copy or your reply-to address.

The newsletter key lives in the repo-root `.env.local` only, for
`tools/sync_newsletter_settings.py`. It is deliberately absent from
`website/.env.local`, from Vercel, and from GitHub.

```
.env.local              BUTTONDOWN_API_KEY        (account)
                        BUTTONDOWN_NEWSLETTER_KEY (newsletter, tooling only)
website/.env.local      BUTTONDOWN_API_KEY        (account)
Vercel + GitHub         BUTTONDOWN_API_KEY        (account)
```

## `enabled_features` does not tell you what you can do

`GET /v1/newsletters` returns this on the free plan:

```json
"enabled_features": ["archives", "portal", "api", "automations", "metadata"]
```

`automations` is in that list. Creating an automation returns 201. Activating
it returns 403 with `required_plan: professional`.

So the field describes features that exist for the newsletter, not features
you are entitled to use, and it is worthless as a preflight check. There is no
capability endpoint. The only reliable way to know whether an operation is
permitted is to attempt it and read the error.

That is worth designing around rather than fighting: make the write idempotent
and let it fail loudly, instead of gating it on a capability check that lies.

## Reading a 403

Buttondown returns two structurally different 403s and the difference is the
whole diagnosis.

**Scope problem** — wrong key. Generic, no machine-readable fields:

```json
{"detail": "You do not have permission to access this resource."}
```

**Billing problem** — right key, unpaid feature. Names the feature and the tier:

```json
{
  "code": "forbidden",
  "detail": "Customizing transactional emails requires a Standard plan - please upgrade your account.",
  "metadata": {"feature": "custom_transactional_emails", "required_plan": "standard"}
}
```

If you get the first one, change keys. If you get the second one, get out a
credit card. Branching on the presence of `metadata.required_plan` is stable
enough to build on.

## What is gated, on the free plan

Verified by probe, not inferred.

| Operation | Free? | Gate |
|---|---|---|
| Create subscribers, send emails, read anything | yes | |
| `subscription_redirect_url` | yes | |
| `subscription_confirmation_redirect_url` | yes | |
| `from_name`, `reply_to_address`, `description`, `timezone` | yes | |
| `custom_subscription_confirmed_email_*` (welcome email) | no | Standard |
| `custom_subscription_confirmation_email_*` (confirm email) | no | Standard |
| Activating an automation | no | Professional |

The two redirect fields being free is the useful find. They are how you get
custom welcome content in front of a new subscriber without paying: point
`subscription_confirmation_redirect_url` at a page on your own site and the
confirm click lands there instead of on Buttondown's stock success page. You
control that page completely, and it is a better surface than an email anyway.

Nothing else on the free plan reaches a subscriber in your own words at signup
time except the `description` field, which renders on the hosted subscribe
page. That is why the description copy in
[`buttondown-settings.md`](buttondown-settings.md) is doing more work than it
looks like it is.

## Subscribers created through the API get double opt-in by default

`POST /v1/subscribers` with no `type` creates an `unactivated` subscriber and
sends the confirmation email. You have to pass `"type": "regular"` to skip it.

This is the opposite of what most ESP APIs do, and it is worth stating plainly
because the site's copy depends on it. `app/api/subscribe/route.ts` does not
send `type`, so form signups really do get a confirmation email, and the
success message ("Check your inbox to confirm") is telling the truth. If
anyone ever adds `type: "regular"` to that route to reduce signup friction,
that message becomes a lie and the welcome email stops firing entirely, since
it triggers on confirmation.

Do not confuse this with the collision header. `X-Buttondown-Collision-Behavior: add`
handles a returning or previously-unsubscribed reader; `type` decides whether
a new one has to confirm. They are unrelated.

## Discovering the schema when the docs are thin

Two techniques that beat searching the documentation.

**Send an invalid enum value and read the rejection.** It lists every valid
option:

```bash
curl -sX POST -H "Authorization: Token $KEY" -H "Content-Type: application/json" \
  -d '{"name":"probe","trigger":"__invalid__","actions":[{"type":"__invalid__","metadata":{}}]}' \
  https://api.buttondown.com/v1/automations
```

```
"Input should be 'add_tags', 'remove_tags', 'send_email', 'add_metadata', ... or 'update_email_type'"
```

**Send a valid action with empty metadata.** The error tells you the required
shape, and Buttondown's are unusually good:

```
{"code":"action_invalid",
 "detail":"send_email actions need an email reference inside 'metadata'. Set
           metadata.email_id (to send an existing draft), or metadata.subject + metadata.body."}
```

Both are read-only in practice: the request is rejected at validation, so
nothing is created. They cost one request each and are faster and more current
than the docs.

## Gotchas worth remembering

- `POST /v1/automations` rejects `status` with `422 extra_forbidden`. New
  automations are always created inactive. Create, then `PATCH` the status.
- Automations are the wrong tool for a welcome email here anyway. They need
  Professional; the transactional email field needs Standard, which is
  cheaper. Same outcome, lower tier.
- Setting a redirect URL takes effect immediately. If you point it at a page
  that does not exist yet, confirming subscribers hit a 404 from that second
  onward. Build the page first.
- Buttondown runs a spam firewall on subscriber creation. Roughly ten rapid
  probe requests from one address got that address blocked from resubscribing,
  with an existing subscription left intact and a `subscriber_blocked` code on
  new attempts. Test against throwaway addresses, and space the requests out.

## Where this is implemented

| File | What it does |
|---|---|
| [`tools/sync_newsletter_settings.py`](../tools/sync_newsletter_settings.py) | Pushes `welcome-email.md` to the newsletter. Needs Standard, fails loudly until then. |
| [`tools/send_issue.py`](../tools/send_issue.py) | Composes and sends an issue. Account key. |
| [`website/app/api/subscribe/route.ts`](../website/app/api/subscribe/route.ts) | The signup form's endpoint. Account key. |
| [`welcome-email.md`](welcome-email.md) | Welcome copy. Not live. |
| [`buttondown-settings.md`](buttondown-settings.md) | Everything set by hand in the web UI. |
