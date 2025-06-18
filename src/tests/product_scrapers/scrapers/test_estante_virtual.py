import pytest
from unittest.mock import patch, MagicMock

from src.product_scrapers.scrapers.estante_virtual import EstanteVirtualScraper


@pytest.fixture
def scraper():
    return EstanteVirtualScraper()


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


@patch.object(EstanteVirtualScraper, "retry_request")
def test_search_success(mock_retry, scraper):
    mock_resp = MagicMock()
    mock_resp.json.return_value = {
        "totalPages": 2,
        "parentSkus": [
            {"productSlug": "/produto1"},
            {"productSlug": "/produto2"},
        ],
    }
    mock_retry.return_value = mock_resp

    with patch.object(
        scraper, "_get_products_list", wraps=scraper._get_products_list
    ) as mock_get_products_list:
        links = scraper.search("livro")
        assert "/produto1" in links[0]
        assert "/produto2" in links[1]
        assert mock_get_products_list.called


def test_get_products_list(scraper):
    data = {
        "parentSkus": [
            {"productSlug": "/produto1"},
            {"productSlug": "/produto2"},
        ]
    }
    urls = scraper._get_products_list(data)
    assert "produto1" in urls[0]
    assert "produto2" in urls[1]


@patch.object(EstanteVirtualScraper, "retry_request")
@patch.object(EstanteVirtualScraper, "_parse_html")
@patch.object(EstanteVirtualScraper, "_extract_initial_state")
def test_scrape_data_success(
    mock_extract_initial_state, mock_parse_html, mock_retry, scraper
):
    mock_resp = MagicMock()
    mock_resp.content = b"<html></html>"
    mock_retry.return_value = mock_resp
    mock_parse_html.return_value = MagicMock()
    mock_extract_initial_state.return_value = {
        "Product": {
            "name": "Livro",
            "author": "Autor",
            "currentProduct": {
                "price": {"saleInCents": 2500, "seller": {"name": "Vendedor"}},
                "description": "Descrição",
                "available": True,
                "images": {"details": ["/img1.jpg"]},
                "sku": "SKU123",
            },
            "grouper": {"groupProducts": {"novo": {"prices": [{"city": "Cidade"}]}}},
            "id": "ID123",
        }
    }
    data = scraper.scrape_data("https://www.estantevirtual.com.br/produto1")
    assert data["title"].startswith("Livro")
    assert data["price"] == "25.00"
    assert data["seller_name"] == "Vendedor"
    assert data["city"] == "Cidade"
    assert data["is_available"] is True
    assert data["image_urls"].endswith("img1.jpg")
    assert data["source_product_code"] == "EV - ID123"


@patch.object(EstanteVirtualScraper, "retry_request")
@patch.object(EstanteVirtualScraper, "_parse_html")
@patch.object(EstanteVirtualScraper, "_extract_initial_state")
def test_scrape_data_no_data(
    mock_extract_initial_state, mock_parse_html, mock_retry, scraper
):
    mock_resp = MagicMock()
    mock_resp.content = b"<html></html>"
    mock_retry.return_value = mock_resp
    mock_parse_html.return_value = MagicMock()
    mock_extract_initial_state.return_value = None
    data = scraper.scrape_data("https://www.estantevirtual.com.br/produto1")
    assert data == {}


def test_extract_price(scraper):
    product_info = {"currentProduct": {"price": {"saleInCents": 1234}}}
    assert scraper._extract_price(product_info) == 12.34


def test_extract_description(scraper):
    product_info = {"currentProduct": {"description": "desc"}}
    assert scraper._extract_description(product_info) == "desc"


def test_extract_seller(scraper):
    product_info = {"currentProduct": {"price": {"seller": {"name": "Vendedor"}}}}
    assert scraper._extract_seller(product_info) == "Vendedor"


def test_extract_location(scraper):
    product_info = {
        "grouper": {"groupProducts": {"novo": {"prices": [{"city": "Cidade"}]}}}
    }
    assert scraper._extract_location(product_info) == "Cidade"


def test_extract_image(scraper):
    product_info = {"currentProduct": {"images": {"details": ["/img1.jpg"]}}}
    assert scraper._extract_image(product_info).endswith("img1.jpg")


def test_extract_is_available(scraper):
    product_info = {"currentProduct": {"available": True}}
    assert scraper._extract_is_available(product_info) is True


def test_extract_source_product_code(scraper):
    product_info = {"currentProduct": {"sku": "SKU123"}}
    assert scraper._extract_source_product_code(product_info) == "EV - SKU123"


@patch.object(EstanteVirtualScraper, "scrape_data")
def test_update_data_merges_product_and_updated(scrape_data_mock, scraper):
    scrape_data_mock.return_value = {"url": "abc", "price": "200"}
    product = {"url": "https://www.estantevirtual.com.br/produto1", "id": 123}
    updated = scraper.update_data(product)
    assert updated["url"] == "abc"
    assert updated["price"] == "200"
    assert updated["id"] == 123


def test_str_repr(scraper):
    assert str(scraper) == "Estante Virtual Scraper"
