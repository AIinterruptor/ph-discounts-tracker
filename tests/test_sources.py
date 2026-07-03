from scraper.sources import SOURCES


def test_sources_has_sixteen_unique_urls():
    urls = [s["url"] for s in SOURCES]
    assert len(urls) == len(set(urls))
    assert len(SOURCES) == 19


def test_every_source_has_required_keys_and_callable_parser():
    required_keys = {"name", "url", "category", "parser"}
    valid_categories = {"retail", "ecommerce", "food", "bank", "aggregator"}
    for source in SOURCES:
        assert required_keys.issubset(source.keys())
        assert source["category"] in valid_categories
        assert callable(source["parser"])
