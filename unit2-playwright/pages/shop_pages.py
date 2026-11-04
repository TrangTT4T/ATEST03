"""Page Objects for Sauce Demo: catalog, product, cart, checkout, login, search."""
import re

from playwright.sync_api import Locator

from .base_page import BasePage, money_to_float

TOTAL = re.compile(r"(sub)?total[^£]{0,40}£\s?([\d,]+\.\d{2})", re.IGNORECASE)


class CatalogPage(BasePage):
    path = "/collections/all"

    def tile(self, handle: str) -> Locator:
        # Each product tile is a link to /products/<handle> holding name, price and "Sold Out".
        return self.page.locator(f"a[href*='/products/{handle}']").first


class ProductPage(BasePage):
    def open_product(self, handle: str):
        return self.open(f"/products/{handle}")

    @property
    def title(self) -> Locator:
        return self.page.get_by_role("heading", level=1).first

    @property
    def add_form(self) -> Locator:
        return self.page.locator("form[action*='/cart/add']").first   # standard Shopify form

    @property
    def add_button(self) -> Locator:
        return self.add_form.locator("[type='submit']").first

    def can_add_to_cart(self) -> bool:
        if self.add_button.count() == 0 or self.add_button.is_disabled():
            return False
        label = (self.add_button.get_attribute("value") or self.add_button.inner_text() or "").lower()
        return "sold out" not in label and "unavailable" not in label

    def add_to_cart(self, quantity: int = 1):
        qty = self.add_form.locator("input[name='quantity']")
        if qty.count():
            qty.fill(str(quantity))
            self._submit()
        else:  # theme without a quantity box: add the product N times
            url = self.page.url
            for i in range(quantity):
                if i:
                    self.page.goto(url)
                self._submit()

    def _submit(self):
        # Wait on the network call itself, not on a timer (Day 6: network-aware waits).
        with self.page.expect_response(lambda r: "/cart/add" in r.url):
            self.submit(self.add_button)
        self.page.wait_for_url(re.compile(r"/cart"))


class CartPage(BasePage):
    path = "/cart"

    @property
    def quantity_inputs(self) -> Locator:
        return self.page.locator("input[name^='updates']")

    def total_quantity(self) -> int:
        inputs = self.quantity_inputs
        return sum(int(inputs.nth(i).input_value() or 0) for i in range(inputs.count()))

    def line_input(self, product_name: str) -> Locator:
        row = (self.page.locator("tr, li, div")
               .filter(has=self.page.get_by_role("link", name=product_name, exact=True))
               .filter(has=self.quantity_inputs).last)
        return row.locator("input[name^='updates']").first

    def set_quantity(self, product_name: str, quantity: int):
        # Quantity 0 + Update removes the line (standard Shopify behaviour).
        self.line_input(product_name).fill(str(quantity))
        self.submit(self.page.locator("[name='update']").first)

    def remove(self, product_name: str):
        self.set_quantity(product_name, 0)

    def total(self) -> float:
        match = TOTAL.search(self.page.locator("body").inner_text())
        if match:
            return float(match.group(2).replace(",", ""))
        form = self.page.locator("form[action*='/cart']").first
        return money_to_float(re.findall(r"£\s?[\d,]+\.\d{2}", form.inner_text())[-1])

    def checkout(self):
        self.submit(self.page.locator("[name='checkout']").first)
        self.page.wait_for_url(re.compile(r"checkout"))


class LoginPage(BasePage):
    path = "/account/login"

    @property
    def form(self) -> Locator:
        return self.page.locator("form[action*='/account/login']").first

    def login(self, email: str, password: str):
        self.form.locator("input[name='customer[email]']").fill(email)
        self.form.locator("input[name='customer[password]']").fill(password)
        self.submit(self.form.locator("[type='submit']").first)

    @property
    def error(self) -> Locator:
        return self.page.locator(".errors, .form-error, [role='alert']").first

    def open_password_reset(self):
        self.page.get_by_role("link", name="Forgot your password?").click()

    @property
    def reset_form(self) -> Locator:
        return self.page.locator("form[action*='/account/recover']").first


class RegisterPage(BasePage):
    path = "/account/register"

    @property
    def form(self) -> Locator:
        return self.page.locator("form[action*='/account']").filter(
            has=self.page.locator("input[name='customer[email]']")).first

    def register(self, first: str, last: str, email: str, password: str):
        for field, value in (("first_name", first), ("last_name", last), ("email", email), ("password", password)):
            self.form.locator(f"input[name='customer[{field}]']").fill(value)
        self.submit(self.form.locator("[type='submit']").first)

    @property
    def error(self) -> Locator:
        return self.page.locator(".errors, .form-error, [role='alert']").first


class SearchPage(BasePage):
    @property
    def result_links(self) -> Locator:
        return self.page.locator("a[href*='/products/']")
