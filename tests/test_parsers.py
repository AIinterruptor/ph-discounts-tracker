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
