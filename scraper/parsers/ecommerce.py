from bs4 import BeautifulSoup

from scraper.models import make_deal


def parse_iprice(html: str, scrape_date: str, store_name: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    deals = []
    for card in soup.select("div.rh_offer_list"):
        title_tag = card.select_one("h2 a")
        if title_tag is None:
            continue
        title = title_tag.get_text(" ", strip=True)
        url = title_tag.get("href", "")
        discount_tag = card.select_one(".sale_letter, .rh_custom_notice")
        discount_text = discount_tag.get_text(" ", strip=True) if discount_tag else ""
        desc_tag = card.select_one(".rh_gr_middle_desc")
        description = desc_tag.get_text(" ", strip=True) if desc_tag else ""
        if not title or not url:
            continue
        deals.append(
            make_deal(
                title=title,
                description=description,
                discount_text=discount_text,
                url=url,
                category="ecommerce",
                source=store_name,
                scrape_date=scrape_date,
            )
        )
    return deals


def parse_rappler(html: str, scrape_date: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    deals = []
    for item in soup.select("li.rappler-table"):
        title_tag = item.select_one(".description h3")
        store_link = item.select_one(".store a")
        if title_tag is None or store_link is None:
            continue
        title = title_tag.get_text(" ", strip=True)
        url = store_link.get("href", "")
        if not title or not url:
            continue
        deals.append(
            make_deal(
                title=title,
                description="",
                discount_text="",
                url=url,
                category="ecommerce",
                source="Rappler Coupons",
                scrape_date=scrape_date,
            )
        )
    return deals


def parse_hashed_card_platform(
    html: str,
    scrape_date: str,
    source_name: str,
    container_selector: str,
    category: str = "ecommerce",
) -> list[dict]:
    """Shared parser for the coupon-site platform used by VoucherCodes.ph,
    RewardPay, Yummy.ph, and CollectOffers. Build-hashed classes regenerate
    on redeploy, so fields are located structurally rather than by class name.

    Two real layouts were confirmed against saved fixtures:

    - VoucherCodes.ph / Yummy.ph (shared "_1ve99md1" template family): each
      card has exactly 5 non-nested leaf `<div>`s in document order —
      discount, type label, brand, title, description. Detected by the
      *absence* of an `<h3>` title element.
    - RewardPay ("xffhp0" template family): title lives in an `<h3>`, discount
      in `.ignouk1`, description in `._18yuqec0`. Detected by the *presence*
      of an `<h3>`.

    Neither layout exposes a real per-offer URL in the static HTML (the
    "claim" buttons are client-side JS with a `data-offer` token, not an
    anchor href) — so instead of fabricating one or borrowing an unrelated
    link (e.g. RewardPay's "Published By" author link), every deal is given
    the page's own canonical URL: `<link rel="canonical">` if present, else
    `<meta property="og:url">`, else an empty string if neither exists.
    """
    soup = BeautifulSoup(html, "html.parser")
    canonical_tag = soup.select_one("link[rel=canonical]")
    if canonical_tag is not None and canonical_tag.get("href"):
        page_url = canonical_tag.get("href", "")
    else:
        og_url_tag = soup.select_one('meta[property="og:url"]')
        page_url = og_url_tag.get("content", "") if og_url_tag is not None else ""

    deals = []
    for card in soup.select(container_selector):
        h3 = card.select_one("h3")
        if h3 is not None:
            # RewardPay-style layout: title in <h3>, discount/description
            # in dedicated (non-hashed-position-dependent) elements.
            title = h3.get_text(" ", strip=True)
            discount_tag = card.select_one(".ignouk1")
            discount_text = discount_tag.get_text(" ", strip=True) if discount_tag else ""
            desc_tag = card.select_one("._18yuqec0")
            description = desc_tag.get_text(" ", strip=True) if desc_tag else ""
        else:
            # VoucherCodes.ph / Yummy.ph-style layout: positional leaf divs.
            leaf_divs = [
                d
                for d in card.find_all("div", recursive=True)
                if d.get_text(strip=True) and not d.find("div")
            ]
            if len(leaf_divs) < 4:
                continue
            texts = [d.get_text(" ", strip=True) for d in leaf_divs]
            discount_text, _type_label, _brand, title = texts[0], texts[1], texts[2], texts[3]
            description = texts[4] if len(texts) > 4 else ""

        if not title:
            continue
        deals.append(
            make_deal(
                title=title,
                description=description,
                discount_text=discount_text,
                url=page_url,
                category=category,
                source=source_name,
                scrape_date=scrape_date,
            )
        )
    return deals


def parse_picodi(html: str, scrape_date: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    deals = []
    for slide in soup.select("li.brandbar__slide"):
        link = slide.select_one("a.brandbar__link")
        if link is None:
            continue
        url = link.get("href", "")
        if url.startswith("/"):
            url = f"https://picodi.com{url}"
        img = slide.select_one("img")
        title = img.get("alt", "").strip() if img else ""
        cashback = slide.select_one(".brandbar__cashback-label")
        discount_text = cashback.get_text(" ", strip=True) if cashback else ""
        if not title or not url:
            continue
        deals.append(
            make_deal(
                title=title,
                description="",
                discount_text=discount_text,
                url=url,
                category="ecommerce",
                source="Picodi PH",
                scrape_date=scrape_date,
            )
        )
    return deals
