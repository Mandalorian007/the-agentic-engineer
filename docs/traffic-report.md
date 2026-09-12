# Traffic report

`uv run tools/traffic_report.py` prints one page of numbers that separate
readers from crawlers. `/traffic` in Claude Code runs it and reasons about the
result. The Vercel dashboard is not the source of truth for this site; most of
what it counts is datacenter traffic from Singapore and China with no referrer.

## Feeds

| Feed | Auth | What it contributes |
|---|---|---|
| Vercel Web Analytics | the logged-in `vercel` CLI (or `VERCEL_TOKEN` in CI) | visitors by day, page, referrer, country, device; the human/raw split |
| Google Search Console | `GSC_SERVICE_ACCOUNT_FILE` or `GSC_SERVICE_ACCOUNT_JSON` | real search clicks, impressions, position, and the queries themselves |
| Buttondown | `BUTTONDOWN_API_KEY` | subscriber count, new in window |

Search Console and Buttondown are optional; the report says so when they are
missing rather than failing.

## The human filter

A visitor is counted as human if they arrived with any referrer, or came
direct from a country in `analytics.trusted_countries` (`blog-config.yaml`).
Everything else with no referrer is crawler noise. On this site that removes
roughly 75% of the dashboard number.

The filter has one known hole: bot fleets that spoof a `google.com` referrer.
July 2026 had one, 582 "visitors" to a single post in one week, 743 desktop
vs 2 mobile, 739 of 745 on Chrome. Real search traffic never looks like that.
The report flags burst days (5x the window's median) and a mobile share under
5% so the pattern is caught, but it cannot remove those rows, so discount the
window by hand when it warns.

## Wiring Search Console

Done on 2026-09-12, and worth recording because it was not the obvious path:

- The Search Console property is `sc-domain:agentic-engineer.com`, owned by
  **mandalorian007@gmail.com**. It was added that day; before then the domain
  was only Workspace-verified and Search Console had never seen it.
- The tool reads it through Application Default Credentials from
  `gcloud auth application-default login` as the gmail account, with the
  `webmasters.readonly` scope. Quota project: `agentic-engineer-blog` (a
  pre-existing project under the gmail account). The Workspace account
  (matthew.fontana@agentic-engineer.com) cannot be used for this: its org
  policy blocks gmail members, and it owns no Search Console properties.
- Verification is a TXT record at the apex on Vercel DNS
  (`google-site-verification=rL7V…`). Do not delete it.

If the credential ever expires, redo the login as the gmail account:

```bash
gcloud auth application-default login \
  --scopes=openid,https://www.googleapis.com/auth/userinfo.email,https://www.googleapis.com/auth/cloud-platform,https://www.googleapis.com/auth/webmasters.readonly
gcloud auth application-default set-quota-project agentic-engineer-blog
```

### CI (later, optional)

For GitHub Actions, create a service account in `agentic-engineer-blog`, add
its email as a user on the Search Console property (Settings → Users and
permissions, Restricted is enough), and put the key JSON in a secret as
`GSC_SERVICE_ACCOUNT_JSON`. `GSC_SERVICE_ACCOUNT_FILE` takes a path instead.
Either one takes precedence over the gcloud login.

## Options

```
--days N            window length, default 28 (compared to the prior N days)
--since YYYY-MM-DD  window start; overrides --days
--top N             rows per table, default 20
--json              machine-readable output, same content
--no-gsc            skip Search Console even if configured
```

## Why the CLI and not the REST API

`vercel metrics` uses the CLI's existing login, so the tool needs no token
locally and the same code path works in CI with `VERCEL_TOKEN`. The metric id
and dimension names differ from the REST docs (`vercel.analytics_pageview.count`,
`unique/visitor_id`, snake_case dimensions); `vercel metrics schema vercel.analytics`
is the source of truth.
