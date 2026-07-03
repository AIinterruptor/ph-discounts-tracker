# PH Discounts Tracker — Design Spec

**Date**: 2026-07-03
**Status**: Approved

## Purpose

A GitHub-hosted, fully automated system that scrapes nationwide Philippines
discount/promo pages daily and publishes a free public site listing current
deals, so users can find real savings without manually checking a dozen
retailer/bank/food sites.

## Non-goals (v1)

- No user accounts, personalization, or push notifications.
- No scraping of JS-heavy SPAs (Shopee/Lazada apps) — covered indirectly via
  voucher aggregator sites instead.
- No price tracking / historical charting — just "what's currently on offer."
- No paid infra — everything runs on GitHub's free tier (Actions + Pages).

## Architecture

```
GitHub Actions (daily cron, 06:00 Asia/Manila)
        |
        v
  scrape.py  -- iterates sources.py registry
        |
        v
  data/deals.json  (normalized, deduped, 14-day expiry applied)
  data/last_run_errors.json (per-source failures, for visibility)
        |
        v
  git commit + push (if data changed)
        |
        v
  GitHub Pages (static site reads data/deals.json client-side)
```

No server, no database. The repo itself is the datastore.

## Components

### 1. Source registry (`scraper/sources.py`)

A flat list of source definitions:

```python
SOURCES = [
    {"name": "SM Deals", "url": "https://www.smsupermalls.com/smdeals",
     "category": "retail", "parser": "parse_sm_deals"},
    ...
]
```

Each source maps to a parser function in `scraper/parsers/`. Adding/removing
a source is a registry edit + (if needed) a new small parser function — no
changes to the runner.

**v1 source list (17 sources):**

| Category | Sources |
|---|---|
| Retail/Mall | smsupermalls.com/smdeals, smsupermalls.com/mall-sale-events, smmallsonline.com/promos-2, robinsonsmalls.com/promos-events |
| E-commerce/Vouchers | iprice.ph/coupons, coupons.rappler.com, vouchercodes.ph, rewardpay.com/ph/shopee, picodi.com/ph, coupons.yummy.ph |
| Food | jollibee.com.ph/promos, mcdonalds.com.ph/press-center, coupons.spot.ph, chowking.ph/promos, grab.com/ph/deals |
| Bank | bpi.com.ph promos, rcbccredit.com/promos, eastwestbanker.com/promos, moneymax.ph (Metrobank promos) |
| Aggregator | collectoffers.com/ph |

All requests use a realistic browser `User-Agent` header (research showed
several 403s on bank sites were likely UA-based bot detection, not real
blocks). Sources that still fail consistently degrade gracefully — logged as
errors, simply don't contribute new deals — without breaking the pipeline.

### 2. Parsers (`scraper/parsers/*.py`)

One function per source (or shared function where 2+ sources share the same
HTML structure, e.g. both SM pages). Each parser:

- Takes raw HTML (string)
- Returns a list of normalized dicts:
  ```python
  {"title": str, "description": str, "discount_text": str,
   "url": str, "category": str, "source": str}
  ```
- Raises on unexpected structure (caught by the runner, not swallowed here)
  so failures are visible in `last_run_errors.json` rather than silently
  returning `[]`.

### 3. Runner (`scraper/scrape.py`)

1. Load existing `data/deals.json` (if present).
2. For each source in the registry:
   - Fetch HTML (`requests`, timeout, browser UA header).
   - Parse via the mapped parser function.
   - On any exception: record `{source, error, timestamp}` into an errors
     list; continue to the next source.
3. Merge freshly-scraped deals into the existing set:
   - Dedup key: `(source, title, discount_text)`.
   - New deal → `first_seen = today`, `last_seen = today`.
   - Previously-seen deal found again → update `last_seen = today`.
   - Previously-seen deal NOT found this run → keep as-is (don't touch
     `last_seen`).
4. Drop any deal where `last_seen` is more than 14 days old.
5. Write `data/deals.json` (sorted newest `first_seen` first) and
   `data/last_run_errors.json`.

### 4. GitHub Actions workflow (`.github/workflows/scrape.yml`)

- Trigger: `schedule` (daily, 06:00 Asia/Manila ≈ 22:00 UTC) + `workflow_dispatch`
  for manual runs.
- Steps: checkout → setup Python → install deps → run `scrape.py` → commit
  `data/deals.json` and `data/last_run_errors.json` if changed → push.
- A second job (or the same workflow) triggers/relies on GitHub Pages
  auto-publish from the `main` branch (Pages configured to serve `/docs` or
  a dedicated `site/` folder — see below).

### 5. Static site (`site/index.html`)

- Plain HTML/CSS/vanilla JS, no build step, no framework.
- On load, `fetch('../data/deals.json')`, render a single reverse-chronological
  feed (newest `first_seen` first).
- Category filter chips (Retail / E-commerce / Food / Bank / Aggregator) —
  client-side filter over the already-loaded JSON, no re-fetch.
- Each deal card: title, discount text, short description, source name
  (linked to original URL), "seen X days ago."
- If `last_run_errors.json` is non-empty, a small collapsed "scraper status"
  note at the bottom (transparency, not alarming — most users won't open it).

GitHub Pages serves this from the `main` branch, `/site` (or `/docs`) folder.

## Data flow / normalization details

- All scraped text is stripped of excess whitespace; HTML entities decoded.
- `discount_text` is kept as free text (e.g. "20% off", "Buy 1 Take 1",
  "₱99 combo") rather than trying to force a numeric discount — PH promos are
  too heterogeneous to normalize reliably in v1.
- Dates are ISO 8601 (`YYYY-MM-DD`), always the *scrape* date, not a claimed
  "valid until" date (most source pages don't reliably state expiry).

## Error handling

- Per-source try/except in the runner — one broken parser never blocks the
  other 16 sources.
- Errors written to `data/last_run_errors.json`, visible on-site (see above)
  and inspectable via git history.
- If a source is broken for a long stretch, its deals simply age out via the
  14-day expiry — no manual cleanup needed, though the source should
  eventually be fixed or dropped from the registry.

## Testing

- `tests/fixtures/*.html` — one saved real HTML snapshot per source (captured
  once during development).
- `tests/test_parsers.py` — each parser tested against its fixture, asserting
  it returns ≥1 well-formed deal dict with all required keys populated.
- `tests/test_merge.py` — unit tests for the merge/expiry logic (new deal,
  re-seen deal, expired deal) using synthetic data — no network needed.
- CI runs pytest on every push (separate from the scheduled scrape job).

## Repo layout

```
ph-discounts-tracker/
├── .github/workflows/
│   ├── scrape.yml        # daily cron + manual dispatch
│   └── test.yml          # pytest on push/PR
├── scraper/
│   ├── sources.py
│   ├── scrape.py
│   └── parsers/
│       ├── retail.py
│       ├── ecommerce.py
│       ├── food.py
│       └── bank.py
├── site/
│   └── index.html
├── data/
│   ├── deals.json
│   └── last_run_errors.json
├── tests/
│   ├── fixtures/
│   ├── test_parsers.py
│   └── test_merge.py
├── requirements.txt
└── README.md
```

## Open risks (accepted for v1)

- Source sites may change HTML structure at any time, silently breaking a
  parser until the next manual check-in — mitigated by error visibility, not
  eliminated.
- Some sources (chowking.ph, grab.com/ph/deals) were flagged "risky" in
  research (thin content / possibly stale) — included anyway since they cost
  nothing to try and degrade gracefully if they stop working.
- No legal/ToS review performed on individual source sites' scraping
  policies — this is a personal/hobby project linking back to sources, not
  redistributing full content commercially.
