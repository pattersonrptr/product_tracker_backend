import pytest
from unittest.mock import patch, MagicMock

from src.product_scrapers.api.api_client import ApiClient


@pytest.fixture
def client():
    return ApiClient(access_token="token123")


@patch("requests.request")
def test_get_search_configs_by_id_success(mock_request, client):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"id": 1, "search_term": "notebook"}
    mock_request.return_value = mock_response

    result = client.get_search_configs_by_id(1)
    assert result["id"] == 1
    assert result["search_term"] == "notebook"


@patch("requests.request")
def test_get_search_configs_by_id_not_found(mock_request, client):
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.json.return_value = None
    mock_request.return_value = mock_response

    result = client.get_search_configs_by_id(999)
    assert result == {}


@patch("requests.request")
def test_get_source_website_by_name_found(mock_request, client):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"id": 2, "name": "OLX"}
    mock_request.return_value = mock_response

    result = client.get_source_website_by_name("OLX")
    assert result["id"] == 2


@patch("requests.request")
def test_get_source_website_by_name_not_found(mock_request, client):
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.json.return_value = None
    mock_request.return_value = mock_response

    result = client.get_source_website_by_name("Desconhecido")
    assert result == {}


@patch("requests.request")
def test_get_search_configs_by_source_website_found(mock_request, client):
    # Mock get_source_website_by_name
    with patch.object(client, "get_source_website_by_name", return_value={"id": 5}):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{"id": 1}, {"id": 2}]
        mock_request.return_value = mock_response

        result = client.get_search_configs_by_source_website("OLX")
        assert isinstance(result, list)
        assert len(result) == 2


@patch("requests.request")
def test_get_search_configs_by_source_website_not_found(mock_request, client):
    with patch.object(client, "get_source_website_by_name", return_value={}):
        result = client.get_search_configs_by_source_website("Desconhecido")
        assert result == []


@patch("requests.request")
def test_get_active_searches(mock_request, client):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = [
        {"id": 1, "is_active": True},
        {"id": 2, "is_active": False},
        {"id": 3, "is_active": True},
    ]
    mock_request.return_value = mock_response

    result = client.get_active_searches()
    assert all(item["is_active"] for item in result)
    assert len(result) == 2


@patch("requests.request")
def test_get_existing_product_urls(mock_request, client):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = [{"url": "http://a.com"}, {"url": "http://b.com"}]
    mock_request.return_value = mock_response

    urls = client.get_existing_product_urls("url")
    assert "http://a.com" in urls
    assert "http://b.com" in urls


@patch("requests.request")
def test_create_product_success(mock_request, client):
    mock_response = MagicMock()
    mock_response.status_code = 201
    mock_request.return_value = mock_response

    product = {"url": "http://a.com"}
    assert client.create_product(product) is True


@patch("requests.request")
def test_create_product_fail(mock_request, client):
    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_request.return_value = mock_response

    product = {"url": "http://a.com"}
    assert client.create_product(product) is False


@patch("requests.request")
def test_product_exists_true(mock_request, client):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"id": 1}
    mock_request.return_value = mock_response

    product = {"url": "http://a.com"}
    assert client.product_exists(product) is True


@patch("requests.request")
def test_product_exists_false(mock_request, client):
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.json.return_value = None
    mock_request.return_value = mock_response

    product = {"url": "http://a.com"}
    assert client.product_exists(product) is False


@patch("requests.request")
def test_create_new_products(mock_request, client):
    # Patch product_exists and create_product
    with patch.object(client, "product_exists", return_value=False), patch.object(
        client, "create_product", return_value=True
    ):
        products = [{"url": "a"}, {"url": "b"}]
        created = client.create_new_products(products)
        assert created == 2


@patch("requests.request")
def test_get_products(mock_request, client):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = [{"id": 1}, {"id": 2}]
    mock_request.return_value = mock_response

    result = client.get_products()
    assert isinstance(result, list)
    assert len(result) == 2


@patch("requests.request")
def test_update_product_list(mock_request, client):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_request.return_value = mock_response

    products = [{"id": 1}, {"id": 2}]
    updated = client.update_product_list(products)
    assert updated == 2


@patch("requests.request")
def test_make_request_exception(mock_request, client):
    mock_request.side_effect = Exception("fail")
    resp = client._make_request("GET", "/fail")
    from requests import Response

    assert isinstance(resp, Response)
