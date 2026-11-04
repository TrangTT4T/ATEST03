"""Catalog page: /collections/all"""
from selenium.webdriver.common.by import By

from .base_page import BasePage


class CatalogPage(BasePage):
    path = "/collections/all"

    def tile_text(self, handle: str) -> str:
        # Each product tile is a link to /products/<handle> holding name, price and "Sold Out".
        return self.find(By.CSS_SELECTOR, f"a[href*='/products/{handle}']").text
