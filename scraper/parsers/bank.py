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
