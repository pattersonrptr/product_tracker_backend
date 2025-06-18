import pytest
from unittest.mock import patch, MagicMock

from src.product_scrapers.scrapers.enjoei import EnjoeiScraper


@pytest.fixture
def scraper():
    return EnjoeiScraper()


def test_headers_with_random_user_agent(scraper):
    with patch.object(scraper, "get_random_user_agent", return_value="UA_TEST"):
        headers = scraper.headers()
        assert headers["User-Agent"] == "UA_TEST"
        assert "Accept-Language" in headers


def test_headers_without_random_user_agent(scraper):
    with patch.object(scraper, "get_random_user_agent", return_value=None):
        headers = scraper.headers()
        assert headers["User-Agent"].startswith("Mozilla/")
        assert "Accept-Language" in headers


@patch.object(EnjoeiScraper, "retry_request")
def test__get_search_data_calls_retry_request(mock_retry, scraper):
    mock_retry.return_value = MagicMock()
    _ = scraper._get_search_data("notebook", after="abc")
    mock_retry.assert_called_once()
    args, kwargs = mock_retry.call_args
    assert "graphql-search-x" in args[0]
    assert kwargs["params"]["term"] == "notebook"
    assert kwargs["params"]["after"] == "abc"


def test__extract_links_normal(scraper):
    data = {
        "data": {
            "search": {
                "products": {
                    "edges": [
                        {"node": {"id": "123"}, "cursor": "CURSOR1"},
                        {"node": {"id": "456"}, "cursor": "CURSOR2"},
                    ]
                }
            }
        }
    }
    urls, cursor = scraper._extract_links(data)
    assert urls[0].endswith("/123/v2.json")
    assert urls[1].endswith("/456/v2.json")
    assert cursor == "CURSOR2"


def test__extract_links_empty(scraper):
    data = {}
    urls, cursor = scraper._extract_links(data)
    assert urls == []
    assert cursor is None


@patch.object(EnjoeiScraper, "_get_search_data")
@patch.object(EnjoeiScraper, "_extract_links")
def test_search_multiple_pages(mock_extract_links, mock_get_search_data, scraper):
    # Simula duas páginas: primeira retorna cursor, segunda não
    mock_resp = MagicMock()
    mock_get_search_data.return_value = mock_resp
    mock_extract_links.side_effect = [
        (["url1"], "CURSOR"),
        (["url2"], None),
    ]
    result = scraper.search("notebook")
    assert result == ["url1", "url2"]
    assert mock_get_search_data.call_count == 2


@patch.object(EnjoeiScraper, "retry_request")
def test_scrape_data_success(mock_retry, scraper):
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "canonical_url": "https://pages.enjoei.com.br/products/123",
        "title": "Produto",
        "fallback_pricing": {"price": {"listed": "100"}, "state": "published"},
        "description": "desc",
        "photos": ["photo1"],
        "id": "123",
    }
    mock_retry.return_value = mock_response
    data = scraper.scrape_data("http://test.com")
    assert data["url"].endswith("/123")
    assert data["price"] == "100"
    assert data["is_available"] is True
    assert "image_urls" in data


@patch.object(EnjoeiScraper, "scrape_data")
def test_update_data_merges_product_and_updated(scrape_data_mock, scraper):
    scrape_data_mock.return_value = {"url": "abc", "price": "200"}
    product = {"url": "https://pages.enjoei.com.br/products/abc"}
    updated = scraper.update_data(product)
    assert updated["url"] == "abc"
    assert updated["price"] == "200"


def test_str_repr(scraper):
    assert str(scraper) == "Enjoei Scraper"
