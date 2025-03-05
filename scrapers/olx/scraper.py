import os
import time
import random
import requests
import cloudscraper
from urllib.parse import quote_plus
from bs4 import BeautifulSoup


class Scraper:
    def __init__(self, api_url=None):
        # self.session = requests.Session()
        self.session = cloudscraper.create_scraper()
        self.api_url = api_url or os.getenv("API_URL", "web:8000")
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:125.0) Gecko/20100101 Firefox/125.0',
            'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
            'DNT': '1',
            'Sec-GPC': '1',
        }
        self.timeouts = (5, 15)  # (connect, read)
        self.session.headers.update(self.headers)

    def run(self, search_term, max_items=10):
        """Executa todo o fluxo de scraping"""
        try:
            # Fase 1: Coleta de links
            search_url = self._build_search_url(search_term)
            html = self._safe_request(search_url)
            if not html:
                return

            links = self._extract_links(html)
            if not links:
                print("Nenhum anúncio encontrado.")
                return

            # Fase 2: Coleta de dados dos anúncios
            items = []
            for i, link in enumerate(links[:max_items]):
                item = self._process_product_page(link, i + 1)
                if item:
                    items.append(item)
                time.sleep(random.uniform(1, 3))  # Delay aleatório entre requisições

            # Fase 3: Envio para API
            if items:
                self._send_to_api(items)

        except Exception as e:
            print(f"Erro durante a execução: {str(e)}")

    def _build_search_url(self, search_term):
        """Constrói a URL de pesquisa formatada corretamente"""
        encoded_search = quote_plus(search_term)
        return f"https://www.olx.com.br/brasil?q={encoded_search}"

    def _safe_request(self, url, max_retries=3):
        """Faz requisições HTTP com tratamento de erros e retries"""
        for attempt in range(max_retries):
            try:
                response = self.session.get(
                    url,
                    timeout=self.timeouts,
                    allow_redirects=True
                )
                response.raise_for_status()
                return response.text

            except requests.exceptions.HTTPError as e:
                print(f"Erro HTTP {e.response.status_code} em {url}")
            except requests.exceptions.RequestException as e:
                print(f"Erro de conexão: {str(e)}")

            if attempt < max_retries - 1:
                sleep_time = random.uniform(2, 5) * (attempt + 1)
                print(f"Tentando novamente em {sleep_time:.1f} segundos...")
                time.sleep(sleep_time)

        print(f"Falha após {max_retries} tentativas para {url}")
        return None

    def _extract_links(self, html_content):
        """Extrai links dos anúncios da página de resultados"""
        soup = BeautifulSoup(html_content, 'html.parser')
        links = []

        for a in soup.find_all('a', {'class': 'olx-ad-card__link-wrapper'}):
            href = a.get('href', '').split('#')[0]  # Remove fragmentos de URL
            if href and href not in links:
                links.append(href)

        return links

    def _process_product_page(self, url, item_number):
        """Processa uma página individual de produto"""
        html = self._safe_request(url)
        if not html:
            return None

        soup = BeautifulSoup(html, 'html.parser')

        return {
            'url': url,
            'title': self._extract_title(soup),
            'price': self._extract_price(soup),
            'item_number': item_number
        }

    def _extract_title(self, soup):
        """Extrai título do anúncio"""
        try:
            return soup.find('h1', {'data-ds-component': 'DS-Text'}).get_text(strip=True)
        except AttributeError:
            return "Título não encontrado"

    def _extract_price(self, soup):
        """Extrai e formata o preço"""
        try:
            price_text = soup.select_one('h2.olx-text:nth-child(2)').get_text(strip=True)
            return price_text.replace('R$', '').strip()
        except AttributeError:
            return "Preço não encontrado"

    def _send_to_api(self, items):
        """Envia dados coletados para a API"""
        success_count = 0
        for item in items:
            try:
                response = requests.post(
                    f"{self.api_url}/products/",
                    json=item,
                    timeout=10
                )
                if response.status_code == 201:
                    success_count += 1
                else:
                    print(f"Erro ao enviar {item['title']}: {response.text}")
            except Exception as e:
                print(f"Falha no envio para API: {str(e)}")

        print(f"Envio concluído: {success_count}/{len(items)} itens salvos")

#
# if __name__ == "__main__":
#     scraper = OlxScraper()
#     scraper.run("livro python", max_items=5)