import pytest
from unittest.mock import patch, MagicMock

from src.product_scrapers.scrapers.olx import OLXScraper


@pytest.fixture
def scraper():
    return OLXScraper()


def test_headers_with_random_user_agent(scraper):
    with patch.object(scraper, "get_random_user_agent", return_value="UA_TEST"):
        headers = scraper.headers()
        assert headers["User-Agent"] == "UA_TEST"
        assert "Accept-Language" in headers


def test_headers_without_random_user_agent(scraper):
    with patch.object(scraper, "get_random_user_agent", return_value=None):
        headers = scraper.headers()
        assert "User-Agent" not in headers or headers["User-Agent"] != ""
        assert "Accept-Language" in headers


@patch.object(OLXScraper, "retry_request")
@patch.object(OLXScraper, "_extract_links")
def test_search_success(mock_extract_links, mock_retry, scraper):
    mock_resp = MagicMock()
    mock_resp.text = "<html></html>"
    mock_retry.return_value = mock_resp

    mock_extract_links.side_effect = [
        ["url1", "url2"],
        [],
    ]
    result = scraper.search("notebook")
    assert result == ["url1", "url2"]
    assert mock_extract_links.call_count == 2


@patch.object(OLXScraper, "retry_request")
def test_search_no_results(mock_retry, scraper):
    mock_resp = MagicMock()
    mock_resp.text = ""
    mock_retry.return_value = mock_resp
    with pytest.raises(Exception, match="No results found"):
        scraper.search("notebook")


def test_build_search_url(scraper):
    url = scraper._build_search_url("notebook", 2)
    assert "notebook" in url
    assert "&o=2" in url


def test_extract_links_success(scraper):
    html_content = """
    <html>
      <script id="__NEXT_DATA__">
        {"props":{"pageProps":{"ads":[{"url":"https://olx.com.br/item1"},{"url":"https://olx.com.br/item2"}]}}}
      </script>
    </html>
    """
    urls = scraper._extract_links(html_content)
    assert "https://olx.com.br/item1" in urls
    assert "https://olx.com.br/item2" in urls


def test_extract_links_no_data(scraper):
    html_content = "<html></html>"
    with pytest.raises(Exception, match="No data found"):
        scraper._extract_links(html_content)


def test_extract_links_no_ads(scraper):
    html_content = """
    <html>
      <script id="__NEXT_DATA__">
        {"props":{"pageProps":{}}}
      </script>
    </html>
    """
    with pytest.raises(Exception, match="No ads data found"):
        scraper._extract_links(html_content)


def test_extract_json_data_success(scraper):
    class SoupMock:
        def find(self, tag, attrs):
            if tag == "script" and attrs.get("id") == "initial-data":

                class Script:
                    def __getitem__(self, key):
                        if key == "data-json":
                            return '{"ad": {"subject": "t", "body": "d", "listId": "1", "priceValue": "R$ 100,00", "images": [{"original": "img"}], "user": {"name": "seller"}, "location": {"municipality": "city", "uf": "state"}}}'

                return Script()
            return None

    soup = SoupMock()
    data = scraper._extract_json_data(soup)
    assert data["subject"] == "t"
    assert data["priceValue"] == "R$ 100,00"


@patch.object(OLXScraper, "retry_request")
def test_scrape_data_success(mock_retry, scraper):
    html = """
    <html>
      <script id="initial-data" data-json='{"ad": {"subject": "t", "body": "d", "listId": "1", "priceValue": "R$ 100,00", "images": [{"original": "img"}], "user": {"name": "seller"}, "location": {"municipality": "city", "uf": "state"}}}'></script>
    </html>
    """
    mock_resp = MagicMock()
    mock_resp.content = html
    mock_retry.return_value = mock_resp

    # Patch BeautifulSoup to use our SoupMock
    with patch("src.product_scrapers.scrapers.olx.BeautifulSoup") as bs_mock:
        soup_mock = MagicMock()
        bs_mock.return_value = soup_mock
        soup_mock.find.return_value = MagicMock()
        soup_mock.find.return_value.__getitem__.side_effect = (
            lambda k: '{"ad": {"subject": "t", "body": "d", "listId": "1", "priceValue": "R$ 100,00", "images": [{"original": "img"}], "user": {"name": "seller"}, "location": {"municipality": "city", "uf": "state"}}}'
            if k == "data-json"
            else None
        )
        data = scraper.scrape_data("http://test.com")
        assert data["title"] == "t"
        assert data["price"] == "100.00"
        assert data["city"] == "city"
        assert data["state"] == "state"
        assert data["seller_name"] == "seller"
        assert data["is_available"] is True


@patch.object(OLXScraper, "scrape_data")
def test_update_data_merges_product_and_updated(scrape_data_mock, scraper):
    scrape_data_mock.return_value = {"url": "abc", "price": "200"}
    product = {"url": "https://olx.com.br/item/abc", "id": 123}
    updated = scraper.update_data(product)
    assert updated["url"] == "abc"
    assert updated["price"] == "200"
    assert updated["id"] == 123


def test_str_repr(scraper):
    assert str(scraper) == "OLX Scraper"
