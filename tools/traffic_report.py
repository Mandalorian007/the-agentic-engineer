#!/usr/bin/env python3
"""
Traffic report: real readers, not crawlers, in one terminal-readable page.

Pulls three feeds and lays them side by side so the numbers can be reasoned
about without opening a dashboard:

  1. Vercel Web Analytics  (via the `vercel metrics` CLI, already logged in)
  2. Google Search Console (optional; needs a service account, see docs)
  3. Buttondown            (subscriber count, new in window)

The Vercel dashboard counts every visitor, and most of ours are datacenter
crawlers (Singapore/China, no referrer). This report splits "humans" from
"raw" using one heuristic: a visitor is human if they arrived with a referrer
OR came direct from a trusted country. Adjust the country list in
blog-config.yaml under `analytics.trusted_countries`.

Usage:
    uv run tools/traffic_report.py                  # last 28 days vs prior 28
    uv run tools/traffic_report.py --days 90
    uv run tools/traffic_report.py --since 2025-10-13   # since launch
    uv run tools/traffic_report.py --json           # machine-readable
    uv run tools/traffic_report.py --no-gsc         # skip Search Console

Environment (all optional, read from .env.local):
    VERCEL_TOKEN               Only needed outside a logged-in `vercel` CLI (CI)
    GSC_SERVICE_ACCOUNT_JSON   Service-account key, inline (for CI secrets)
    GSC_SERVICE_ACCOUNT_FILE   Same key as a file path
    (neither set)              Application Default Credentials from gcloud; the
                               local path, see docs/traffic-report.md
    BUTTONDOWN_API_KEY         Account key; newsletter section is skipped without it

Exit codes:
    0  report printed
    1  Vercel query failed (the other feeds are best-effort)
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent.parent))
from lib.config import load_config
from lib.frontmatter import parse_frontmatter

project_root = Path(__file__).parent.parent
env_file = project_root / ".env.local"
if env_file.exists():
    load_dotenv(env_file)

METRIC = "vercel.analytics_pageview.count"
VISITORS = "vercel_analytics_pageview_count_unique_visitor_id"

# Direct traffic from these countries is assumed human. Everything else that
# arrives with no referrer is treated as crawler noise. Referred traffic from
# anywhere is always counted as human.
DEFAULT_TRUSTED_COUNTRIES = [
    "US", "CA", "GB", "IE", "DE", "FR", "NL", "BE", "CH", "AT",
    "SE", "NO", "DK", "FI", "ES", "PT", "IT", "PL", "CZ",
    "AU", "NZ", "JP", "KR", "IL", "BR", "MX",
]

SEARCH_ENGINES = {
    "google.com", "bing.com", "duckduckgo.com", "search.brave.com",
    "yahoo.com", "ecosia.org", "yandex.ru", "baidu.com",
}
ANSWER_ENGINES = {
    "chatgpt.com", "perplexity.ai", "claude.ai", "gemini.google.com",
    "copilot.microsoft.com", "notebook.google.com", "you.com",
}


# ---------------------------------------------------------------------------
# Vercel
# ---------------------------------------------------------------------------

class VercelError(Exception):
    pass


class Vercel:
    """Thin wrapper over `vercel metrics ... --format json`.

    Shelling out to the CLI means no token handling locally: it uses whatever
    `vercel login` already established. In CI, set VERCEL_TOKEN and the same
    code path works.
    """

    def __init__(self, project: str, cwd: Path, token: Optional[str] = None):
        self.project = project
        self.cwd = cwd
        self.token = token

    def query(
        self,
        since: date,
        until: date,
        *,
        filter_expr: str,
        group_by: Optional[str] = None,
        granularity: Optional[str] = None,
        limit: int = 25,
    ) -> Dict[str, Any]:
        cmd = [
            "vercel", "metrics", METRIC,
            "-a", "unique/visitor_id",
            "--project", self.project,
            "--since", since.isoformat(),
            # `until` is inclusive of the day, so push to the next midnight.
            "--until", (until + timedelta(days=1)).isoformat(),
            "--filter", filter_expr,
            "--limit", str(limit),
            "--format", "json",
        ]
        if group_by:
            cmd += ["--group-by", group_by]
        if granularity:
            cmd += ["--granularity", granularity]
        if self.token:
            cmd += ["--token", self.token]

        proc = subprocess.run(cmd, cwd=self.cwd, capture_output=True, text=True)
        out = proc.stdout
        # The CLI prints a "Querying metrics..." line before the JSON.
        start = out.find("{")
        if start < 0:
            raise VercelError(
                f"vercel metrics returned no JSON (exit {proc.returncode}):\n"
                f"{proc.stderr.strip() or out.strip()}"
            )
        payload = json.loads(out[start:])
        if "error" in payload:
            raise VercelError(json.dumps(payload["error"]))
        return payload

    def total(self, since: date, until: date, filter_expr: str) -> int:
        payload = self.query(since, until, filter_expr=filter_expr, granularity="1d")
        return sum(row.get(VISITORS, 0) for row in payload.get("data", []))

    def grouped(
        self, since: date, until: date, filter_expr: str, dim: str, limit: int = 25
    ) -> Dict[str, int]:
        payload = self.query(
            since, until, filter_expr=filter_expr, group_by=dim, limit=limit
        )
        return {row.get(dim, ""): row.get(VISITORS, 0) for row in payload.get("summary", [])}

    def daily(self, since: date, until: date, filter_expr: str) -> List[tuple]:
        payload = self.query(since, until, filter_expr=filter_expr, granularity="1d")
        series = []
        for row in payload.get("data", []):
            day = row["timestamp"][:10]
            series.append((day, row.get(VISITORS, 0)))
        return series


def human_filter(trusted: List[str]) -> str:
    countries = ",".join(f"'{c}'" for c in trusted)
    return (
        "environment eq 'production' and "
        f"(referrer_hostname ne '' or country in ({countries}))"
    )


RAW_FILTER = "environment eq 'production'"


# ---------------------------------------------------------------------------
# Google Search Console (optional)
# ---------------------------------------------------------------------------

GSC_SCOPES = ["https://www.googleapis.com/auth/webmasters.readonly"]


def gsc_client():
    """
    Return a Search Console service, or None if not configured.

    Three ways in, checked in order:
      1. GSC_SERVICE_ACCOUNT_JSON  (inline key, for CI)
      2. GSC_SERVICE_ACCOUNT_FILE  (path to a key)
      3. Application Default Credentials from `gcloud auth application-default
         login --scopes=...` (the local path; you are the property owner, so
         no service account and no permission grant are needed)
    """
    try:
        from googleapiclient.discovery import build
    except ImportError:
        print("⚠️  google-api-python-client not installed; run: uv sync", file=sys.stderr)
        return None

    sa_json = os.environ.get("GSC_SERVICE_ACCOUNT_JSON")
    sa_file = os.environ.get("GSC_SERVICE_ACCOUNT_FILE")
    creds = None
    if sa_json or sa_file:
        from google.oauth2 import service_account
        if sa_json:
            creds = service_account.Credentials.from_service_account_info(
                json.loads(sa_json), scopes=GSC_SCOPES)
        else:
            creds = service_account.Credentials.from_service_account_file(
                sa_file, scopes=GSC_SCOPES)
    else:
        try:
            import google.auth
            from google.auth.exceptions import DefaultCredentialsError
            creds, _ = google.auth.default(scopes=GSC_SCOPES)
        except (ImportError, DefaultCredentialsError):
            return None
    return build("searchconsole", "v1", credentials=creds, cache_discovery=False)


def gsc_query(svc, site: str, since: date, until: date,
              dimensions: Optional[List[str]] = None, limit: int = 25) -> List[Dict]:
    body: Dict[str, Any] = {
        "startDate": since.isoformat(),
        "endDate": until.isoformat(),
        "rowLimit": limit,
    }
    if dimensions:
        body["dimensions"] = dimensions
    resp = svc.searchanalytics().query(siteUrl=site, body=body).execute()
    return resp.get("rows", [])


# ---------------------------------------------------------------------------
# Buttondown (optional)
# ---------------------------------------------------------------------------

def buttondown_subscribers(api_key: str, since: date) -> Dict[str, int]:
    """Total regular subscribers and how many were created since `since`."""
    headers = {"Authorization": f"Token {api_key}"}
    base = "https://api.buttondown.com/v1/subscribers"
    total = requests.get(
        base, headers=headers, params={"type": "regular", "page_size": 1}, timeout=15
    ).json().get("count", 0)

    new = 0
    url: Optional[str] = f"{base}?type=regular&ordering=-creation_date&page_size=100"
    cutoff = datetime.combine(since, datetime.min.time(), tzinfo=timezone.utc)
    while url:
        page = requests.get(url, headers=headers, timeout=15).json()
        stop = False
        for sub in page.get("results", []):
            created = datetime.fromisoformat(sub["creation_date"].replace("Z", "+00:00"))
            if created < cutoff:
                stop = True
                break
            new += 1
        url = None if stop else page.get("next")
    return {"total": total, "new": new}


# ---------------------------------------------------------------------------
# Presentation
# ---------------------------------------------------------------------------

def load_titles(config: Dict[str, Any]) -> Dict[str, str]:
    """Map /blog/<slug> -> post title so the page table reads like the blog."""
    titles: Dict[str, str] = {}
    posts_dir = project_root / config["content_dir"]
    for mdx in posts_dir.glob("*.mdx"):
        try:
            fm, _ = parse_frontmatter(mdx.read_text(encoding="utf-8"))
        except Exception:
            continue
        titles[f"/blog/{mdx.stem}"] = fm.get("title", mdx.stem)
    return titles


def pct(cur: int, prev: int) -> str:
    if prev == 0:
        return "new" if cur else "–"
    change = (cur - prev) / prev * 100
    sign = "+" if change >= 0 else ""
    return f"{sign}{change:.0f}%"


def sparkline(values: List[int]) -> str:
    bars = "▁▂▃▄▅▆▇█"
    top = max(values) if values else 0
    if top == 0:
        return bars[0] * len(values)
    return "".join(bars[min(7, int(v / top * 7))] for v in values)


def table(rows: List[List[str]], header: List[str]) -> str:
    widths = [max(len(str(r[i])) for r in [header] + rows) for i in range(len(header))]
    def fmt(r):
        return "| " + " | ".join(str(c).ljust(widths[i]) for i, c in enumerate(r)) + " |"
    sep = "|" + "|".join("-" * (w + 2) for w in widths) + "|"
    return "\n".join([fmt(header), sep] + [fmt(r) for r in rows])


def classify_referrer(host: str) -> str:
    if host == "":
        return "direct"
    if host in SEARCH_ENGINES:
        return "search"
    if host in ANSWER_ENGINES:
        return "answer engine"
    if any(s in host for s in ("linkedin", "twitter", "x.com", "t.co", "bsky",
                               "reddit", "news.ycombinator", "lobste.rs", "facebook")):
        return "social"
    return "other"


def build_report(args: argparse.Namespace) -> Dict[str, Any]:
    config = load_config()
    domain = config["domain"]
    trusted = (config.get("analytics") or {}).get("trusted_countries", DEFAULT_TRUSTED_COUNTRIES)
    titles = load_titles(config)

    # Vercel reports through yesterday; today is partial and GSC lags 2-3 days.
    until = date.today() - timedelta(days=1)
    if args.since:
        since = date.fromisoformat(args.since)
        days = (until - since).days + 1
    else:
        days = args.days
        since = until - timedelta(days=days - 1)
    prev_until = since - timedelta(days=1)
    prev_since = prev_until - timedelta(days=days - 1)

    vercel = Vercel(
        project=(config.get("analytics") or {}).get("vercel_project", "agentic-engineer"),
        cwd=project_root / "website",
        token=os.environ.get("VERCEL_TOKEN"),
    )
    hf = human_filter(trusted)

    report: Dict[str, Any] = {
        "window": {"since": since.isoformat(), "until": until.isoformat(), "days": days,
                   "prev_since": prev_since.isoformat(), "prev_until": prev_until.isoformat()},
        "trusted_countries": trusted,
    }

    # --- Vercel: totals
    humans = vercel.total(since, until, hf)
    humans_prev = vercel.total(prev_since, prev_until, hf)
    raw = vercel.total(since, until, RAW_FILTER)
    raw_prev = vercel.total(prev_since, prev_until, RAW_FILTER)
    report["totals"] = {
        "humans": humans, "humans_prev": humans_prev,
        "raw": raw, "raw_prev": raw_prev,
        "crawler_share": round(1 - humans / raw, 3) if raw else 0,
    }

    # --- Vercel: breakdowns
    report["referrers"] = vercel.grouped(since, until, hf, "referrer_hostname", limit=20)
    report["referrers_prev"] = vercel.grouped(prev_since, prev_until, hf, "referrer_hostname", limit=20)
    report["pages"] = vercel.grouped(since, until, hf, "request_path", limit=args.top)
    report["pages_prev"] = vercel.grouped(prev_since, prev_until, hf, "request_path", limit=200)
    report["countries_raw"] = vercel.grouped(since, until, RAW_FILTER, "country", limit=10)
    report["daily_humans"] = vercel.daily(since, until, hf)
    report["daily_raw"] = vercel.daily(since, until, RAW_FILTER)
    report["devices"] = vercel.grouped(since, until, hf, "device_type", limit=5)

    # Bot fleets slip past the human filter by spoofing a search referrer.
    # They show up as a one-page burst on ~100% desktop Chrome, so flag any
    # day that is far above the window's median and check the device mix.
    values = [v for _, v in report["daily_humans"]]
    ordered = sorted(values)
    median = ordered[len(ordered) // 2] if ordered else 0
    threshold = max(10, median * 5)
    report["bursts"] = [(d, v) for d, v in report["daily_humans"] if v > threshold]
    total_dev = sum(report["devices"].values()) or 1
    report["mobile_share"] = round(report["devices"].get("mobile", 0) / total_dev, 3)

    # --- Search Console
    report["gsc"] = None
    if not args.no_gsc:
        svc = gsc_client()
        if svc:
            site = f"sc-domain:{domain}"
            try:
                tot = gsc_query(svc, site, since, until)
                tot_prev = gsc_query(svc, site, prev_since, prev_until)
                report["gsc"] = {
                    "totals": tot[0] if tot else {},
                    "totals_prev": tot_prev[0] if tot_prev else {},
                    "queries": gsc_query(svc, site, since, until, ["query"], args.top),
                    "pages": gsc_query(svc, site, since, until, ["page"], args.top),
                }
            except Exception as e:  # noqa: BLE001 - best effort feed
                report["gsc_error"] = str(e)

    # --- Buttondown
    report["newsletter"] = None
    api_key = os.environ.get("BUTTONDOWN_API_KEY")
    if api_key:
        try:
            report["newsletter"] = buttondown_subscribers(api_key, since)
        except Exception as e:  # noqa: BLE001
            report["newsletter_error"] = str(e)

    report["titles"] = titles
    return report


def render(r: Dict[str, Any]) -> str:
    w = r["window"]
    t = r["totals"]
    titles = r["titles"]
    out: List[str] = []
    out.append(f"# Traffic report: {w['since']} → {w['until']} ({w['days']}d)")
    out.append(f"Compared to {w['prev_since']} → {w['prev_until']}. "
               f"Humans = referred from anywhere, or direct from a trusted country.")
    out.append("")

    # Totals
    out.append("## Readers")
    out.append(table([
        ["Humans", t["humans"], t["humans_prev"], pct(t["humans"], t["humans_prev"]),
         f"{t['humans'] / w['days']:.1f}/day"],
        ["Raw (dashboard number)", t["raw"], t["raw_prev"], pct(t["raw"], t["raw_prev"]),
         f"{t['crawler_share'] * 100:.0f}% crawler"],
    ], ["Metric", "Now", "Prior", "Δ", "Note"]))
    out.append("")
    days = [d for d, _ in r["daily_humans"]]
    out.append(f"Daily humans: `{sparkline([v for _, v in r['daily_humans']])}` "
               f"({days[0]} → {days[-1]}, peak {max(v for _, v in r['daily_humans'])})")
    dev = ", ".join(f"{k} {v}" for k, v in sorted(r["devices"].items(), key=lambda kv: -kv[1]))
    out.append(f"Device mix (humans): {dev}. Mobile share {r['mobile_share'] * 100:.0f}%.")
    if r["bursts"]:
        burst = ", ".join(f"{d} ({v})" for d, v in r["bursts"])
        out.append(f"⚠️  Burst days: {burst}. Check the page and device mix before trusting "
                   f"the totals: a one-page spike at ~0% mobile is a bot fleet with a spoofed "
                   f"search referrer, not readers.")
    elif r["mobile_share"] < 0.05 and t["humans"] > 50:
        out.append("⚠️  Mobile share under 5% on a meaningful sample. Developer blogs run "
                   "roughly 15-35%; this low usually means bots inside the human count.")
    out.append("")

    # Referrers
    out.append("## Where humans came from")
    by_class: Dict[str, int] = {}
    rows = []
    for host, n in sorted(r["referrers"].items(), key=lambda kv: -kv[1]):
        cls = classify_referrer(host)
        by_class[cls] = by_class.get(cls, 0) + n
        prev = r["referrers_prev"].get(host, 0)
        rows.append([host or "(direct, trusted country)", cls, n, prev, pct(n, prev)])
    out.append(table(rows, ["Referrer", "Class", "Now", "Prior", "Δ"]))
    summary = ", ".join(f"{k} {v}" for k, v in sorted(by_class.items(), key=lambda kv: -kv[1]))
    out.append(f"By class: {summary}")
    out.append("")

    # Pages
    out.append("## Top pages (humans)")
    rows = []
    for path, n in sorted(r["pages"].items(), key=lambda kv: -kv[1]):
        prev = r["pages_prev"].get(path, 0)
        label = titles.get(path)
        shown = f"{path}  ·  {label}" if label else path
        rows.append([shown, n, prev, pct(n, prev)])
    out.append(table(rows, ["Page", "Now", "Prior", "Δ"]))
    out.append("")

    # Countries
    out.append("## Countries (raw, for the crawler picture)")
    total_raw = sum(r["countries_raw"].values()) or 1
    rows = []
    for c, n in sorted(r["countries_raw"].items(), key=lambda kv: -kv[1]):
        flag = "" if c in r["trusted_countries"] else "untrusted direct → crawler"
        rows.append([c, n, f"{n / total_raw * 100:.0f}%", flag])
    out.append(table(rows, ["Country", "Visitors", "Share", "Read"]))
    out.append("")

    # GSC
    out.append("## Google Search Console")
    g = r.get("gsc")
    if g:
        tot, prev = g["totals"], g["totals_prev"]
        out.append(table([
            ["Clicks", tot.get("clicks", 0), prev.get("clicks", 0),
             pct(int(tot.get("clicks", 0)), int(prev.get("clicks", 0)))],
            ["Impressions", tot.get("impressions", 0), prev.get("impressions", 0),
             pct(int(tot.get("impressions", 0)), int(prev.get("impressions", 0)))],
            ["CTR", f"{tot.get('ctr', 0) * 100:.1f}%", f"{prev.get('ctr', 0) * 100:.1f}%", ""],
            ["Avg position", f"{tot.get('position', 0):.1f}", f"{prev.get('position', 0):.1f}", ""],
        ], ["Metric", "Now", "Prior", "Δ"]))
        out.append("")
        out.append("Top queries:")
        out.append(table(
            [[row["keys"][0], row["clicks"], row["impressions"], f"{row['position']:.1f}"]
             for row in g["queries"]],
            ["Query", "Clicks", "Impr", "Pos"]))
        out.append("")
        out.append("Top pages in search:")
        out.append(table(
            [[row["keys"][0].split("//", 1)[-1].split("/", 1)[-1].join(["/", ""]),
              row["clicks"], row["impressions"], f"{row['position']:.1f}"]
             for row in g["pages"]],
            ["Page", "Clicks", "Impr", "Pos"]))
    elif r.get("gsc_error"):
        out.append(f"⚠️  query failed: {r['gsc_error']}")
    else:
        out.append("Not configured. Run `gcloud auth application-default login` with the "
                   "webmasters.readonly scope (see docs/traffic-report.md). This is the only "
                   "feed that counts real search clicks and shows the queries.")
    out.append("")

    # Newsletter
    out.append("## Newsletter")
    n = r.get("newsletter")
    if n:
        plural = "" if n["total"] == 1 else "s"
        out.append(f"{n['total']} subscriber{plural}, {n['new']} new in window.")
    elif r.get("newsletter_error"):
        out.append(f"⚠️  Buttondown query failed: {r['newsletter_error']}")
    else:
        out.append("BUTTONDOWN_API_KEY not set; skipped.")
    out.append("")
    return "\n".join(out)


def main() -> int:
    parser = argparse.ArgumentParser(description="Human-filtered traffic report")
    parser.add_argument("--days", type=int, default=28, help="Window length (default 28)")
    parser.add_argument("--since", help="Window start YYYY-MM-DD (overrides --days)")
    parser.add_argument("--top", type=int, default=20, help="Rows per table (default 20)")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of markdown")
    parser.add_argument("--no-gsc", action="store_true", help="Skip Search Console")
    args = parser.parse_args()

    try:
        report = build_report(args)
    except VercelError as e:
        print(f"❌ Vercel query failed: {e}", file=sys.stderr)
        print("   Run `vercel login` (or set VERCEL_TOKEN) and confirm website/.vercel is linked.",
              file=sys.stderr)
        return 1

    if args.json:
        report.pop("titles", None)
        print(json.dumps(report, indent=2))
    else:
        print(render(report))
    return 0


if __name__ == "__main__":
    sys.exit(main())
