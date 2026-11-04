"""Product detail page: /products/<handle>"""
from selenium.webdriver.common.by import By

from .base_page import BasePage

ADD_FORM = "form[action*='/cart/add']"            # standard Shopify add-to-cart form
ADD_BUTTON = ADD_FORM + " [type='submit']"


class ProductPage(BasePage):
    def open_product(self, handle: str):
        return self.open(f"/products/{handle}")

    def title(self) -> str:
        return self.find(By.TAG_NAME, "h1").text

    def can_add_to_cart(self) -> bool:
        buttons = self.find_all(By.CSS_SELECTOR, ADD_BUTTON)
        if not buttons:
            return False
        button = buttons[0]
        label = (button.get_attribute("value") or button.text or "").lower()
        return button.is_enabled() and "sold out" not in label and "unavailable" not in label

    def add_to_cart(self, quantity: int = 1):
        qty = self.find_all(By.CSS_SELECTOR, ADD_FORM + " input[name='quantity']")
        if qty:
            qty[0].clear()
            qty[0].send_keys(str(quantity))
            self._submit()
        else:
            # Theme without a quantity box: add the product N times.
            product_url = self.url
            for i in range(quantity):
                if i:
                    self.driver.get(product_url)
                self._submit()

    def _submit(self):
        # Wait for each POST to finish (redirect to /cart) before the next action;
        # without this the next driver.get() can cancel the request (found in the Unit 2 re-check).
        self.submit(By.CSS_SELECTOR, ADD_BUTTON)
        self.wait.until(lambda d: "/cart" in d.current_url and "/products/" not in d.current_url)
