import pytest
from unittest.mock import MagicMock

from src.product_scrapers.scrapers.manager.scraper_manager import ScraperManager

@pytest.fixture
def mock_scraper():
    scraper = MagicMock()
    scraper.search.return_value = ["url1", "url2"]
    scraper.scrape_data.return_value = {"url": "url1", "data": "info"}
    scraper.update_data.return_value = {"url": "url1", "updated": True}
    return scraper

@pytest.fixture
def manager(mock_scraper):
    return ScraperManager(scraper=mock_scraper)

def test_get_products_urls(manager, mock_scraper):
    result = manager.get_products_urls("notebook")
    mock_scraper.search.assert_called_once_with("notebook")
    assert result == ["url1", "url2"]

def test_scrape_product(manager, mock_scraper):
    result = manager.scrape_product("url1")
    mock_scraper.scrape_data.assert_called_once_with("url1")
    assert result == {"url": "url1", "data": "info"}

def test_update_product(manager, mock_scraper):
    product = {"url": "url1"}
    result = manager.update_product(product)
    mock_scraper.update_data.assert_called_once_with(product)
    assert result == {"url": "url1", "updated": True}

def test_get_urls_to_update():
    existing = ["a", "b"]
    urls = ["a", "b", "c", "d"]
    result = ScraperManager.get_urls_to_update(existing, urls)
    assert set(result) == {"c", "d"}

def test_split_search_urls(manager):
    search_results = {"search": "notebook", "urls": ["a", "b", "c", "d", "e"]}
    chunks = list(manager.split_search_urls(search_results, chunk_size=2))
    assert chunks == [["a", "b"], ["c", "d"], ["e"]]

def test__get_search_urls():
    search_results = {"search": "notebook", "urls": ["a", "b"]}
    urls = ScraperManager._get_search_urls(search_results)
    assert urls == ["a", "b"]

def test__chunk_urls():
    urls = ["a", "b", "c", "d", "e"]
    chunks = list(ScraperManager._chunk_urls(urls, chunk_size=2))
    assert chunks == [["a", "b"], ["c", "d"], ["e"]]
