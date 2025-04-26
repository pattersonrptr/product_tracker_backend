import unittest
import requests

from unittest.mock import MagicMock, patch
from product_scrapers.enjoei.scraper import Scraper


class TestScraper(unittest.TestCase):
    def setUp(self):
        self.scraper = Scraper(api_url="http://test-api.com")
        self.mock_response = MagicMock(spec=requests.Response)
        self.mock_response.status_code = 200
        self.mock_response.json.return_value = {"data": "mock_data"}

    @patch("product_scrapers.enjoei.scraper.cloudscraper.create_scraper")
    def test_init(self, mock_scraper):
        scraper = Scraper()
        self.assertEqual(scraper.BASE_URL, "https://enjusearch.enjoei.com.br")
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

    @patch("product_scrapers.enjoei.scraper.cloudscraper.create_scraper")
    def test_init_headers_and_timeouts(self, mock_create_scraper):
        mock_session = MagicMock()
        mock_create_scraper.return_value = mock_session

        scraper = Scraper()

        self.assertEqual(
            scraper.headers["User-Agent"],
            "Mozilla/5.0 (X11; Linux x86_64; rv:125.0) Gecko/20100101 Firefox/125.0",
        )
        self.assertEqual(scraper.timeouts, (5, 15))

        mock_session.headers.update.assert_called_once_with(scraper.headers)

    @patch("product_scrapers.enjoei.scraper.cloudscraper.create_scraper")
    def test_search_basic(self, mock_create_scraper):
        mock_session = MagicMock()
        mock_create_scraper.return_value = mock_session
        mock_session.get.return_value = self.mock_response

        scraper = Scraper()
        term = "test_product"
        response = scraper.search(term)

        mock_session.get.assert_called_once_with(
            f"{scraper.BASE_URL}/graphql-search-x",
            headers=scraper.headers,
            params={
                "browser_id": "07176e90-ef8c-4a5a-976b-b68d3a42fdeb-1742160795598",
                "city": "atibaia",
                "first": "30",
                "new_buyer": "false",
                "operation_name": "searchProducts",
                "query_id": "7d3ea67171219db36dfcf404acab5807",
                "search_context": "products_search",
                "search_id": "d89a6bf8-7b44-4e94-a4ff-2dd8e70930f4-1743294487254",
                "shipping_range": "near_regions",
                "state": "sp",
                "term": term,
                "user_id": "34906900",
            },
        )

        self.assertEqual(response, self.mock_response)

    @patch("product_scrapers.enjoei.scraper.cloudscraper.create_scraper")
    def test_search_with_after_param(self, mock_create_scraper):
        mock_session = MagicMock()
        mock_create_scraper.return_value = mock_session
        mock_session.get.return_value = self.mock_response

        scraper = Scraper()
        term = "test_product"
        after = "cursor123"
        response = scraper.search(term, after=after)

        mock_session.get.assert_called_once_with(
            f"{scraper.BASE_URL}/graphql-search-x",
            headers=scraper.headers,
            params={
                "browser_id": "07176e90-ef8c-4a5a-976b-b68d3a42fdeb-1742160795598",
                "city": "atibaia",
                "first": "30",
                "new_buyer": "false",
                "operation_name": "searchProducts",
                "query_id": "7d3ea67171219db36dfcf404acab5807",
                "search_context": "products_search",
                "search_id": "d89a6bf8-7b44-4e94-a4ff-2dd8e70930f4-1743294487254",
                "shipping_range": "near_regions",
                "state": "sp",
                "term": term,
                "user_id": "34906900",
                "after": after,
            },
        )

    @patch("product_scrapers.enjoei.scraper.cloudscraper.create_scraper")
    def test_search_connection_error(self, mock_create_scraper):
        mock_session = MagicMock()
        mock_create_scraper.return_value = mock_session
        mock_session.get.side_effect = requests.exceptions.ConnectionError(
            "Connection failed"
        )

        scraper = Scraper()

        with self.assertRaises(requests.exceptions.ConnectionError):
            scraper.search("test_product")

    def test_extract_links_with_multiple_edges(self):
        mock_data = {
            "data": {
                "search": {
                    "products": {
                        "edges": [
                            {"node": {"id": "123"}, "cursor": "cursor1"},
                            {"node": {"id": "456"}, "cursor": "cursor2"},
                        ]
                    }
                }
            }
        }

        urls, cursor = self.scraper.extract_links(mock_data)

        expected_urls = [
            "https://pages.enjoei.com.br/products/123/v2.json",
            "https://pages.enjoei.com.br/products/456/v2.json",
        ]

        self.assertEqual(urls, expected_urls)
        self.assertEqual(cursor, "cursor2")

    def test_extract_links_with_empty_edges(self):
        mock_data = {"data": {"search": {"products": {"edges": []}}}}

        urls, cursor = self.scraper.extract_links(mock_data)

        self.assertEqual(urls, [])
        self.assertIsNone(cursor)

    def test_extract_links_with_malformed_data(self):
        malformed_data = {"invalid": "data"}

        urls, cursor = self.scraper.extract_links(malformed_data)

        self.assertEqual(urls, [])
        self.assertIsNone(cursor)

    def test_extract_links_with_partial_data(self):
        partial_data = {"data": {"search": {"wrong_structure": {}}}}

        urls, cursor = self.scraper.extract_links(partial_data)

        self.assertEqual(urls, [])
        self.assertIsNone(cursor)

    @patch("product_scrapers.enjoei.scraper.cloudscraper.create_scraper")
    def test_get_product_data(self, mock_create_scraper):
        mock_session = MagicMock()
        mock_create_scraper.return_value = mock_session
        mock_session.get.return_value = self.mock_response

        scraper = Scraper()
        test_url = "https://exemplo.com/produto"
        response = scraper.get_product_data(test_url)

        mock_session.get.assert_called_once_with(test_url, headers=scraper.headers)

    def test_extract_links_exception_handling(self):
        invalid_data = {
            "data": {"search": {"products": {"edges": [{"no_node_key": "invalid"}]}}}
        }

        urls, cursor = self.scraper.extract_links(invalid_data)
        self.assertEqual(urls, [])
        self.assertIsNone(cursor)
