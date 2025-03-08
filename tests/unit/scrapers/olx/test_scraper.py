import os
import pytest
from unittest.mock import Mock, patch, call
import requests
from bs4 import BeautifulSoup
from scrapers.olx.scraper import Scraper

@pytest.fixture
def scraper():
    return Scraper(api_url="http://mockapi:8000")

@pytest.fixture
def mock_search_html():
    """Carrega o HTML da página de busca da fixture"""
    fixtures_dir = os.path.join(os.path.dirname(__file__), 'fixtures')
    with open(os.path.join(fixtures_dir, 'search_page.html'), 'r') as f:
        return f.read()

@pytest.fixture
def mock_product_html():
    """Carrega o HTML da página de produto da fixture"""
    fixtures_dir = os.path.join(os.path.dirname(__file__), 'fixtures')
    with open(os.path.join(fixtures_dir, 'product_page.html'), 'r') as f:
        return f.read()

class TestScraper:
    @pytest.mark.parametrize("fixture_name,expected_title", [
        ("product_page.html", "Black Hat Python - 2ª Edição"),  # Caso válido
        (None, "Título não encontrado")          # Caso inválido (sem HTML)
    ])
    def test_extract_title_with_fixtures(self, scraper, fixture_name, expected_title):
        # Configuração
        if fixture_name:
            fixtures_dir = os.path.join(os.path.dirname(__file__), 'fixtures')
            with open(os.path.join(fixtures_dir, fixture_name), 'r') as f:
                html = f.read()
        else:
            html = "<html></html>"  # HTML vazio para o caso inválido

        # Execução
        soup = BeautifulSoup(html, 'html.parser')
        result = scraper._extract_title(soup)

        # Verificação
        assert result == expected_title

    # Mantenha os outros testes existentes...
    def test_build_search_url(self, scraper):
        assert scraper._build_search_url("iphone 12") == "https://www.olx.com.br/brasil?q=iphone+12"


    def test_extract_links(self, scraper, mock_search_html):
        soup = BeautifulSoup(mock_search_html, 'html.parser')
        links = scraper._extract_links(mock_search_html)

        assert len(links) == 50
        assert ("https://sp.olx.com.br/grande-campinas/livros-e-revistas/"
                "livro-beyond-the-basic-stuff-with-python-best-practices-for-writing-clean-code-1313709930") in links
        assert ("https://sp.olx.com.br/sao-paulo-e-regiao/livros-e-revistas/"
                "livro-python-3-conceitos-e-aplicacoes-uma-abordagem-didatica-1375766826") in links  # Deve remover o #extra
        assert ("https://pb.olx.com.br/paraiba/livros-e-revistas/"
                "livro-de-programacao-em-python-python-direto-ao-ponto-1380006734") in links

    def test_extract_title_success(self, scraper, mock_product_html):
        soup = BeautifulSoup(mock_product_html, 'html.parser')
        title = scraper._extract_title(soup)
        assert title == "Black Hat Python - 2ª Edição"

    def test_extract_title_failure(self, scraper):
        soup = BeautifulSoup("<html></html>", 'html.parser')
        title = scraper._extract_title(soup)
        assert title == "Título não encontrado"

    def test_extract_price_success(self, scraper, mock_product_html):
        soup = BeautifulSoup(mock_product_html, 'html.parser')
        price = scraper._extract_price(soup)
        assert price == "80"

    def test_extract_price_failure(self, scraper):
        soup = BeautifulSoup("<html></html>", 'html.parser')
        price = scraper._extract_price(soup)
        assert price == "Preço não encontrado"

    @patch('scrapers.olx.scraper.requests.post')
    def test_send_to_api_success(self, mock_post, scraper):
        mock_response = Mock()
        mock_response.status_code = 201
        mock_post.return_value = mock_response

        items = [{'title': 'Teste 1'}, {'title': 'Teste 2'}]
        scraper._send_to_api(items)

        assert mock_post.call_count == 2
        assert mock_post.call_args[1]['timeout'] == 10

    @patch('scrapers.olx.scraper.time.sleep')
    @patch('scrapers.olx.scraper.random.uniform')
    def test_safe_request_retries(self, mock_uniform, mock_sleep, scraper):
        # Configura os mocks para retornar valores que serão multiplicados por (attempt + 1)
        mock_uniform.side_effect = [2.5, 2.0]  # Primeira retentativa: 2.5*1=2.5s, Segunda: 2.0*2=4.0s
        mock_get = Mock()
        mock_get.side_effect = requests.exceptions.ConnectionError()
        scraper.session.get = mock_get

        result = scraper._safe_request("http://invalid.url")

        # Verificações
        assert mock_get.call_count == 3
        assert mock_sleep.call_count == 2
        mock_sleep.assert_has_calls([
            call(2.5),  # Primeira retentativa: 2.5 * 1
            call(4.0)  # Segunda retentativa: 2.0 * 2
        ])
        assert result is None

    @patch('scrapers.olx.scraper.Scraper._safe_request')
    def test_process_product_page(self, mock_safe_request, scraper, mock_product_html):
        mock_safe_request.return_value = mock_product_html
        result = scraper._process_product_page("http://dummy.url", 1)

        assert result == {
            'url': 'http://dummy.url',
            'title': 'Black Hat Python - 2ª Edição',
            'price': '80',
            'item_number': 1
        }

    @patch('scrapers.olx.scraper.Scraper._send_to_api')
    @patch('scrapers.olx.scraper.Scraper._process_product_page')
    @patch('scrapers.olx.scraper.Scraper._extract_links')
    @patch('scrapers.olx.scraper.Scraper._safe_request')
    def test_full_flow(self, mock_safe_request, mock_extract_links,
                       mock_process, mock_send, scraper):
        # Configura os mocks
        mock_safe_request.return_value = "<html>dummy</html>"
        mock_extract_links.return_value = ["link1", "link2", "link3"]
        mock_process.side_effect = [
            {'title': 'Item 1'},
            {'title': 'Item 2'},
            None  # Simula falha no terceiro item
        ]

        scraper.run("teste", max_items=2)

        # Verifica o fluxo completo
        assert mock_safe_request.call_count == 1
        assert mock_extract_links.call_count == 1
        assert mock_process.call_count == 2  # Deve parar no max_items
        mock_send.assert_called_once_with([{'title': 'Item 1'}, {'title': 'Item 2'}])