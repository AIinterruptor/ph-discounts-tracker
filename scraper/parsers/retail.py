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
