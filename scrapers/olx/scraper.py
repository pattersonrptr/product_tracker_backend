import os
import time
import random
import requests

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException

from scrapers.olx.webdriver import WebDriver

class Scraper:
    def __init__(self, api_url=None):
        self.driver = WebDriver().get_driver()
        self.api_url = api_url or os.getenv("API_URL", "http://web:8000")

    def run(self):
        try:
            self.search_screen()
            self.do_research("livro python")
            links = self.capture_item_links()
            items = self.get_items_data(links)

            for item in items:
                self.send_to_api(item)

        except Exception as ex:
            print(f"Erro: {ex}")
        finally:
            self.driver.quit()

    def send_to_api(self, item):
        """Envia os dados do anúncio para a API FastAPI"""
        try:
            response = requests.post(
                f"{self.api_url}/products/",
                json=item,
                timeout=10
            )
            if response.status_code == 201:
                print(f"Anúncio salvo com sucesso: {item['title']}")
            else:
                print(f"Erro ao salvar anúncio: {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"Erro na requisição: {e}")

    def close_modal_if_exists(self):
        try:
            close_modal_button = self.driver.find_element(
                By.CLASS_NAME,
                "olx-modal__close-button"
            )
            close_modal_button.click()
            print("Modal fechado.")
        except NoSuchElementException:
            print("Modal não encontrado.")

    def search_screen(self):
        self.driver.get("https://www.olx.com.br/")
        self.driver.maximize_window()
        time.sleep(random.uniform(5, 10))

        self.close_modal_if_exists()
        time.sleep(random.uniform(3, 6))

    def do_research(self, research_key):
        search_input = self.driver.find_element(
            By.CLASS_NAME, "olx-text-input__input-field"
        )
        search_input.send_keys(research_key)
        time.sleep(random.uniform(5, 10))
        search_input.send_keys(Keys.ENTER)

        time.sleep(random.uniform(5, 10))


    def capture_item_links(self):
        products_links = []
        try:
            products = self.driver.find_elements(By.CLASS_NAME, "olx-ad-card__link-wrapper")
            for product in products:
                link = product.get_attribute("href")
                if link:
                    products_links.append(link)
        except NoSuchElementException:
            print("Nenhum anúncio encontrado.")

        return products_links

    def get_items_data(self, products_links):
        items = []
        for i, link in enumerate(products_links[:1]):
            self.driver.quit()
            self.driver = WebDriver().get_driver()

            print(f"Acessando anúncio {i + 1}: {link}")

            items.append(self.get_item_data(i, link))
            time.sleep(random.uniform(5, 7))
        return items

    def get_item_data(self, item_number, link):
        self.driver.get(link)
        time.sleep(random.uniform(5, 10))
        try:
            title_element = self.driver.find_element(
                By.CSS_SELECTOR,
                "h1[data-ds-component='DS-Text'].ad__sc-45jt43-0"
            )
            title = title_element.text
        except NoSuchElementException:
            title = "Título não encontrado"

        try:
            price_element = self.driver.find_element(
                By.CSS_SELECTOR,
                "h2.olx-text:nth-child(2)"
            )
            price = price_element.text.replace("R$ ", "")
        except NoSuchElementException:
            price = "Preço não encontrado"

        print("Number: ", item_number)
        print("Title: ", title)
        print("Price: ", price)

        return {
            "url": link,
            "title": title,
            "price": price,
        }
