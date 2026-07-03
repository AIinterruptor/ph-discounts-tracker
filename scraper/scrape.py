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
