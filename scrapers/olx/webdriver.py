from selenium import webdriver
from selenium.webdriver.chrome.options import Options

class WebDriver:
    def __init__(self):
        self.options = None
        self.driver = None
        self.set_driver()

    def set_options(self):
        self.options = Options()
        self.options.add_argument("--headless=new")  # Nova sintaxe para Chrome >= 109
        self.options.add_argument("--no-sandbox")
        self.options.add_argument("--disable-dev-shm-usage")
        self.options.add_argument("--disable-gpu")
        self.options.add_argument("--window-size=1920,1080")
        self.options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36"
        )
        self.options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.options.add_experimental_option("useAutomationExtension", False)

    def set_driver(self):
        self.set_options()
        self.driver = webdriver.Chrome(options=self.options)

    def get_driver(self):
        return self.driver