import pytest
from unittest.mock import patch, MagicMock

from src.product_scrapers.scrapers.mercado_livre import MercadoLivreScraper

@pytest.fixture
def scraper():
    return MercadoLivreScraper()

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

def test_extract_links(scraper):
    html = """
    <html>
      <a class="poly-component__title-wrapper" href="https://produto1"></a>
      <a class="poly-component__title-wrapper" href="https://produto2"></a>
      <a class="poly-component__title-wrapper" href="https://click1/ignorar"></a>
    </html>
    """
    links = scraper._extract_links(html)
    assert "https://produto1" in links
    assert "https://produto2" in links
    assert all(not l.startswith("https://click1") for l in links)

def test_get_next_url(scraper):
    url = scraper._get_next_url(20, "notebook")
    assert "notebook" in url
    assert "_Desde_21_" in url

@patch.object(MercadoLivreScraper, "retry_request")
@patch.object(MercadoLivreScraper, "_extract_links")
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

@patch.object(MercadoLivreScraper, "retry_request")
def test_search_no_results(mock_retry, scraper):
    mock_resp = MagicMock()
    mock_resp.text = ""
    mock_retry.return_value = mock_resp
    result = scraper.search("notebook")
    assert result == []

def test_extract_title(scraper):
    class Soup:
        def find(self, tag, class_=None):
            if tag == "h1" and class_ == "ui-pdp-title":
                class Title:
                    def get_text(self, strip):
                        return "Produto Teste"
                return Title()
            return None
    soup = Soup()
    assert scraper._extract_title(soup) == "Produto Teste"

def test_extract_price(scraper):
    class Soup:
        def find(self, tag, itemprop=None):
            if tag == "meta" and itemprop == "price":
                return {"content": "123.45"}
            return None
    soup = Soup()
    assert scraper._extract_price(soup) == "123.45"

def test_extract_description(scraper):
    class Soup:
        def find(self, tag, attrs=None):
            if tag == "p" and attrs and attrs.get("class") == "ui-pdp-description__content":
                class Desc:
                    def get_text(self, strip):
                        return "Descrição"
                return Desc()
            return None
    soup = Soup()
    assert scraper._extract_description(soup) == "Descrição"

def test_extract_availability(scraper):
    class StockInfo:
        def get_text(self, strip):
            return "Disponível"
    class Soup:
        def select_one(self, selector):
            if selector == ".ui-pdp-stock-information__title":
                return StockInfo()
            return None
    soup = Soup()
    assert scraper._extract_availability(soup) is True

def test_extract_product_code(scraper):
    url = "https://produto.com#wid=12345"
    assert scraper._extract_product_code(url) == "12345"

def test_extract_image_src(scraper):
    class Img:
        def has_attr(self, attr):
            return attr == "src"
        def __getitem__(self, key):
            if key == "src":
                return "img_url"
    class Soup:
        def select_one(self, selector):
            if selector == "img.ui-pdp-image.ui-pdp-gallery__figure__image":
                return Img()
            return None
    soup = Soup()
    assert scraper._extract_image_src(soup) == "img_url"

@patch.object(MercadoLivreScraper, "retry_request")
def test_scrape_data_success(mock_retry, scraper):
    html = "<html></html>"
    mock_resp = MagicMock()
    mock_resp.content = html
    mock_retry.return_value = mock_resp

    with patch("src.product_scrapers.scrapers.mercado_livre.BeautifulSoup") as bs_mock:
        soup_mock = MagicMock()
        bs_mock.return_value = soup_mock
        scraper._extract_title = MagicMock(return_value="Produto")
        scraper._extract_price = MagicMock(return_value="100.00")
        scraper._extract_description = MagicMock(return_value="desc")
        scraper._extract_product_code = MagicMock(return_value="abc")
        scraper._extract_availability = MagicMock(return_value=True)
        scraper._extract_image_src = MagicMock(return_value="img_url")
        data = scraper.scrape_data("http://test.com")
        assert data["title"] == "Produto"
        assert data["price"] == "100.00"
        assert data["is_available"] is True
        assert data["image_urls"] == "img_url"
        assert data["source_product_code"] == "ML - abc"

@patch.object(MercadoLivreScraper, "scrape_data")
def test_update_data_merges_product_and_updated(scrape_data_mock, scraper):
    scrape_data_mock.return_value = {"url": "abc", "price": "200"}
    product = {"url": "https://produto.com", "id": 123}
    updated = scraper.update_data(product)
    assert updated["url"] == "abc"
    assert updated["price"] == "200"
    assert updated["id"] == 123

def test_str_repr(scraper):
    assert str(scraper) == "Mercado Livre Scraper"
