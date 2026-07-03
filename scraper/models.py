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
