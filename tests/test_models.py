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
