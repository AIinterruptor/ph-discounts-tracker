from bs4 import BeautifulSoup

from scraper.models import make_deal


def parse_jollibee(html: str, scrape_date: str) -> list[dict]:
    """Jollibee promo cards carry no discount/description text (confirmed
    against the saved fixture — only a title and a "Learn more" link), so
    discount_text and description are left empty. The site still has value
    as a "new promo announced" feed.
    """
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
    """Chowking promo cards carry the title only in the anchor's `title`
    attribute (no visible text), confirmed against the saved fixture.
    """
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
