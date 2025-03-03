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
            self.searchScreen()
            self.doResearch("livro python")
            links = self.captureItemLinks()
            items = self.getItemsData(links)

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
                f"{self.api_url}/ads/",
                json=item,
                timeout=10
            )
            if response.status_code == 201:
                print(f"Anúncio salvo com sucesso: {item['title']}")
            else:
                print(f"Erro ao salvar anúncio: {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"Erro na requisição: {e}")

    def closeModalIfExists(self):
        try:
            close_modal_button = self.driver.find_element(
                By.CLASS_NAME,
                "olx-modal__close-button"
            )
            close_modal_button.click()
            print("Modal fechado.")
        except NoSuchElementException:
            print("Modal não encontrado.")

    def searchScreen(self):
        self.driver.get("https://www.olx.com.br/")
        self.driver.maximize_window()
        time.sleep(random.uniform(5, 10))

        self.closeModalIfExists()
        time.sleep(random.uniform(3, 6))

    def doResearch(self, researchKey):
        search_input = self.driver.find_element(
            By.CLASS_NAME, "olx-text-input__input-field"
        )
        search_input.send_keys(researchKey)
        time.sleep(random.uniform(5, 10))
        search_input.send_keys(Keys.ENTER)

        time.sleep(random.uniform(5, 10))


    def captureItemLinks(self):
        ad_links = []
        try:
            ads = self.driver.find_elements(By.CLASS_NAME, "olx-ad-card__link-wrapper")
            for ad in ads:
                link = ad.get_attribute("href")
                if link:
                    ad_links.append(link)
        except NoSuchElementException:
            print("Nenhum anúncio encontrado.")

        return ad_links

    def getItemsData(self, ad_links):
        items = []
        for i, link in enumerate(ad_links[:1]):
            self.driver.quit()
            self.driver = WebDriver().get_driver()

            print(f"Acessando anúncio {i + 1}: {link}")

            items.append(self.getItemData(i, link))
            time.sleep(random.uniform(5, 7))
        return items

    def getItemData(self, item_number, link):
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
