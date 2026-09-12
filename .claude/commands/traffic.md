---
description: Pull the human-filtered traffic report (Vercel, Search Console, Buttondown) and reason about it
---

Run the traffic report and interpret it. Do not open the Vercel dashboard; the
dashboard number is mostly crawlers and this report already separates them.

Usage:
- `/traffic` — last 28 days vs the prior 28
- `/traffic --days 90` — longer window
- `/traffic --since 2025-10-13` — since launch

Execute:
```
uv run tools/traffic_report.py [--days N | --since YYYY-MM-DD] [--top N] [--no-gsc]
```

## How to read it

- **Humans** is the number that matters. It counts referred visitors from
  anywhere plus direct visitors from trusted countries (`analytics.trusted_countries`
  in `blog-config.yaml`). **Raw** is what the Vercel dashboard shows.
- Bot fleets can spoof a search referrer and pass the human filter. The tell is
  a one-page burst on ~100% desktop Chrome. The report flags burst days and a
  mobile share under 5%; when it does, treat the window's totals as suspect and
  say so.
- Search Console is the only feed that counts real search clicks and shows
  queries. If it says "Not configured", say that the search numbers are
  missing rather than inferring them from Vercel referrers.
- Newsletter subscribers come from Buttondown.

## What to hand back

Lead with the human daily average and whether it moved. Then the 3-5 things
worth acting on: pages gaining or losing, referrer classes shifting (search,
answer engines, social), any burst that needs discounting, and the search
queries if GSC is wired. Skip the full tables unless asked; the user can run
the tool for those.
