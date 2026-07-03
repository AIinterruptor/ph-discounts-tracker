from pathlib import Path

from scraper.parsers import ecommerce, retail

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
    assert deal["url"] == "https://www.vouchercodes.ph"


def test_parse_hashed_card_platform_rewardpay():
    html = _read_fixture("rewardpay.html")
    deals = ecommerce.parse_hashed_card_platform(
        html, "2026-07-03", "RewardPay Shopee", container_selector="article.xffhp0"
    )
    assert len(deals) >= 1
    assert deals[0]["source"] == "RewardPay Shopee"
    assert deals[0]["url"] == "https://www.rewardpay.com/ph/shopee"
    assert deals[0]["discount_text"] != ""
    assert deals[0]["description"] != ""


def test_parse_hashed_card_platform_yummy():
    html = _read_fixture("yummy.html")
    deals = ecommerce.parse_hashed_card_platform(
        html, "2026-07-03", "Yummy.ph Coupons", container_selector="article._1ve99md1"
    )
    assert len(deals) >= 1
    assert deals[0]["source"] == "Yummy.ph Coupons"
    assert deals[0]["url"] == "https://coupons.yummy.ph"


def test_parse_picodi_returns_deals():
    html = _read_fixture("picodi.html")
    deals = ecommerce.parse_picodi(html, "2026-07-03")
    assert len(deals) >= 1
    deal = deals[0]
    assert deal["category"] == "ecommerce"
    assert deal["source"] == "Picodi PH"
    assert deal["title"] != ""
