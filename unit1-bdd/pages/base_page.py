"""Base Page Object (Selenium WebDriver): navigation, waits and shared helpers."""
import re

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

MONEY = re.compile(r"£\s?([\d,]+\.\d{2})")


def money_to_float(text: str) -> float:
    """'£1,120.00' -> 1120.0"""
    match = MONEY.search(text)
    if not match:
        raise ValueError(f"No £ amount found in: {text!r}")
    return float(match.group(1).replace(",", ""))


class BasePage:
    path = "/"

    def __init__(self, driver, base_url: str, timeout: int = 10):
        self.driver = driver
        self.base_url = base_url.rstrip("/")
        self.wait = WebDriverWait(driver, timeout)

    # Navigation ------------------------------------------------------------
    def open(self, path: str | None = None):
        self.driver.get(self.base_url + (path or self.path))
        return self

    @property
    def url(self) -> str:
        return self.driver.current_url

    # Element helpers (explicit waits, never time.sleep) ---------------------
    def find(self, by, value):
        return self.wait.until(EC.presence_of_element_located((by, value)))

    def find_all(self, by, value):
        return self.driver.find_elements(by, value)

    def click(self, by, value):
        self.wait.until(EC.element_to_be_clickable((by, value))).click()

    def submit(self, by, value):
        """Click a form button and wait until the browser has replaced the old page.

        Without this, the next driver.get() can cancel the form POST (Day 4 findings F7/F8).
        """
        old_page = self.driver.find_element(By.TAG_NAME, "html")
        self.click(by, value)
        self.wait.until(EC.staleness_of(old_page))

    def type(self, by, value, text):
        element = self.find(by, value)
        element.clear()
        element.send_keys(text)
        return element

    def body_text(self) -> str:
        return self.driver.find_element(By.TAG_NAME, "body").text

    # Header ------------------------------------------------------------------
    def mini_cart_count(self) -> int:
        link = self.find(By.XPATH, "//a[contains(., 'My Cart')]")
        return int(re.search(r"\((\d+)\)", link.text).group(1))

    def search(self, keyword: str):
        box = self.type(By.NAME, "q", keyword)
        box.send_keys(Keys.ENTER)
        self.wait.until(EC.url_contains("/search"))
