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
