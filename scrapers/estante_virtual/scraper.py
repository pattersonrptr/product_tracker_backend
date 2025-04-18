import cloudscraper

from scrapers.base.scraper import Scraper


class Scraper(Scraper):
    def __init__(self, api_url=None):
        self.BASE_URL = "https://www.estantevirtual.com.br"
        self.session = cloudscraper.create_scraper()

    def search(self, search_term: str) -> list[str]:
        cookies = {
            "uuid": "19a804b1-521e-4f8c-af59-de098361fe51",
            "__uzma": "6b9119ba-dcac-4abd-a649-88d6adb7c8d1",
            "__uzmb": "1740803766",
            "__uzme": "3979",
            "__uzmc": "311711669662",
            "__uzmd": "1742179725",
            "g_state": '{"i_l":0}',
            "email": "pattersonjunior%40gmail.com",
            "uname": "PATTERSON",
            "customerServiceUuid": "19a804b1-521e-4f8c-af59-de098361fe51",
            "customerServiceUname": "PATTERSON",
            "croct.cid": "73cf1701-2632-4170-bbc3-2820d538179b",
            "zipcode": "12950391",
            "cityCode": "3504107",
            "uf": "SP",
            "az_asm_20241212": "96PsaP01l/v2aPhA3cDPYY4sTvDXvTnb3NzMNg5+qt22hUXkdkEbVfRDcmiTtVpdZaNGWN1nLqf34BGk",
            "az_botm_20241212": "7aab3faf27c85372487e7c80bcaeb1d1",
            "campaignCode": "ev",
            "tid": "bc2854ff-4141-4b4d-bdd3-29b3c8e5b911",
            "SmartHint-Session": "cf1178e0-8976-4121-a291-51e9b75f4a8f",
        }

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:136.0) Gecko/20100101 Firefox/136.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "pt-BR,en-US;q=0.8,en;q=0.6,fr;q=0.4,pt;q=0.2",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Sec-GPC": "1",
            "Priority": "u=0, i",
        }

        params = {
            "q": search_term,
            "searchField": "titulo-autor",
            # 'tipo-de-livro': 'usado',
        }

        return self.session.get(
            f"{self.BASE_URL}/busca/api",
            params=params,
            cookies=cookies,
            headers=headers,
        )

    def _get_products_list(self, data: dict) -> list:
        return [
            {
                "url": f"{'https://www.estantevirtual.com.br'}{item['productSlug']}",
                "title": item.get("name"),
                "price": str(item.get("salePrice") / 100).replace(".", ","),
            }
            for item in data["parentSkus"]
        ]

    def scrape_data(self, url: str) -> dict: ...

    def update_data(self, product: dict) -> dict:
        # https://www.estantevirtual.com.br/busca/api?q=Python%20e%20Django&searchField=titulo-autor&tipo-de-livro=usado
        # https://www.estantevirtual.com.br/busca/api?q=python&searchField=titulo-autor&page=2&tipo-de-livro=usado
        # https://www.estantevirtual.com.br/pdp-api/api/searchProducts/0GU-8162-000-BK/usado?pageSize=100&page=1&sort=lowest-first
        # https://www.estantevirtual.com.br/pdp-api/api/searchProducts/14B-6094-000-BK/novo?pageSize=10&page=1&sort=lowest-first
        # https://www.estantevirtual.com.br/frdmprcsts/1NK-9561-000-01/lazy
        return {}
