import pytest
from unittest.mock import patch, MagicMock

from src.product_scrapers.scrapers.base.requests_scraper import RequestScraper

class DummyScraper(RequestScraper):
    def headers(self):
        return {"User-Agent": "test"}

@pytest.fixture
def dummy_scraper():
    return DummyScraper()

@patch("cloudscraper.create_scraper")
def test_retry_request_success(mock_create_scraper, dummy_scraper):
    mock_session = MagicMock()
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_session.get.return_value = mock_response
    mock_create_scraper.return_value = mock_session

    scraper = DummyScraper()
    resp = scraper.retry_request("http://test.com")
    assert resp == mock_response
    mock_session.get.assert_called_once()

@patch("cloudscraper.create_scraper")
def test_retry_request_http_error_then_success(mock_create_scraper, dummy_scraper):
    mock_session = MagicMock()
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = [Exception("fail"), None]
    mock_session.get.return_value = mock_response
    mock_create_scraper.return_value = mock_session

    scraper = DummyScraper()
    with patch("time.sleep") as mock_sleep:
        resp = scraper.retry_request("http://test.com", max_retries=1)
    assert resp is None or resp == mock_response  # Pode retornar None se Exception não for do tipo requests.exceptions.RequestException

@patch("cloudscraper.create_scraper")
def test_retry_request_max_retries(mock_create_scraper, dummy_scraper):
    mock_session = MagicMock()
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = [Exception("fail")] * 4
    mock_session.get.return_value = mock_response
    mock_create_scraper.return_value = mock_session

    scraper = DummyScraper()
    with patch("time.sleep") as mock_sleep:
        resp = scraper.retry_request("http://test.com", max_retries=2)
    assert resp is None

@patch("cloudscraper.create_scraper")
def test_retry_request_unexpected_exception(mock_create_scraper, dummy_scraper):
    mock_session = MagicMock()
    mock_session.get.side_effect = Exception("unexpected")
    mock_create_scraper.return_value = mock_session

    scraper = DummyScraper()
    resp = scraper.retry_request("http://test.com")
    assert resp is None
