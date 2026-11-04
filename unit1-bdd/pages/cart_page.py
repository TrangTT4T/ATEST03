"""Cart page: /cart"""
import re

from selenium.webdriver.common.by import By

from .base_page import BasePage, money_to_float

QTY_INPUTS = "input[name^='updates']"
TOTAL = re.compile(r"(sub)?total[^£]{0,40}£\s?([\d,]+\.\d{2})", re.IGNORECASE)


class CartPage(BasePage):
    path = "/cart"

    def quantity_inputs(self):
        return self.find_all(By.CSS_SELECTOR, QTY_INPUTS)

    def total_quantity(self) -> int:
        return sum(int(i.get_attribute("value") or 0) for i in self.quantity_inputs())

    def is_empty(self) -> bool:
        return not self.quantity_inputs()

    def line_input(self, product_name: str):
        # The quantity box in the same cart row as the product link.
        xpath = (f"//a[normalize-space()='{product_name}']"
                 f"/ancestor::*[.//input[starts-with(@name,'updates')]][1]"
                 f"//input[starts-with(@name,'updates')]")
        return self.find(By.XPATH, xpath)

    def set_quantity(self, product_name: str, quantity: int):
        # Setting a line to 0 and updating removes it (standard Shopify behaviour).
        box = self.line_input(product_name)
        box.clear()
        box.send_keys(str(quantity))
        self.submit(By.CSS_SELECTOR, "[name='update']")

    def remove(self, product_name: str):
        self.set_quantity(product_name, 0)

    def total(self) -> float:
        match = TOTAL.search(self.body_text())
        if match:
            return float(match.group(2).replace(",", ""))
        form = self.find(By.CSS_SELECTOR, "form[action*='/cart']")
        amounts = re.findall(r"£\s?[\d,]+\.\d{2}", form.text)
        return money_to_float(amounts[-1])

    def checkout(self):
        self.submit(By.CSS_SELECTOR, "[name='checkout']")
