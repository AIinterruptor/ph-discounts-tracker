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
