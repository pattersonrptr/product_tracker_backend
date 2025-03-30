import unittest
from unittest.mock import MagicMock, patch

import requests
from bs4 import BeautifulSoup

from scrapers.olx.scraper import Scraper


class TestScraper(unittest.TestCase):
    def setUp(self):
        self.scraper = Scraper(api_url="http://test-api.com")
        self.mock_html = """
        <html>
            <body>
                <section class="olx-ad-card--horizontal">
                    <a href="http://test.com/item1"></a>
                    <a href="http://test.com/item2"></a>
                </section>
            </body>
        </html>
        """
        self.mock_product_page = """
        <html>
            <body>
                <span class="olx-text--title-medium">Produto Teste</span>
                <span class="olx-text olx-text--title-large olx-text--block">R$ 1.234,56</span>
            </body>
        </html>
        """

    @patch("scrapers.olx.scraper.cloudscraper.create_scraper")
    def test_init(self, mock_scraper):
        scraper = Scraper()
        self.assertEqual(scraper.BASE_URL, "https://www.olx.com.br/brasil")
        self.assertIsNotNone(scraper.session)
        self.assertEqual(scraper.api_url, "web:8000")

        custom_scraper = Scraper(api_url="custom-api")
        self.assertEqual(custom_scraper.api_url, "custom-api")

    def test_init_without_api_url(self):
        with patch.dict("os.environ", {"API_URL": ""}):
            scraper = Scraper()
            self.assertEqual(scraper.api_url, "web:8000")

    def test_init_with_env_var(self):
        with patch.dict("os.environ", {"API_URL": "http://env-api:5000"}):
            scraper = Scraper()
            self.assertEqual(scraper.api_url, "http://env-api:5000")

    @patch("scrapers.olx.scraper.requests.Session.get")
    def test_safe_request_failure(self, mock_get):
        mock_get.side_effect = requests.exceptions.HTTPError("Server error")
        result = self.scraper._safe_request("http://error.com")
        self.assertIsNone(result)

    def test_safe_request_unknown_error(self):
        with patch("scrapers.olx.scraper.requests.Session.get") as mock_get:
            mock_get.side_effect = Exception("Erro genérico")
            result = self.scraper._safe_request("http://error.com", max_retries=1)
            self.assertIsNone(result)

    @patch("scrapers.olx.scraper.requests.Session.get")
    def test_safe_request_unexpected_error(self, mock_get):
        mock_get.side_effect = ValueError("Unexpected value error")
        result = self.scraper._safe_request("http://test.com")
        assert result is None

    @patch("scrapers.olx.scraper.requests.Session.get")
    def test_safe_request_connection_error(self, mock_get):
        mock_get.side_effect = requests.exceptions.ConnectionError("Connection failed")
        result = self.scraper._safe_request("http://test.com")
        assert result is None

    @patch("scrapers.olx.scraper.requests.Session.get")
    def test_safe_request_http_error(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        mock_get.side_effect = requests.exceptions.HTTPError(response=mock_response)
        result = self.scraper._safe_request("http://test.com")
        assert result is None

    @patch("scrapers.olx.scraper.Scraper._safe_request")
    def test_scrape_search(self, mock_safe_request):
        mock_safe_request.side_effect = [self.mock_html, self.mock_html, None]

        links = self.scraper.scrape_search("teste")

        self.assertEqual(len(links), 4)
        self.assertIn("http://test.com/item1", links)
        self.assertIn("http://test.com/item2", links)
        self.assertEqual(mock_safe_request.call_count, 3)

    @patch("scrapers.olx.scraper.Scraper._safe_request")
    def test_scrape_search_exception(self, mock_safe_request):
        mock_safe_request.side_effect = Exception("Test error")
        links = self.scraper.scrape_search("test")
        assert links == []
        assert mock_safe_request.called

    @patch("scrapers.olx.scraper.Scraper._safe_request")
    @patch("scrapers.olx.scraper.Scraper._extract_links")
    def test_scrape_search_empty_links(self, mock_extract_links, mock_safe_request):
        mock_safe_request.return_value = "<html></html>"
        mock_extract_links.return_value = []
        links = self.scraper.scrape_search("teste")

        self.assertEqual(links, [])
        mock_safe_request.assert_called_once()
        mock_extract_links.assert_called_once()

    @patch("scrapers.olx.scraper.Scraper._safe_request")
    def test_scrape_product_page(self, mock_safe_request):
        mock_safe_request.return_value = self.mock_product_page

        result = self.scraper.scrape_product_page("http://test.com/product")

        self.assertEqual(result["url"], "http://test.com/product")
        self.assertEqual(result["title"], "Produto Teste")
        self.assertEqual(result["price"], "1.234,56")

    @patch("scrapers.olx.scraper.Scraper._safe_request")
    def test_update_product(self, mock_safe_request):
        mock_safe_request.return_value = self.mock_product_page
        product = {
            "id": 123,
            "url": "http://test.com/product",
            "title": "Old Title",
            "price": "Old Price",
        }

        updated = self.scraper.update_product(product)

        self.assertEqual(updated["id"], 123)
        self.assertEqual(updated["title"], "Produto Teste")
        self.assertEqual(updated["price"], "1.234,56")

    def test_build_search_url(self):
        url = self.scraper._build_search_url("cadeira gamer")
        self.assertEqual(url, "https://www.olx.com.br/brasil?q=cadeira+gamer&o=1")

        url_page2 = self.scraper._build_search_url("cadeira gamer", 2)
        self.assertEqual(url_page2, "https://www.olx.com.br/brasil?q=cadeira+gamer&o=2")

    @patch("scrapers.olx.scraper.requests.Session.get")
    def test_safe_request_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "<html>test</html>"
        mock_get.return_value = mock_response

        result = self.scraper._safe_request("http://test.com")
        self.assertEqual(result, "<html>test</html>")

    @patch("scrapers.olx.scraper.requests.Session.get")
    def test_safe_request_retry(self, mock_get):
        mock_get.side_effect = [
            requests.exceptions.ConnectionError("Error 1"),
            requests.exceptions.Timeout("Error 2"),
            MagicMock(status_code=200, text="<html>success</html>"),
        ]

        result = self.scraper._safe_request("http://test.com")
        self.assertEqual(result, "<html>success</html>")
        self.assertEqual(mock_get.call_count, 3)

    def test_extract_links(self):
        links = self.scraper._extract_links(self.mock_html)

        self.assertEqual(len(links), 2)
        self.assertIn("http://test.com/item1", links)
        self.assertIn("http://test.com/item2", links)

    def test_extract_title(self):
        soup = BeautifulSoup(self.mock_product_page, "html.parser")
        title = self.scraper._extract_title(soup)
        self.assertEqual(title, "Produto Teste")

    def test_extract_title_not_found(self):
        soup = BeautifulSoup("<html></html>", "html.parser")
        title = self.scraper._extract_title(soup)
        self.assertEqual(title, "Title not found")

    def test_extract_price(self):
        soup = BeautifulSoup(self.mock_product_page, "html.parser")
        price = self.scraper._extract_price(soup)
        self.assertEqual(price, "1.234,56")

    def test_extract_price_not_found(self):
        soup = BeautifulSoup("<html></html>", "html.parser")
        price = self.scraper._extract_price(soup)
        self.assertEqual(price, "Price not found")

    @patch("scrapers.olx.scraper.requests.post")
    def test_send_to_api(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_post.return_value = mock_response

        items = [
            {"title": "Item 1", "price": "100"},
            {"title": "Item 2", "price": "200"},
        ]

        self.scraper._send_to_api(items)
        self.assertEqual(mock_post.call_count, 2)

    @patch("scrapers.olx.scraper.requests.post")
    def test_send_to_api_failure(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_post.return_value = mock_response

        items = [{"title": "Item erro", "price": "100"}]
        self.scraper._send_to_api(items)

        mock_post.assert_called_once()

    def test_send_to_api_empty(self):
        with self.assertLogs(level="WARNING") as log:
            self.scraper._send_to_api([])
            self.assertIn("No items to send", log.output[0])

    @patch("scrapers.olx.scraper.requests.post")
    def test_send_to_api_partial_failure(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = "Bad request"
        mock_post.return_value = mock_response

        items = [{"title": "Item inválido", "price": "abc"}]
        with self.assertLogs(level="ERROR") as log:
            self.scraper._send_to_api(items)
            self.assertIn("Error sending Item inválido", log.output[0])

    @patch("scrapers.olx.scraper.requests.post")
    def test_send_to_api_missing_title(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = "Bad request"
        mock_post.return_value = mock_response

        items = [{"price": "100"}]

        with self.assertLogs(level="ERROR") as log:
            self.scraper._send_to_api(items)

            self.assertIn(
                "Error sending Unknown Item: 400 - Bad request", log.output[0]
            )

        mock_post.assert_called_once_with(
            f"{self.scraper.api_url}/products/", json={"price": "100"}, timeout=10
        )

    @patch("scrapers.olx.scraper.requests.post")
    def test_send_to_api_exception(self, mock_post):
        mock_post.side_effect = Exception("Connection error")
        with self.assertLogs(level="ERROR") as log:
            self.scraper._send_to_api([{"title": "Test", "price": "100"}])
            self.assertIn("Send failure: Connection error", log.output[0])

    def test_init_with_empty_env_var(self):
        with patch.dict("os.environ", {"API_URL": ""}):
            scraper = Scraper()
            assert scraper.api_url == "web:8000"

    @patch("scrapers.olx.scraper.requests.Session.get")
    def test_safe_request_ssl_error(self, mock_get):
        mock_get.side_effect = requests.exceptions.SSLError("SSL Error")
        result = self.scraper._safe_request("https://error.com", max_retries=1)
        assert result is None

    @patch("scrapers.olx.scraper.requests.post")
    def test_send_to_api_missing_title_log(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = "Missing title"
        mock_post.return_value = mock_response

        with self.assertLogs(level="ERROR") as log:
            self.scraper._send_to_api([{"price": "100"}])
            self.assertIn("Unknown Item", log.output[0])
