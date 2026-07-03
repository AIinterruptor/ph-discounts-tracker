from scraper.parsers.ecommerce import parse_hashed_card_platform


def parse_collectoffers(html: str, scrape_date: str) -> list[dict]:
    return parse_hashed_card_platform(
        html,
        scrape_date,
        "CollectOffers PH",
        container_selector="article._1ve99md1",
        category="aggregator",
    )
