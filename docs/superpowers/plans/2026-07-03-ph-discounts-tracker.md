# PH Discounts Tracker Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a GitHub-hosted system that scrapes 16 curated Philippines discount/promo pages daily via GitHub Actions, stores normalized results in `data/deals.json` with 14-day expiry, and serves them on a static GitHub Pages feed with category filters.

**Architecture:** A Python scraper (`scraper/`) with one parser module per category (retail, ecommerce, food, bank, aggregator), driven by a source registry and a single runner that merges results with expiry logic. A GitHub Actions workflow runs the scraper daily and commits changes; a separate workflow runs tests on push. A dependency-free static HTML/JS page (`site/index.html`) reads the committed JSON directly.

**Tech Stack:** Python 3.11, `requests`, `beautifulsoup4`, `pytest`, GitHub Actions, GitHub Pages, vanilla HTML/CSS/JS (no build step, no framework).

## Global Constraints

- All HTTP requests use a realistic browser `User-Agent` header (spec: several bank-site 403s were likely UA-based bot detection, not real blocks).
- Every source parser is wrapped in try/except at the runner level — one broken parser must never stop the other sources from running.
- Deal dedup key is `(source, title, discount_text)`. A deal not re-found in a run keeps its `last_seen` unchanged; it is dropped once `last_seen` is more than 14 days old.
- Dates are ISO 8601 `YYYY-MM-DD`, always the scrape date (spec: source pages don't reliably state true expiry).
- No headless browser / JS rendering in v1 — sources that require it are excluded (confirmed during research: SM Deals `/smdeals` AJAX-empty page, Shopee/Lazada direct sites).
- No build step for the site — plain HTML/CSS/JS only.

---

## Source List (16 sources, finalized after HTML verification)

Two sources from the original spec were dropped after fetching real HTML:
- `smsupermalls.com/smdeals` — the deal grid is populated by client-side AJAX and ships empty in raw HTML; `mall-sale-events` (kept) covers the same retail category with real server-rendered content.
- `grab.com/ph/deals` — this URL is a single static campaign page, not a repeating deal list; dropped rather than special-cased for one item.
- `mcdonalds.com.ph/press-center` — this is a press-release index, not a discounts page (no discount text anywhere on it); dropped.

`iprice.ph/coupons/` (an A–Z store index, not deals) is replaced with three known high-traffic per-store subpages that do carry real deal cards: `iprice.ph/coupons/lazada/`, `iprice.ph/coupons/shopee/`, `iprice.ph/coupons/zalora/`.

| Category | Source name | URL | Parser module |
|---|---|---|---|
| retail | SM Sale Events | `https://www.smsupermalls.com/mall-sale-events` | `retail.py` |
| retail | SM Malls Online | `https://www.smmallsonline.com/promos-2/` | `retail.py` |
| retail | Robinsons Malls | `https://robinsonsmalls.com/promos-events` | `retail.py` |
| ecommerce | iPrice Lazada | `https://iprice.ph/coupons/lazada/` | `ecommerce.py` |
| ecommerce | iPrice Shopee | `https://iprice.ph/coupons/shopee/` | `ecommerce.py` |
| ecommerce | iPrice Zalora | `https://iprice.ph/coupons/zalora/` | `ecommerce.py` |
| ecommerce | Rappler Coupons | `https://coupons.rappler.com` | `ecommerce.py` |
| ecommerce | VoucherCodes.ph | `https://vouchercodes.ph` | `ecommerce.py` |
| ecommerce | RewardPay Shopee | `https://rewardpay.com/ph/shopee` | `ecommerce.py` |
| ecommerce | Picodi PH | `https://picodi.com/ph` | `ecommerce.py` |
| ecommerce | Yummy.ph Coupons | `https://coupons.yummy.ph` | `ecommerce.py` |
| food | Jollibee Promos | `https://www.jollibee.com.ph/promos` | `food.py` |
| food | Chowking Promos | `https://chowking.ph/promos` | `food.py` |
| food | Spot.ph Coupons | `https://coupons.spot.ph` | `food.py` |
| bank | BPI Promos | `https://www.bpi.com.ph/personal/rewards-and-promotions/promos` | `bank.py` |
| bank | RCBC Credit Promos | `https://www.rcbccredit.com/promos` | `bank.py` |
| bank | EastWest Promos | `https://www.eastwestbanker.com/promos` | `bank.py` |
| bank | Moneymax Metrobank | `https://www.moneymax.ph/credit-card/partners/metrobank` | `bank.py` |
| aggregator | CollectOffers PH | `https://collectoffers.com/ph` | `aggregator.py` |

That's 18 rows — 16 unique domains/parsers worth noting: VoucherCodes.ph, RewardPay, Yummy.ph, Spot.ph, and CollectOffers all share the same underlying "hashed class" platform but with different template variants (`_1ve99md*` vs `xffhp*`), so each still needs its own selector constant even though the parsing logic is shared via a common helper function.

---

## File Structure

```
ph-discounts-tracker/
├── .github/workflows/
│   ├── scrape.yml
│   └── test.yml
├── scraper/
│   ├── __init__.py
│   ├── http.py              # shared fetch-with-UA helper
│   ├── models.py             # Deal dataclass, normalization helper
│   ├── sources.py            # registry: list of Source entries
│   ├── scrape.py              # runner: fetch -> parse -> merge -> write
│   └── parsers/
│       ├── __init__.py
│       ├── retail.py
│       ├── ecommerce.py
│       ├── food.py
│       ├── bank.py
│       └── aggregator.py
├── site/
│   └── index.html
├── data/
│   ├── deals.json
│   └── last_run_errors.json
├── tests/
│   ├── fixtures/
│   │   ├── sm_saleevents.html
│   │   ├── smmallsonline.html
│   │   ├── robinsons.html
│   │   ├── iprice_lazada.html
│   │   ├── rappler.html
│   │   ├── vouchercodes.html
│   │   ├── rewardpay.html
│   │   ├── picodi.html
│   │   ├── yummy.html
│   │   ├── jollibee.html
│   │   ├── chowking.html
│   │   ├── spot.html
│   │   ├── bpi.html
│   │   ├── rcbc.html
│   │   ├── eastwest.html
│   │   ├── moneymax_metrobank.html
│   │   └── collectoffers.html
│   ├── test_parsers.py
│   └── test_merge.py
├── requirements.txt
├── .gitignore
└── README.md
```

**Responsibility split:**
- `scraper/http.py` — one function, `fetch(url) -> str`, owns the UA header and timeout. Nothing else touches `requests` directly.
- `scraper/models.py` — the `Deal` shape and a `make_deal(...)` normalization helper (whitespace stripping) shared by every parser, so all 16 parsers produce identically-shaped dicts.
- `scraper/parsers/*.py` — pure functions `parse(html: str) -> list[dict]`, one per category file, no I/O.
- `scraper/sources.py` — the registry mapping URL → category → parser function reference. This is the only file touched when adding/removing a source with an already-shared parser shape.
- `scraper/scrape.py` — orchestration only: loop the registry, call `http.fetch`, call the parser, catch exceptions, merge into existing `data/deals.json` with expiry, write output. No parsing logic lives here.

---

## Task 1: Project scaffold, Deal model, and HTTP helper

**Files:**
- Create: `requirements.txt`
- Create: `.gitignore`
- Create: `scraper/__init__.py`
- Create: `scraper/models.py`
- Create: `scraper/http.py`
- Create: `tests/__init__.py`
- Test: `tests/test_models.py`

**Interfaces:**
- Produces: `scraper.models.make_deal(title: str, description: str, discount_text: str, url: str, category: str, source: str, scrape_date: str) -> dict` returning `{"title", "description", "discount_text", "url", "category", "source", "first_seen", "last_seen"}` (both seen dates set to `scrape_date`).
- Produces: `scraper.http.fetch(url: str, timeout: int = 15) -> str` returning response text, raising `requests.HTTPError` on non-2xx and `requests.RequestException` on network failure. Sends header `{"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"}`.

- [ ] **Step 1: Create the project scaffold files**

Create `requirements.txt`:
```
requests==2.32.3
beautifulsoup4==4.12.3
pytest==8.3.3
```

Create `.gitignore`:
```
__pycache__/
*.pyc
.pytest_cache/
venv/
.venv/
```

Create empty `scraper/__init__.py` and `tests/__init__.py` (both zero-byte files, just to make the directories importable packages).

- [ ] **Step 2: Write the failing test for `make_deal`**

Create `tests/test_models.py`:
```python
from scraper.models import make_deal


def test_make_deal_normalizes_whitespace_and_sets_dates():
    deal = make_deal(
        title="  Big   Sale  \n",
        description="Save on stuff.\n\n  ",
        discount_text=" 20% OFF ",
        url="https://example.com/deal",
        category="retail",
        source="Example Source",
        scrape_date="2026-07-03",
    )
    assert deal == {
        "title": "Big Sale",
        "description": "Save on stuff.",
        "discount_text": "20% OFF",
        "url": "https://example.com/deal",
        "category": "retail",
        "source": "Example Source",
        "first_seen": "2026-07-03",
        "last_seen": "2026-07-03",
    }
```

- [ ] **Step 3: Run test to verify it fails**

Run: `python -m pytest tests/test_models.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'scraper.models'`

- [ ] **Step 4: Implement `scraper/models.py`**

```python
import re


def _clean(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def make_deal(title, description, discount_text, url, category, source, scrape_date):
    return {
        "title": _clean(title),
        "description": _clean(description),
        "discount_text": _clean(discount_text),
        "url": url,
        "category": category,
        "source": source,
        "first_seen": scrape_date,
        "last_seen": scrape_date,
    }
```

- [ ] **Step 5: Run test to verify it passes**

Run: `python -m pytest tests/test_models.py -v`
Expected: PASS

- [ ] **Step 6: Implement `scraper/http.py`**

```python
import requests

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)


def fetch(url: str, timeout: int = 15) -> str:
    response = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=timeout)
    response.raise_for_status()
    return response.text
```

No test for this file directly — it's a thin wrapper over `requests` exercised indirectly by the runner tests in Task 7. Manual verification happens in Task 8 (end-to-end run).

- [ ] **Step 7: Commit**

```bash
git add requirements.txt .gitignore scraper/__init__.py scraper/models.py scraper/http.py tests/__init__.py tests/test_models.py
git commit -m "Add project scaffold, Deal model, and HTTP fetch helper"
```

---

## Task 2: Retail parsers (SM Sale Events, SM Malls Online, Robinsons)

**Files:**
- Create: `scraper/parsers/__init__.py`
- Create: `scraper/parsers/retail.py`
- Create: `tests/fixtures/sm_saleevents.html`
- Create: `tests/fixtures/smmallsonline.html`
- Create: `tests/fixtures/robinsons.html`
- Test: `tests/test_parsers.py` (retail section)

**Interfaces:**
- Consumes: `scraper.models.make_deal(...)` from Task 1.
- Produces: `scraper.parsers.retail.parse_sm_sale_events(html: str, scrape_date: str) -> list[dict]`, `scraper.parsers.retail.parse_sm_malls_online(html: str, scrape_date: str) -> list[dict]`, `scraper.parsers.retail.parse_robinsons(html: str, scrape_date: str) -> list[dict]`. All three return lists of dicts shaped like `make_deal`'s output. Each parser function signature `(html: str, scrape_date: str) -> list[dict]` is the shape every parser function in every category module follows for the rest of this plan.

- [ ] **Step 1: Copy the saved fixture HTML into the repo**

Copy the three files from the research scratchpad into `tests/fixtures/`:

```bash
cp "C:/Users/josed/AppData/Local/Temp/claude/C--Users-josed/35bc89e9-4a6d-41f2-9021-15dd9d628e5d/scratchpad/html/sm_saleevents.html" tests/fixtures/sm_saleevents.html
cp "C:/Users/josed/AppData/Local/Temp/claude/C--Users-josed/35bc89e9-4a6d-41f2-9021-15dd9d628e5d/scratchpad/html/smmallsonline.html" tests/fixtures/smmallsonline.html
cp "C:/Users/josed/AppData/Local/Temp/claude/C--Users-josed/35bc89e9-4a6d-41f2-9021-15dd9d628e5d/scratchpad/html/robinsons.html" tests/fixtures/robinsons.html
```

If any file is missing (scratchpad cleaned up), re-fetch the source URL with a browser UA and save the raw HTML to that path before continuing — the parser tests depend on real fixture content, not synthetic HTML, since real pages have quirks (e.g. the genuine `<hh4>` typo tag on SM Sale Events) that synthetic HTML would miss.

- [ ] **Step 2: Write the failing tests**

Create `tests/test_parsers.py` (this file grows across Tasks 2-6, retail section first):
```python
from pathlib import Path

from scraper.parsers import retail

FIXTURES = Path(__file__).parent / "fixtures"


def _read_fixture(name):
    return (FIXTURES / name).read_text(encoding="utf-8")


def test_parse_sm_sale_events_returns_deals():
    html = _read_fixture("sm_saleevents.html")
    deals = retail.parse_sm_sale_events(html, "2026-07-03")
    assert len(deals) >= 1
    deal = deals[0]
    assert deal["category"] == "retail"
    assert deal["source"] == "SM Sale Events"
    assert deal["title"] != ""
    assert deal["url"].startswith("http")


def test_parse_sm_malls_online_returns_deals():
    html = _read_fixture("smmallsonline.html")
    deals = retail.parse_sm_malls_online(html, "2026-07-03")
    assert len(deals) >= 1
    deal = deals[0]
    assert deal["category"] == "retail"
    assert deal["source"] == "SM Malls Online"
    assert deal["title"] != ""
    assert deal["url"].startswith("http")


def test_parse_robinsons_returns_deals():
    html = _read_fixture("robinsons.html")
    deals = retail.parse_robinsons(html, "2026-07-03")
    assert len(deals) >= 1
    deal = deals[0]
    assert deal["category"] == "retail"
    assert deal["source"] == "Robinsons Malls"
    assert deal["url"].startswith("http")
```

- [ ] **Step 3: Run tests to verify they fail**

Run: `python -m pytest tests/test_parsers.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'scraper.parsers'`

- [ ] **Step 4: Implement `scraper/parsers/__init__.py` (empty) and `scraper/parsers/retail.py`**

Create empty `scraper/parsers/__init__.py`.

Create `scraper/parsers/retail.py`:
```python
from bs4 import BeautifulSoup

from scraper.models import make_deal


def parse_sm_sale_events(html: str, scrape_date: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    deals = []
    for anchor in soup.select("a.card-text"):
        card = anchor.select_one("div.card.big-card")
        if card is None:
            continue
        title_tag = card.select_one(".truncate-deals") or card.select_one("h4")
        title = title_tag.get_text(" ", strip=True) if title_tag else ""
        desc_tag = card.select_one("p.card-text")
        description = desc_tag.get_text(" ", strip=True) if desc_tag else ""
        url = anchor.get("href", "")
        if not title or not url:
            continue
        deals.append(
            make_deal(
                title=title,
                description=description,
                discount_text=description,
                url=url,
                category="retail",
                source="SM Sale Events",
                scrape_date=scrape_date,
            )
        )
    return deals


def parse_sm_malls_online(html: str, scrape_date: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    deals = []
    for article in soup.select("article"):
        title_link = article.select_one("h2.blog-entry-title a, h2.entry-title a")
        if title_link is None:
            continue
        excerpt = article.select_one(".excerpt-wrap.entry-summary p, .entry-summary p")
        description = excerpt.get_text(" ", strip=True) if excerpt else ""
        title = title_link.get_text(" ", strip=True)
        url = title_link.get("href", "")
        if not title or not url:
            continue
        deals.append(
            make_deal(
                title=title,
                description=description,
                discount_text="",
                url=url,
                category="retail",
                source="SM Malls Online",
                scrape_date=scrape_date,
            )
        )
    return deals


def parse_robinsons(html: str, scrape_date: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    deals = []
    for link in soup.select("a.event_link"):
        url = link.get("href", "")
        if not url:
            continue
        if url.startswith("/"):
            url = f"https://robinsonsmalls.com{url}"
        img = link.select_one("img")
        title = img.get("alt", "").strip() if img else ""
        if not title:
            title = url.rstrip("/").rsplit("/", 1)[-1].replace("-", " ").title()
        body_container = link.find_parent("div", class_="views-field")
        description = ""
        if body_container is not None:
            sibling = body_container.find_next_sibling(
                "div", class_="views-field-body"
            )
            if sibling is not None:
                description = sibling.get_text(" ", strip=True)
        deals.append(
            make_deal(
                title=title,
                description=description,
                discount_text="",
                url=url,
                category="retail",
                source="Robinsons Malls",
                scrape_date=scrape_date,
            )
        )
    return deals
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `python -m pytest tests/test_parsers.py -v`
Expected: PASS for all three retail tests. If `parse_robinsons` yields 0 deals because the fixture's markup nests differently than expected, inspect `tests/fixtures/robinsons.html` directly (`grep -o 'event_link' tests/fixtures/robinsons.html` to count occurrences) and adjust the selector — the fixture is ground truth, not the snippet in this plan.

- [ ] **Step 6: Commit**

```bash
git add scraper/parsers/__init__.py scraper/parsers/retail.py tests/fixtures/sm_saleevents.html tests/fixtures/smmallsonline.html tests/fixtures/robinsons.html tests/test_parsers.py
git commit -m "Add retail parsers for SM Sale Events, SM Malls Online, Robinsons"
```

---

## Task 3: E-commerce parsers (iPrice x3, Rappler, VoucherCodes, RewardPay, Picodi, Yummy)

**Files:**
- Create: `scraper/parsers/ecommerce.py`
- Create: `tests/fixtures/iprice_lazada.html`
- Create: `tests/fixtures/rappler.html`
- Create: `tests/fixtures/vouchercodes.html`
- Create: `tests/fixtures/rewardpay.html`
- Create: `tests/fixtures/picodi.html`
- Create: `tests/fixtures/yummy.html`
- Modify: `tests/test_parsers.py` (add ecommerce section)

**Interfaces:**
- Consumes: `scraper.models.make_deal(...)`.
- Produces: `scraper.parsers.ecommerce.parse_iprice(html: str, scrape_date: str, store_name: str) -> list[dict]` (shared by all 3 iPrice subpages, `store_name` passed by the caller/registry), `parse_rappler(html, scrape_date)`, `parse_hashed_card_platform(html: str, scrape_date: str, source_name: str) -> list[dict]` (shared by VoucherCodes/RewardPay/Yummy — see Task 6 note on CollectOffers reusing this same function), `parse_picodi(html, scrape_date)`.

Note on the shared hashed-platform parser: research found VoucherCodes.ph, Yummy.ph, and CollectOffers.ph share the `_1ve99md1` template family exactly, while RewardPay uses a different hash prefix (`xffhp0`) for the same positional layout. `parse_hashed_card_platform` takes an explicit `container_selector` parameter so both variants can reuse one function body.

- [ ] **Step 1: Copy fixture HTML**

```bash
cp "C:/Users/josed/AppData/Local/Temp/claude/C--Users-josed/35bc89e9-4a6d-41f2-9021-15dd9d628e5d/scratchpad/html/iprice_lazada.html" tests/fixtures/iprice_lazada.html
cp "C:/Users/josed/AppData/Local/Temp/claude/C--Users-josed/35bc89e9-4a6d-41f2-9021-15dd9d628e5d/scratchpad/html/rappler.html" tests/fixtures/rappler.html
cp "C:/Users/josed/AppData/Local/Temp/claude/C--Users-josed/35bc89e9-4a6d-41f2-9021-15dd9d628e5d/scratchpad/html/vouchercodes.html" tests/fixtures/vouchercodes.html
cp "C:/Users/josed/AppData/Local/Temp/claude/C--Users-josed/35bc89e9-4a6d-41f2-9021-15dd9d628e5d/scratchpad/html/rewardpay.html" tests/fixtures/rewardpay.html
cp "C:/Users/josed/AppData/Local/Temp/claude/C--Users-josed/35bc89e9-4a6d-41f2-9021-15dd9d628e5d/scratchpad/html/picodi.html" tests/fixtures/picodi.html
cp "C:/Users/josed/AppData/Local/Temp/claude/C--Users-josed/35bc89e9-4a6d-41f2-9021-15dd9d628e5d/scratchpad/html/yummy.html" tests/fixtures/yummy.html
```

- [ ] **Step 2: Write the failing tests**

Append to `tests/test_parsers.py`:
```python
from scraper.parsers import ecommerce


def test_parse_iprice_returns_deals():
    html = _read_fixture("iprice_lazada.html")
    deals = ecommerce.parse_iprice(html, "2026-07-03", "iPrice Lazada")
    assert len(deals) >= 1
    deal = deals[0]
    assert deal["category"] == "ecommerce"
    assert deal["source"] == "iPrice Lazada"
    assert deal["discount_text"] != ""
    assert deal["url"].startswith("http")


def test_parse_rappler_returns_deals():
    html = _read_fixture("rappler.html")
    deals = ecommerce.parse_rappler(html, "2026-07-03")
    assert len(deals) >= 1
    deal = deals[0]
    assert deal["category"] == "ecommerce"
    assert deal["source"] == "Rappler Coupons"
    assert deal["title"] != ""


def test_parse_hashed_card_platform_vouchercodes():
    html = _read_fixture("vouchercodes.html")
    deals = ecommerce.parse_hashed_card_platform(
        html, "2026-07-03", "VoucherCodes.ph", container_selector="article._1ve99md1"
    )
    assert len(deals) >= 1
    deal = deals[0]
    assert deal["source"] == "VoucherCodes.ph"
    assert deal["discount_text"] != ""
    assert deal["title"] != ""


def test_parse_hashed_card_platform_rewardpay():
    html = _read_fixture("rewardpay.html")
    deals = ecommerce.parse_hashed_card_platform(
        html, "2026-07-03", "RewardPay Shopee", container_selector="article.xffhp0"
    )
    assert len(deals) >= 1
    assert deals[0]["source"] == "RewardPay Shopee"


def test_parse_hashed_card_platform_yummy():
    html = _read_fixture("yummy.html")
    deals = ecommerce.parse_hashed_card_platform(
        html, "2026-07-03", "Yummy.ph Coupons", container_selector="article._1ve99md1"
    )
    assert len(deals) >= 1
    assert deals[0]["source"] == "Yummy.ph Coupons"


def test_parse_picodi_returns_deals():
    html = _read_fixture("picodi.html")
    deals = ecommerce.parse_picodi(html, "2026-07-03")
    assert len(deals) >= 1
    deal = deals[0]
    assert deal["category"] == "ecommerce"
    assert deal["source"] == "Picodi PH"
    assert deal["title"] != ""
```

- [ ] **Step 3: Run tests to verify they fail**

Run: `python -m pytest tests/test_parsers.py -v -k ecommerce or iprice or rappler or hashed or picodi`
Expected: FAIL with `ModuleNotFoundError: No module named 'scraper.parsers.ecommerce'`

- [ ] **Step 4: Implement `scraper/parsers/ecommerce.py`**

```python
from bs4 import BeautifulSoup

from scraper.models import make_deal


def parse_iprice(html: str, scrape_date: str, store_name: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    deals = []
    for card in soup.select("div.rh_offer_list"):
        title_tag = card.select_one("h2 a")
        if title_tag is None:
            continue
        title = title_tag.get_text(" ", strip=True)
        url = title_tag.get("href", "")
        discount_tag = card.select_one(".sale_letter, .rh_custom_notice")
        discount_text = discount_tag.get_text(" ", strip=True) if discount_tag else ""
        desc_tag = card.select_one(".rh_gr_middle_desc")
        description = desc_tag.get_text(" ", strip=True) if desc_tag else ""
        if not title or not url:
            continue
        deals.append(
            make_deal(
                title=title,
                description=description,
                discount_text=discount_text,
                url=url,
                category="ecommerce",
                source=store_name,
                scrape_date=scrape_date,
            )
        )
    return deals


def parse_rappler(html: str, scrape_date: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    deals = []
    for item in soup.select("li.rappler-table"):
        title_tag = item.select_one(".description h3")
        store_link = item.select_one(".store a")
        if title_tag is None or store_link is None:
            continue
        title = title_tag.get_text(" ", strip=True)
        url = store_link.get("href", "")
        if not title or not url:
            continue
        deals.append(
            make_deal(
                title=title,
                description="",
                discount_text="",
                url=url,
                category="ecommerce",
                source="Rappler Coupons",
                scrape_date=scrape_date,
            )
        )
    return deals


def parse_hashed_card_platform(
    html: str, scrape_date: str, source_name: str, container_selector: str
) -> list[dict]:
    """Shared parser for the coupon-site platform used by VoucherCodes.ph,
    RewardPay, Yummy.ph, and CollectOffers. Build-hashed classes regenerate
    on redeploy, so fields are located by child position within each
    container, not by class name."""
    soup = BeautifulSoup(html, "html.parser")
    deals = []
    for article in soup.select(container_selector):
        text_wrapper = article.find_all("div", recursive=True)
        texts = [
            d.get_text(" ", strip=True)
            for d in text_wrapper
            if d.get_text(strip=True) and not d.find("div")
        ]
        if len(texts) < 4:
            continue
        discount_text, _type_label, _brand, title = texts[0], texts[1], texts[2], texts[3]
        description = texts[4] if len(texts) > 4 else ""
        link_tag = article.select_one("a[href]")
        url = link_tag.get("href", "") if link_tag else ""
        if url.startswith("/"):
            url = f"https://{source_name.lower().replace(' ', '')}.example{url}"
        if not title:
            continue
        deals.append(
            make_deal(
                title=title,
                description=description,
                discount_text=discount_text,
                url=url,
                category="ecommerce",
                source=source_name,
                scrape_date=scrape_date,
            )
        )
    return deals


def parse_picodi(html: str, scrape_date: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    deals = []
    for slide in soup.select("li.brandbar__slide"):
        link = slide.select_one("a.brandbar__link")
        if link is None:
            continue
        url = link.get("href", "")
        if url.startswith("/"):
            url = f"https://picodi.com{url}"
        img = slide.select_one("img")
        title = img.get("alt", "").strip() if img else ""
        cashback = slide.select_one(".brandbar__cashback-label")
        discount_text = cashback.get_text(" ", strip=True) if cashback else ""
        if not title or not url:
            continue
        deals.append(
            make_deal(
                title=title,
                description="",
                discount_text=discount_text,
                url=url,
                category="ecommerce",
                source="Picodi PH",
                scrape_date=scrape_date,
            )
        )
    return deals
```

- [ ] **Step 5: Run tests, fix selectors against real fixtures if they fail**

Run: `python -m pytest tests/test_parsers.py -v`

The `parse_hashed_card_platform` function is the riskiest one in this task — it locates fields by counting non-nested `div` children by text content, which is fragile to exact DOM nesting. If the test fails because `texts` doesn't line up as expected, open the fixture file and count the actual div nesting depth by hand (`grep -c 'class="_1ve99md' tests/fixtures/vouchercodes.html`), then adjust the `text_wrapper` filter (e.g. restrict to `article.select_one("div.{inner_container_class}").find_all("div", recursive=False)` for direct children only, if the fixture's real structure has a single wrapping div with the five fields as direct children — re-check against the actual saved HTML rather than the plan's snippet, since real site markup is ground truth).

Expected: PASS for all ecommerce tests once selectors are confirmed against real fixture content.

- [ ] **Step 6: Commit**

```bash
git add scraper/parsers/ecommerce.py tests/fixtures/iprice_lazada.html tests/fixtures/rappler.html tests/fixtures/vouchercodes.html tests/fixtures/rewardpay.html tests/fixtures/picodi.html tests/fixtures/yummy.html tests/test_parsers.py
git commit -m "Add ecommerce parsers for iPrice, Rappler, VoucherCodes, RewardPay, Picodi, Yummy"
```

---

## Task 4: Food parsers (Jollibee, Chowking, Spot.ph)

**Files:**
- Create: `scraper/parsers/food.py`
- Create: `tests/fixtures/jollibee.html`
- Create: `tests/fixtures/chowking.html`
- Create: `tests/fixtures/spot.html`
- Modify: `tests/test_parsers.py` (add food section)

**Interfaces:**
- Consumes: `scraper.models.make_deal(...)`, `scraper.parsers.ecommerce.parse_hashed_card_platform(...)` (reused for Spot.ph, which shares the same platform).
- Produces: `scraper.parsers.food.parse_jollibee(html: str, scrape_date: str) -> list[dict]`, `scraper.parsers.food.parse_chowking(html: str, scrape_date: str) -> list[dict]`.

- [ ] **Step 1: Copy fixture HTML**

```bash
cp "C:/Users/josed/AppData/Local/Temp/claude/C--Users-josed/35bc89e9-4a6d-41f2-9021-15dd9d628e5d/scratchpad/html/jollibee.html" tests/fixtures/jollibee.html
cp "C:/Users/josed/AppData/Local/Temp/claude/C--Users-josed/35bc89e9-4a6d-41f2-9021-15dd9d628e5d/scratchpad/html/chowking.html" tests/fixtures/chowking.html
cp "C:/Users/josed/AppData/Local/Temp/claude/C--Users-josed/35bc89e9-4a6d-41f2-9021-15dd9d628e5d/scratchpad/html/spot.html" tests/fixtures/spot.html
```

- [ ] **Step 2: Write the failing tests**

Append to `tests/test_parsers.py`:
```python
from scraper.parsers import food


def test_parse_jollibee_returns_deals():
    html = _read_fixture("jollibee.html")
    deals = food.parse_jollibee(html, "2026-07-03")
    assert len(deals) >= 1
    deal = deals[0]
    assert deal["category"] == "food"
    assert deal["source"] == "Jollibee Promos"
    assert deal["title"] != ""
    assert deal["url"].startswith("http")


def test_parse_chowking_returns_deals():
    html = _read_fixture("chowking.html")
    deals = food.parse_chowking(html, "2026-07-03")
    assert len(deals) >= 1
    deal = deals[0]
    assert deal["category"] == "food"
    assert deal["source"] == "Chowking Promos"
    assert deal["title"] != ""
    assert deal["url"].startswith("http")


def test_parse_spot_via_hashed_platform():
    html = _read_fixture("spot.html")
    deals = ecommerce.parse_hashed_card_platform(
        html, "2026-07-03", "Spot.ph Coupons", container_selector="article._1ve99md1"
    )
    assert len(deals) >= 1
    assert deals[0]["source"] == "Spot.ph Coupons"
```

- [ ] **Step 3: Run tests to verify they fail**

Run: `python -m pytest tests/test_parsers.py -v -k food or chowking or jollibee or spot`
Expected: FAIL with `ModuleNotFoundError: No module named 'scraper.parsers.food'`

- [ ] **Step 4: Implement `scraper/parsers/food.py`**

Jollibee cards carry no discount/description text (confirmed from research — only title + "Learn more"), so `discount_text` and `description` are empty strings for this source; the site still has value as a "new promo announced" feed. Chowking cards carry the title only in the anchor's `title` attribute (no visible text), confirmed from research.

```python
from bs4 import BeautifulSoup

from scraper.models import make_deal


def parse_jollibee(html: str, scrape_date: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    deals = []
    for card in soup.select("div.card"):
        title_link = card.select_one(".title-wrapper a")
        if title_link is None:
            continue
        title = title_link.get_text(" ", strip=True)
        url = title_link.get("href", "")
        if url.startswith("/"):
            url = f"https://www.jollibee.com.ph{url}"
        if not title or not url:
            continue
        deals.append(
            make_deal(
                title=title,
                description="",
                discount_text="",
                url=url,
                category="food",
                source="Jollibee Promos",
                scrape_date=scrape_date,
            )
        )
    return deals


def parse_chowking(html: str, scrape_date: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    deals = []
    for item in soup.select("div.ck_basic_elem_grid-item"):
        link = item.select_one("a[title]")
        if link is None:
            continue
        title = link.get("title", "").strip()
        url = link.get("href", "")
        if not title or not url:
            continue
        deals.append(
            make_deal(
                title=title,
                description="",
                discount_text="",
                url=url,
                category="food",
                source="Chowking Promos",
                scrape_date=scrape_date,
            )
        )
    return deals
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `python -m pytest tests/test_parsers.py -v`
Expected: PASS for all food tests.

- [ ] **Step 6: Commit**

```bash
git add scraper/parsers/food.py tests/fixtures/jollibee.html tests/fixtures/chowking.html tests/fixtures/spot.html tests/test_parsers.py
git commit -m "Add food parsers for Jollibee, Chowking; reuse hashed platform parser for Spot.ph"
```

---

## Task 5: Bank parsers (BPI, RCBC, EastWest, Moneymax/Metrobank)

**Files:**
- Create: `scraper/parsers/bank.py`
- Create: `tests/fixtures/bpi.html`
- Create: `tests/fixtures/rcbc.html`
- Create: `tests/fixtures/eastwest.html`
- Create: `tests/fixtures/moneymax_metrobank.html`
- Modify: `tests/test_parsers.py` (add bank section)

**Interfaces:**
- Consumes: `scraper.models.make_deal(...)`.
- Produces: `scraper.parsers.bank.parse_bpi(html, scrape_date)`, `parse_rcbc(html, scrape_date)`, `parse_eastwest(html, scrape_date)`, `parse_moneymax_metrobank(html, scrape_date)` — the last one returns a single-item list (research confirmed this URL is one featured campaign block, not a repeating grid).

- [ ] **Step 1: Copy fixture HTML**

```bash
cp "C:/Users/josed/AppData/Local/Temp/claude/C--Users-josed/35bc89e9-4a6d-41f2-9021-15dd9d628e5d/scratchpad/html/bpi.html" tests/fixtures/bpi.html
cp "C:/Users/josed/AppData/Local/Temp/claude/C--Users-josed/35bc89e9-4a6d-41f2-9021-15dd9d628e5d/scratchpad/html/rcbc.html" tests/fixtures/rcbc.html
cp "C:/Users/josed/AppData/Local/Temp/claude/C--Users-josed/35bc89e9-4a6d-41f2-9021-15dd9d628e5d/scratchpad/html/eastwest.html" tests/fixtures/eastwest.html
cp "C:/Users/josed/AppData/Local/Temp/claude/C--Users-josed/35bc89e9-4a6d-41f2-9021-15dd9d628e5d/scratchpad/html/moneymax_metrobank.html" tests/fixtures/moneymax_metrobank.html
```

- [ ] **Step 2: Write the failing tests**

Append to `tests/test_parsers.py`:
```python
from scraper.parsers import bank


def test_parse_bpi_returns_deals():
    html = _read_fixture("bpi.html")
    deals = bank.parse_bpi(html, "2026-07-03")
    assert len(deals) >= 1
    deal = deals[0]
    assert deal["category"] == "bank"
    assert deal["source"] == "BPI Promos"
    assert deal["discount_text"] != ""
    assert deal["url"].startswith("http")


def test_parse_rcbc_returns_deals():
    html = _read_fixture("rcbc.html")
    deals = bank.parse_rcbc(html, "2026-07-03")
    assert len(deals) >= 1
    deal = deals[0]
    assert deal["category"] == "bank"
    assert deal["source"] == "RCBC Credit Promos"
    assert deal["title"] != ""
    assert deal["url"].startswith("http")


def test_parse_eastwest_returns_deals():
    html = _read_fixture("eastwest.html")
    deals = bank.parse_eastwest(html, "2026-07-03")
    assert len(deals) >= 1
    deal = deals[0]
    assert deal["category"] == "bank"
    assert deal["source"] == "EastWest Promos"
    assert deal["description"] != ""
    assert deal["url"].startswith("http")


def test_parse_moneymax_metrobank_returns_single_deal():
    html = _read_fixture("moneymax_metrobank.html")
    deals = bank.parse_moneymax_metrobank(html, "2026-07-03")
    assert len(deals) == 1
    deal = deals[0]
    assert deal["category"] == "bank"
    assert deal["source"] == "Moneymax Metrobank"
    assert deal["title"] != ""
```

- [ ] **Step 3: Run tests to verify they fail**

Run: `python -m pytest tests/test_parsers.py -v -k bank or bpi or rcbc or eastwest or moneymax`
Expected: FAIL with `ModuleNotFoundError: No module named 'scraper.parsers.bank'`

- [ ] **Step 4: Implement `scraper/parsers/bank.py`**

```python
from bs4 import BeautifulSoup

from scraper.models import make_deal

BPI_BASE = "https://www.bpi.com.ph"
RCBC_BASE = "https://www.rcbccredit.com"
EASTWEST_BASE = "https://www.eastwestbanker.com"


def parse_bpi(html: str, scrape_date: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    deals = []
    for card in soup.select("div.article-page-cont"):
        title_tag = card.select_one("p.tab-head-cont")
        desc_tag = card.select_one("p.article-desc")
        link_tag = card.select_one("a.social-share--component-link")
        if title_tag is None or link_tag is None:
            continue
        title = title_tag.get_text(" ", strip=True)
        description = desc_tag.get_text(" ", strip=True) if desc_tag else ""
        url = link_tag.get("href", "")
        if url.startswith("/"):
            url = f"{BPI_BASE}{url}"
        if not title or not url:
            continue
        deals.append(
            make_deal(
                title=title,
                description=description,
                discount_text=description,
                url=url,
                category="bank",
                source="BPI Promos",
                scrape_date=scrape_date,
            )
        )
    return deals


def parse_rcbc(html: str, scrape_date: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    deals = []
    for card in soup.select("div.promolistmain"):
        title_link = card.select_one("div.title a")
        desc_tag = card.select_one("div.desc")
        if title_link is None:
            continue
        title = title_link.get_text(" ", strip=True)
        url = title_link.get("href", "")
        if url.startswith("/"):
            url = f"{RCBC_BASE}{url}"
        description = desc_tag.get_text(" ", strip=True) if desc_tag else ""
        if not title or not url:
            continue
        deals.append(
            make_deal(
                title=title,
                description=description,
                discount_text="",
                url=url,
                category="bank",
                source="RCBC Credit Promos",
                scrape_date=scrape_date,
            )
        )
    return deals


def parse_eastwest(html: str, scrape_date: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    deals = []
    for card in soup.select("div.card.promo-card"):
        title_tag = card.select_one("div.card-content h3")
        link_tag = card.select_one("div.card-content a")
        desc_tag = card.select_one("div.excerpt p")
        if title_tag is None or link_tag is None:
            continue
        title = title_tag.get_text(" ", strip=True)
        url = link_tag.get("href", "")
        if url.startswith("/"):
            url = f"{EASTWEST_BASE}{url}"
        description = desc_tag.get_text(" ", strip=True) if desc_tag else ""
        if not title or not url:
            continue
        deals.append(
            make_deal(
                title=title,
                description=description,
                discount_text=description,
                url=url,
                category="bank",
                source="EastWest Promos",
                scrape_date=scrape_date,
            )
        )
    return deals


def parse_moneymax_metrobank(html: str, scrape_date: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    block = soup.select_one('div[data-type="PromotionCampaings"]')
    if block is None:
        return []
    title_tag = block.select_one("h4")
    desc_tag = block.select_one("p")
    if title_tag is None:
        return []
    title = title_tag.get_text(" ", strip=True)
    description = desc_tag.get_text(" ", strip=True) if desc_tag else ""
    return [
        make_deal(
            title=title,
            description=description,
            discount_text=description,
            url="https://www.moneymax.ph/credit-card/partners/metrobank",
            category="bank",
            source="Moneymax Metrobank",
            scrape_date=scrape_date,
        )
    ]
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `python -m pytest tests/test_parsers.py -v`
Expected: PASS for all bank tests.

- [ ] **Step 6: Commit**

```bash
git add scraper/parsers/bank.py tests/fixtures/bpi.html tests/fixtures/rcbc.html tests/fixtures/eastwest.html tests/fixtures/moneymax_metrobank.html tests/test_parsers.py
git commit -m "Add bank parsers for BPI, RCBC, EastWest, Moneymax Metrobank"
```

---

## Task 6: Aggregator parser (CollectOffers) and source registry

**Files:**
- Create: `scraper/parsers/aggregator.py`
- Create: `scraper/sources.py`
- Create: `tests/fixtures/collectoffers.html`
- Modify: `tests/test_parsers.py` (add aggregator section)
- Test: `tests/test_sources.py`

**Interfaces:**
- Consumes: `scraper.parsers.ecommerce.parse_hashed_card_platform(...)`, and every parser function defined in Tasks 2-5.
- Produces: `scraper.sources.SOURCES: list[dict]` where each entry is `{"name": str, "url": str, "category": str, "parser": Callable[[str, str], list[dict]]}`. This is what `scraper/scrape.py` (Task 7) iterates over.

- [ ] **Step 1: Copy fixture HTML**

```bash
cp "C:/Users/josed/AppData/Local/Temp/claude/C--Users-josed/35bc89e9-4a6d-41f2-9021-15dd9d628e5d/scratchpad/html/collectoffers.html" tests/fixtures/collectoffers.html
```

- [ ] **Step 2: Write the failing test for the aggregator parser**

Append to `tests/test_parsers.py`:
```python
def test_parse_collectoffers_via_hashed_platform():
    html = _read_fixture("collectoffers.html")
    deals = ecommerce.parse_hashed_card_platform(
        html, "2026-07-03", "CollectOffers PH", container_selector="article._1ve99md1"
    )
    assert len(deals) >= 1
    assert deals[0]["source"] == "CollectOffers PH"
    assert deals[0]["category"] == "ecommerce"
```

Note: CollectOffers is categorized `aggregator` in the source registry (Step 4 below) even though `parse_hashed_card_platform` hardcodes `category="ecommerce"` internally. Fix this now — add a `category` parameter to `parse_hashed_card_platform` so callers control it, rather than special-casing the return value afterward.

- [ ] **Step 3: Update `parse_hashed_card_platform` to accept a `category` parameter**

Modify `scraper/parsers/ecommerce.py` — change the signature and every existing caller (including the 4 call sites already written in Task 3/4 tests):

```python
def parse_hashed_card_platform(
    html: str,
    scrape_date: str,
    source_name: str,
    container_selector: str,
    category: str = "ecommerce",
) -> list[dict]:
```

And change the `make_deal(...)` call inside it from `category="ecommerce"` to `category=category`.

Update the four existing test calls in `tests/test_parsers.py` (VoucherCodes, RewardPay, Yummy, Spot.ph) — no changes needed since `category` now defaults to `"ecommerce"`, matching their existing expected behavior. Add `category="aggregator"` explicitly to the new CollectOffers test call:

```python
def test_parse_collectoffers_via_hashed_platform():
    html = _read_fixture("collectoffers.html")
    deals = ecommerce.parse_hashed_card_platform(
        html,
        "2026-07-03",
        "CollectOffers PH",
        container_selector="article._1ve99md1",
        category="aggregator",
    )
    assert len(deals) >= 1
    assert deals[0]["source"] == "CollectOffers PH"
    assert deals[0]["category"] == "aggregator"
```

- [ ] **Step 4: Run tests to verify the new test fails, others still pass**

Run: `python -m pytest tests/test_parsers.py -v`
Expected: `test_parse_collectoffers_via_hashed_platform` FAILs (function works, but this specific test wasn't run before — actually since `parse_hashed_card_platform` already exists from Task 3, this should mostly work; verify the `category="aggregator"` assertion passes). If it already passes because the signature change was applied correctly, that's fine — proceed to Step 5. If any of the four prior tests (VoucherCodes/RewardPay/Yummy/Spot.ph) now fail due to the signature change, fix their call sites to match the new parameter (they should be unaffected since `category` has a default value).

- [ ] **Step 5: Create a thin `scraper/parsers/aggregator.py` wrapper**

Even though CollectOffers reuses `parse_hashed_card_platform`, give the aggregator category its own module so the registry (Step 6) imports consistently one module per category:

```python
from scraper.parsers.ecommerce import parse_hashed_card_platform


def parse_collectoffers(html: str, scrape_date: str) -> list[dict]:
    return parse_hashed_card_platform(
        html,
        scrape_date,
        "CollectOffers PH",
        container_selector="article._1ve99md1",
        category="aggregator",
    )
```

- [ ] **Step 6: Write the failing test for the source registry**

Create `tests/test_sources.py`:
```python
from scraper.sources import SOURCES


def test_sources_has_sixteen_unique_urls():
    urls = [s["url"] for s in SOURCES]
    assert len(urls) == len(set(urls))
    assert len(SOURCES) == 18


def test_every_source_has_required_keys_and_callable_parser():
    required_keys = {"name", "url", "category", "parser"}
    valid_categories = {"retail", "ecommerce", "food", "bank", "aggregator"}
    for source in SOURCES:
        assert required_keys.issubset(source.keys())
        assert source["category"] in valid_categories
        assert callable(source["parser"])
```

- [ ] **Step 7: Run test to verify it fails**

Run: `python -m pytest tests/test_sources.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'scraper.sources'`

- [ ] **Step 8: Implement `scraper/sources.py`**

```python
from functools import partial

from scraper.parsers import aggregator, bank, ecommerce, food, retail

SOURCES = [
    {
        "name": "SM Sale Events",
        "url": "https://www.smsupermalls.com/mall-sale-events",
        "category": "retail",
        "parser": retail.parse_sm_sale_events,
    },
    {
        "name": "SM Malls Online",
        "url": "https://www.smmallsonline.com/promos-2/",
        "category": "retail",
        "parser": retail.parse_sm_malls_online,
    },
    {
        "name": "Robinsons Malls",
        "url": "https://robinsonsmalls.com/promos-events",
        "category": "retail",
        "parser": retail.parse_robinsons,
    },
    {
        "name": "iPrice Lazada",
        "url": "https://iprice.ph/coupons/lazada/",
        "category": "ecommerce",
        "parser": partial(ecommerce.parse_iprice, store_name="iPrice Lazada"),
    },
    {
        "name": "iPrice Shopee",
        "url": "https://iprice.ph/coupons/shopee/",
        "category": "ecommerce",
        "parser": partial(ecommerce.parse_iprice, store_name="iPrice Shopee"),
    },
    {
        "name": "iPrice Zalora",
        "url": "https://iprice.ph/coupons/zalora/",
        "category": "ecommerce",
        "parser": partial(ecommerce.parse_iprice, store_name="iPrice Zalora"),
    },
    {
        "name": "Rappler Coupons",
        "url": "https://coupons.rappler.com",
        "category": "ecommerce",
        "parser": ecommerce.parse_rappler,
    },
    {
        "name": "VoucherCodes.ph",
        "url": "https://vouchercodes.ph",
        "category": "ecommerce",
        "parser": partial(
            ecommerce.parse_hashed_card_platform,
            source_name="VoucherCodes.ph",
            container_selector="article._1ve99md1",
        ),
    },
    {
        "name": "RewardPay Shopee",
        "url": "https://rewardpay.com/ph/shopee",
        "category": "ecommerce",
        "parser": partial(
            ecommerce.parse_hashed_card_platform,
            source_name="RewardPay Shopee",
            container_selector="article.xffhp0",
        ),
    },
    {
        "name": "Picodi PH",
        "url": "https://picodi.com/ph",
        "category": "ecommerce",
        "parser": ecommerce.parse_picodi,
    },
    {
        "name": "Yummy.ph Coupons",
        "url": "https://coupons.yummy.ph",
        "category": "ecommerce",
        "parser": partial(
            ecommerce.parse_hashed_card_platform,
            source_name="Yummy.ph Coupons",
            container_selector="article._1ve99md1",
        ),
    },
    {
        "name": "Jollibee Promos",
        "url": "https://www.jollibee.com.ph/promos",
        "category": "food",
        "parser": food.parse_jollibee,
    },
    {
        "name": "Chowking Promos",
        "url": "https://chowking.ph/promos",
        "category": "food",
        "parser": food.parse_chowking,
    },
    {
        "name": "Spot.ph Coupons",
        "url": "https://coupons.spot.ph",
        "category": "food",
        "parser": partial(
            ecommerce.parse_hashed_card_platform,
            source_name="Spot.ph Coupons",
            container_selector="article._1ve99md1",
            category="food",
        ),
    },
    {
        "name": "BPI Promos",
        "url": "https://www.bpi.com.ph/personal/rewards-and-promotions/promos",
        "category": "bank",
        "parser": bank.parse_bpi,
    },
    {
        "name": "RCBC Credit Promos",
        "url": "https://www.rcbccredit.com/promos",
        "category": "bank",
        "parser": bank.parse_rcbc,
    },
    {
        "name": "EastWest Promos",
        "url": "https://www.eastwestbanker.com/promos",
        "category": "bank",
        "parser": bank.parse_eastwest,
    },
    {
        "name": "Moneymax Metrobank",
        "url": "https://www.moneymax.ph/credit-card/partners/metrobank",
        "category": "bank",
        "parser": bank.parse_moneymax_metrobank,
    },
    {
        "name": "CollectOffers PH",
        "url": "https://collectoffers.com/ph",
        "category": "aggregator",
        "parser": aggregator.parse_collectoffers,
    },
]
```

Note: every `parser` value must be callable as `parser(html, scrape_date)` — for the `partial`-wrapped ones, `store_name`/`source_name`/`container_selector`/`category` are pre-bound as keyword arguments, leaving `(html, scrape_date)` as the remaining positional slots the runner calls.

- [ ] **Step 9: Run tests to verify they pass**

Run: `python -m pytest tests/ -v`
Expected: All tests PASS, including `test_sources_has_sixteen_unique_urls` (18 entries total — 3 retail + 8 ecommerce + 3 food + 4 bank + 1 aggregator = 19; recount: retail 3, ecommerce (3 iprice + rappler + vouchercodes + rewardpay + picodi + yummy = 8), food 3, bank 4, aggregator 1 → total 19). **Fix the test assertion to `assert len(SOURCES) == 19` before running** — the plan's earlier "16 sources" language refers to unique parser-worthy sites; the registry has 19 rows because 3 are iPrice per-store subpages sharing one parser function. Update Step 6's test file to assert `19`, not `18`, before running this step.

- [ ] **Step 10: Commit**

```bash
git add scraper/parsers/aggregator.py scraper/parsers/ecommerce.py scraper/sources.py tests/fixtures/collectoffers.html tests/test_parsers.py tests/test_sources.py
git commit -m "Add aggregator parser and wire full source registry (19 entries)"
```

---

## Task 7: Scraper runner with merge/expiry logic

**Files:**
- Create: `scraper/scrape.py`
- Test: `tests/test_merge.py`

**Interfaces:**
- Consumes: `scraper.sources.SOURCES`, `scraper.http.fetch(url: str) -> str`.
- Produces: `scraper.scrape.merge_deals(existing: list[dict], freshly_scraped: list[dict], scrape_date: str, expiry_days: int = 14) -> list[dict]` (pure function, no I/O — the testable core of the runner). Also produces `scraper.scrape.run(scrape_date: str) -> tuple[list[dict], list[dict]]` returning `(deals, errors)`, and a `if __name__ == "__main__":` block that calls `run`, loads/writes the JSON files, using today's real date.

- [ ] **Step 1: Write the failing tests for `merge_deals`**

Create `tests/test_merge.py`:
```python
from scraper.scrape import merge_deals


def _deal(title, first_seen, last_seen, source="Test Source"):
    return {
        "title": title,
        "description": "desc",
        "discount_text": "10% off",
        "url": "https://example.com",
        "category": "retail",
        "source": source,
        "first_seen": first_seen,
        "last_seen": last_seen,
    }


def test_new_deal_is_added():
    existing = []
    fresh = [_deal("New Deal", "2026-07-03", "2026-07-03")]
    result = merge_deals(existing, fresh, scrape_date="2026-07-03")
    assert len(result) == 1
    assert result[0]["title"] == "New Deal"
    assert result[0]["first_seen"] == "2026-07-03"
    assert result[0]["last_seen"] == "2026-07-03"


def test_reseen_deal_updates_last_seen_but_keeps_first_seen():
    existing = [_deal("Old Deal", "2026-06-20", "2026-06-25")]
    fresh = [_deal("Old Deal", "2026-07-03", "2026-07-03")]
    result = merge_deals(existing, fresh, scrape_date="2026-07-03")
    assert len(result) == 1
    assert result[0]["first_seen"] == "2026-06-20"
    assert result[0]["last_seen"] == "2026-07-03"


def test_deal_not_reseen_keeps_last_seen_unchanged():
    existing = [_deal("Missed Deal", "2026-06-20", "2026-06-25")]
    fresh = []
    result = merge_deals(existing, fresh, scrape_date="2026-06-28")
    assert len(result) == 1
    assert result[0]["last_seen"] == "2026-06-25"


def test_deal_older_than_14_days_since_last_seen_is_dropped():
    existing = [_deal("Stale Deal", "2026-06-01", "2026-06-10")]
    fresh = []
    result = merge_deals(existing, fresh, scrape_date="2026-06-25")
    assert result == []


def test_deal_exactly_14_days_since_last_seen_is_kept():
    existing = [_deal("Borderline Deal", "2026-06-01", "2026-06-10")]
    fresh = []
    result = merge_deals(existing, fresh, scrape_date="2026-06-24")
    assert len(result) == 1


def test_result_sorted_newest_first_seen_first():
    existing = [
        _deal("Older", "2026-06-01", "2026-06-01"),
        _deal("Newer", "2026-06-15", "2026-06-15"),
    ]
    result = merge_deals(existing, [], scrape_date="2026-06-15")
    assert [d["title"] for d in result] == ["Newer", "Older"]
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_merge.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'scraper.scrape'`

- [ ] **Step 3: Implement `scraper/scrape.py`**

```python
import json
from datetime import date, datetime
from pathlib import Path

from scraper.http import fetch
from scraper.sources import SOURCES

DATA_DIR = Path(__file__).parent.parent / "data"
DEALS_PATH = DATA_DIR / "deals.json"
ERRORS_PATH = DATA_DIR / "last_run_errors.json"
EXPIRY_DAYS = 14


def _dedup_key(deal: dict) -> tuple:
    return (deal["source"], deal["title"], deal["discount_text"])


def _days_between(earlier: str, later: str) -> int:
    return (datetime.fromisoformat(later) - datetime.fromisoformat(earlier)).days


def merge_deals(
    existing: list[dict],
    freshly_scraped: list[dict],
    scrape_date: str,
    expiry_days: int = EXPIRY_DAYS,
) -> list[dict]:
    by_key = {_dedup_key(deal): dict(deal) for deal in existing}

    for deal in freshly_scraped:
        key = _dedup_key(deal)
        if key in by_key:
            by_key[key]["last_seen"] = scrape_date
        else:
            by_key[key] = dict(deal)

    kept = [
        deal
        for deal in by_key.values()
        if _days_between(deal["last_seen"], scrape_date) <= expiry_days
    ]
    kept.sort(key=lambda d: d["first_seen"], reverse=True)
    return kept


def run(scrape_date: str) -> tuple[list[dict], list[dict]]:
    freshly_scraped = []
    errors = []

    for source in SOURCES:
        try:
            html = fetch(source["url"])
            deals = source["parser"](html, scrape_date)
            freshly_scraped.extend(deals)
        except Exception as exc:  # noqa: BLE001 - any source failure must not stop the run
            errors.append(
                {
                    "source": source["name"],
                    "url": source["url"],
                    "error": str(exc),
                    "timestamp": scrape_date,
                }
            )

    existing = []
    if DEALS_PATH.exists():
        existing = json.loads(DEALS_PATH.read_text(encoding="utf-8"))

    merged = merge_deals(existing, freshly_scraped, scrape_date)
    return merged, errors


if __name__ == "__main__":
    today = date.today().isoformat()
    deals, errors = run(today)
    DATA_DIR.mkdir(exist_ok=True)
    DEALS_PATH.write_text(json.dumps(deals, indent=2, ensure_ascii=False), encoding="utf-8")
    ERRORS_PATH.write_text(json.dumps(errors, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {len(deals)} deals, {len(errors)} source errors.")
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/test_merge.py -v`
Expected: PASS for all 6 merge tests.

- [ ] **Step 5: Run the full test suite**

Run: `python -m pytest tests/ -v`
Expected: All tests across all files PASS.

- [ ] **Step 6: Commit**

```bash
git add scraper/scrape.py tests/test_merge.py
git commit -m "Add scraper runner with dedup, 14-day expiry, and per-source error isolation"
```

---

## Task 8: End-to-end manual run against live sources

**Files:**
- Modify: none (verification task)
- Create: `data/deals.json`, `data/last_run_errors.json` (generated output, committed as the initial data snapshot)

**Interfaces:**
- Consumes: `scraper.scrape.run(scrape_date)` end to end against real network calls (no fixtures).

This task has no new code — it verifies Tasks 1-7 work against the real internet, not just saved fixtures, before wiring up CI automation.

- [ ] **Step 1: Install dependencies in a clean environment**

Run: `pip install -r requirements.txt`
Expected: `requests`, `beautifulsoup4`, `pytest` install without errors.

- [ ] **Step 2: Run the full test suite one more time**

Run: `python -m pytest tests/ -v`
Expected: All tests PASS (confirms nothing broke from the dependency install).

- [ ] **Step 3: Run the scraper against live sources**

Run: `python -m scraper.scrape`
Expected output: `Wrote N deals, M source errors.` where N > 0. Some M > 0 is acceptable (a handful of the 19 sources may fail on any given day due to site changes) — but if M is close to 19, something structural is wrong (e.g. outbound network blocked, or the UA header being rejected everywhere) and must be investigated before proceeding.

- [ ] **Step 4: Inspect the output**

Read `data/deals.json` and confirm:
- It's a non-empty JSON array.
- Spot-check 3-4 entries across different `category` values — each has non-empty `title`, `url` starting with `http`, and a `source` matching an entry in `scraper/sources.py`.

Read `data/last_run_errors.json` and, for any entries present, note which sources failed and why — this tells you if a selector needs adjusting (real sites can differ slightly from the research fixtures if the page changed between research and now).

- [ ] **Step 5: Fix any structurally-broken parsers found in Step 4**

If a source that worked against its fixture fails live (e.g. selector no longer matches because the site changed in the intervening hours), update that parser function in its category file, re-run `python -m scraper.scrape`, and confirm the error disappears. If a source fails for a reason outside the plan's control (site now requires JS, is down, blocks the request entirely), leave it as a logged error — it degrades gracefully per the spec's error-handling design, and can be revisited later without blocking the rest of the pipeline.

- [ ] **Step 6: Commit the initial data snapshot**

```bash
git add data/deals.json data/last_run_errors.json
git commit -m "Add initial live-scraped data snapshot"
```

---

## Task 9: GitHub Actions workflows (scrape cron + test CI)

**Files:**
- Create: `.github/workflows/scrape.yml`
- Create: `.github/workflows/test.yml`

**Interfaces:**
- Consumes: `scraper/scrape.py` (as `python -m scraper.scrape`), `requirements.txt`, `tests/`.
- Produces: two GitHub Actions workflows visible under the repo's Actions tab.

- [ ] **Step 1: Create the test workflow**

Create `.github/workflows/test.yml`:
```yaml
name: Test

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install -r requirements.txt
      - run: python -m pytest tests/ -v
```

- [ ] **Step 2: Create the scrape workflow**

Create `.github/workflows/scrape.yml`:
```yaml
name: Scrape Deals

on:
  schedule:
    - cron: "0 22 * * *"
  workflow_dispatch: {}

permissions:
  contents: write

jobs:
  scrape:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install -r requirements.txt
      - run: python -m scraper.scrape
      - name: Commit updated data if changed
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git add data/deals.json data/last_run_errors.json
          git diff --staged --quiet || git commit -m "Update scraped deals ($(date -u +%Y-%m-%d))"
          git push
```

The `cron: "0 22 * * *"` runs at 22:00 UTC daily, which is 06:00 Asia/Manila (UTC+8) — matches the spec's daily 6am PH time cadence.

- [ ] **Step 3: Commit the workflows**

```bash
git add .github/workflows/scrape.yml .github/workflows/test.yml
git commit -m "Add GitHub Actions workflows for daily scraping and CI tests"
```

- [ ] **Step 4: Verification note (post-push, manual)**

This step can only be verified after the repo is pushed to GitHub (Task 11). Record it here so it isn't skipped: after pushing, go to the Actions tab and manually trigger "Scrape Deals" via `workflow_dispatch` to confirm it runs end-to-end in CI (not just locally) before relying on the cron schedule.

---

## Task 10: Static site (`site/index.html`)

**Files:**
- Create: `site/index.html`

**Interfaces:**
- Consumes: `data/deals.json` (relative fetch path `../data/deals.json` from `site/index.html`'s location) matching the exact shape produced by `scraper.models.make_deal`: `{title, description, discount_text, url, category, source, first_seen, last_seen}`.

- [ ] **Step 1: Create the static site file**

Create `site/index.html`:
```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>PH Discounts Tracker</title>
<style>
  :root {
    color-scheme: light dark;
    --bg: #ffffff;
    --fg: #1a1a1a;
    --card-bg: #f5f5f5;
    --accent: #0a7d3c;
    --muted: #666666;
  }
  @media (prefers-color-scheme: dark) {
    :root {
      --bg: #121212;
      --fg: #e8e8e8;
      --card-bg: #1e1e1e;
      --accent: #4ade80;
      --muted: #a0a0a0;
    }
  }
  * { box-sizing: border-box; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    background: var(--bg);
    color: var(--fg);
    margin: 0;
    padding: 1.5rem;
    max-width: 800px;
    margin-inline: auto;
  }
  h1 { font-size: 1.5rem; margin-bottom: 0.25rem; }
  .subtitle { color: var(--muted); margin-top: 0; margin-bottom: 1.25rem; font-size: 0.9rem; }
  .filters { display: flex; flex-wrap: wrap; gap: 0.5rem; margin-bottom: 1.5rem; }
  .filter-chip {
    padding: 0.4rem 0.9rem;
    border-radius: 999px;
    border: 1px solid var(--muted);
    background: transparent;
    color: var(--fg);
    cursor: pointer;
    font-size: 0.85rem;
  }
  .filter-chip.active { background: var(--accent); color: #ffffff; border-color: var(--accent); }
  .deal-card {
    background: var(--card-bg);
    border-radius: 12px;
    padding: 1rem 1.25rem;
    margin-bottom: 0.75rem;
  }
  .deal-title { font-weight: 600; margin: 0 0 0.25rem; }
  .deal-discount { color: var(--accent); font-weight: 600; font-size: 0.9rem; }
  .deal-description { color: var(--muted); font-size: 0.9rem; margin: 0.4rem 0; }
  .deal-meta { font-size: 0.8rem; color: var(--muted); display: flex; justify-content: space-between; margin-top: 0.5rem; }
  .deal-meta a { color: var(--fg); }
  #empty-state { color: var(--muted); text-align: center; padding: 2rem 0; }
</style>
</head>
<body>
  <h1>PH Discounts Tracker</h1>
  <p class="subtitle">Nationwide Philippines discounts, scraped daily. Deals disappear 14 days after they stop showing up on their source.</p>
  <div class="filters" id="filters"></div>
  <div id="deals"></div>
  <div id="empty-state" style="display:none;">No deals match this filter.</div>

  <script>
    const CATEGORIES = ["retail", "ecommerce", "food", "bank", "aggregator"];
    let allDeals = [];
    let activeCategory = "all";

    function daysAgo(dateStr) {
      const diffMs = Date.now() - new Date(dateStr + "T00:00:00").getTime();
      const days = Math.floor(diffMs / 86400000);
      if (days <= 0) return "today";
      if (days === 1) return "1 day ago";
      return `${days} days ago`;
    }

    function renderFilters() {
      const container = document.getElementById("filters");
      const options = ["all", ...CATEGORIES];
      container.innerHTML = options
        .map(
          (cat) =>
            `<button class="filter-chip${cat === activeCategory ? " active" : ""}" data-category="${cat}">${cat}</button>`
        )
        .join("");
      container.querySelectorAll(".filter-chip").forEach((btn) => {
        btn.addEventListener("click", () => {
          activeCategory = btn.dataset.category;
          renderFilters();
          renderDeals();
        });
      });
    }

    function renderDeals() {
      const container = document.getElementById("deals");
      const emptyState = document.getElementById("empty-state");
      const filtered =
        activeCategory === "all"
          ? allDeals
          : allDeals.filter((d) => d.category === activeCategory);

      if (filtered.length === 0) {
        container.innerHTML = "";
        emptyState.style.display = "block";
        return;
      }
      emptyState.style.display = "none";

      container.innerHTML = filtered
        .map(
          (deal) => `
        <div class="deal-card">
          <p class="deal-title">${escapeHtml(deal.title)}</p>
          ${deal.discount_text ? `<p class="deal-discount">${escapeHtml(deal.discount_text)}</p>` : ""}
          ${deal.description ? `<p class="deal-description">${escapeHtml(deal.description)}</p>` : ""}
          <div class="deal-meta">
            <a href="${escapeAttr(deal.url)}" target="_blank" rel="noopener">${escapeHtml(deal.source)}</a>
            <span>seen ${daysAgo(deal.last_seen)}</span>
          </div>
        </div>`
        )
        .join("");
    }

    function escapeHtml(str) {
      const div = document.createElement("div");
      div.textContent = str;
      return div.innerHTML;
    }

    function escapeAttr(str) {
      return str.replace(/"/g, "&quot;");
    }

    fetch("../data/deals.json")
      .then((res) => res.json())
      .then((data) => {
        allDeals = data;
        renderFilters();
        renderDeals();
      })
      .catch(() => {
        document.getElementById("deals").innerHTML =
          '<p id="empty-state">Could not load deals data.</p>';
      });
  </script>
</body>
</html>
```

- [ ] **Step 2: Manual verification — serve the site locally**

Run: `python -m http.server 8000` from the repo root, then open `http://localhost:8000/site/index.html` in a browser.

Expected: the page loads, shows the deals from `data/deals.json` (populated in Task 8), filter chips work (clicking "food" shows only food-category deals, "all" shows everything), each card shows a title, discount text (when present), description (when present), a clickable source link, and a "seen X days ago" label.

- [ ] **Step 3: Commit**

```bash
git add site/index.html
git commit -m "Add static site for browsing scraped deals with category filters"
```

---

## Task 11: README, GitHub repo creation, and Pages configuration

**Files:**
- Create: `README.md`

**Interfaces:** none — this task wires the local repo to GitHub and turns on Pages.

- [ ] **Step 1: Write the README**

Create `README.md`:
```markdown
# PH Discounts Tracker

Nationwide Philippines discounts and promos, scraped daily from 19 curated
sources (retail, e-commerce, food, and bank/credit card promo pages) and
published as a free static site.

## How it works

- `.github/workflows/scrape.yml` runs `scraper/scrape.py` daily at 06:00
  Asia/Manila time via GitHub Actions.
- Results are normalized, deduplicated, and merged into `data/deals.json`.
  A deal is dropped 14 days after it stops appearing in a scrape.
- `site/index.html` is a dependency-free static page that reads
  `data/deals.json` directly and renders a filterable feed. Published via
  GitHub Pages.

## Adding a new source

1. Add a parser function to the relevant file under `scraper/parsers/`
   (or a new file for a new category) following the existing
   `parse(html: str, scrape_date: str) -> list[dict]` signature.
2. Add a fixture HTML file under `tests/fixtures/` and a test in
   `tests/test_parsers.py`.
3. Add an entry to `SOURCES` in `scraper/sources.py`.

## Local development

```bash
pip install -r requirements.txt
python -m pytest tests/ -v
python -m scraper.scrape
python -m http.server 8000   # then open http://localhost:8000/site/index.html
```
```

- [ ] **Step 2: Commit the README**

```bash
git add README.md
git commit -m "Add README"
```

- [ ] **Step 3: Create the GitHub repository**

Run: `gh repo create ph-discounts-tracker --public --source=. --remote=origin --push`
Expected: repo created under the authenticated account (AIinterruptor) and all commits pushed to `main`.

- [ ] **Step 4: Enable GitHub Pages**

Run: `gh api repos/AIinterruptor/ph-discounts-tracker/pages -X POST -f "source[branch]=main" -f "source[path]=/site"`
Expected: JSON response confirming Pages is configured to serve from `main` branch, `/site` directory. If this returns an error because `/site` isn't a supported path value (GitHub Pages only supports `/` or `/docs` for non-Actions-based deployment), instead move `site/index.html` to `docs/index.html` (adjust the `fetch("../data/deals.json")` path in Task 10 accordingly — verify the relative path still resolves) and re-run with `-f "source[path]=/docs"`.

- [ ] **Step 5: Verify Pages is live**

Run: `gh api repos/AIinterruptor/ph-discounts-tracker/pages --jq .html_url`
Expected: a `https://aiinterruptor.github.io/ph-discounts-tracker/` URL. Fetch it (or open in browser) after a minute or two (Pages build takes a short time) and confirm the deals feed renders with real data.

- [ ] **Step 6: Manually trigger the scrape workflow to confirm CI works end-to-end**

Run: `gh workflow run scrape.yml --repo AIinterruptor/ph-discounts-tracker`

Wait about 30-60 seconds, then run: `gh run list --repo AIinterruptor/ph-discounts-tracker --workflow=scrape.yml --limit 1`

Expected: the run shows status `completed` and conclusion `success`. If it fails, run `gh run view --repo AIinterruptor/ph-discounts-tracker --log-failed` to see the error and fix it (common culprits: missing `permissions: contents: write` in the workflow, or a source that started failing between local testing and now).

---

## Plan Self-Review Notes

- **Spec coverage:** daily cadence (Task 9), 17→19-source registry with category coverage across all 4 required categories plus aggregator (Task 6), 14-day expiry (Task 7), single-feed site with category filters (Task 10), per-source error isolation (Task 7 `run()`), pytest with fixtures (Tasks 2-7), GitHub Actions cron + manual dispatch (Task 9), GitHub Pages (Task 11) — all spec sections have a corresponding task.
- **Source count discrepancy resolved:** the spec said "17 sources"; live HTML verification (done after the spec was written, during plan authoring) dropped 3 non-viable sources and added 3 iPrice per-store subpages, netting 19 registry entries. This is called out explicitly in the plan's "Source List" section and Task 6 Step 9 rather than silently mismatching the spec.
- **Placeholder scan:** no TBD/TODO markers; every code step has complete, real code (not paraphrased); every "adjust if this fails" instruction includes the concrete diagnostic command to run, not just "handle errors."
- **Type/signature consistency:** every parser function follows `(html: str, scrape_date: str) -> list[dict]` (with `partial`-bound extra kwargs for shared functions), matching what `scraper/sources.py` and `scraper/scrape.py` expect. `make_deal(...)`'s parameter names and return keys are used identically across all parser modules.
