"""Base Page Object (Playwright, sync API).

Locator strategy (Day 5): role/label/text first, then stable attributes (name, form action).
No sleeps: Playwright auto-waits on actions and `expect()` retries assertions.
"""
import re

from playwright.sync_api import Locator, Page

MONEY = re.compile(r"£\s?([\d,]+\.\d{2})")


def money_to_float(text: str) -> float:
    """'£1,120.00' -> 1120.0"""
    match = MONEY.search(text)
    if not match:
        raise ValueError(f"No £ amount found in: {text!r}")
    return float(match.group(1).replace(",", ""))


class BasePage:
    path = "/"

    def __init__(self, page: Page):
        self.page = page

    def open(self, path: str | None = None):
        # Relative URL: pytest-playwright gives every context the --base-url.
        self.page.goto(path or self.path)
        return self

    def submit(self, button: Locator):
        """Click a form button and wait for the resulting navigation to finish.

        wait_for_load_state() alone returns at once (the old page is already loaded), so the next
        goto() could cancel the POST. Unit 1 hit this as findings F7/F8; both units now wait here.
        """
        with self.page.expect_navigation(wait_until="domcontentloaded"):
            button.click()

    # Header ----------------------------------------------------------------
    @property
    def mini_cart(self) -> Locator:
        return self.page.get_by_role("link", name=re.compile(r"My Cart \(\d+\)")).first

    def mini_cart_count(self) -> int:
        return int(re.search(r"\((\d+)\)", self.mini_cart.inner_text()).group(1))

    @property
    def search_box(self) -> Locator:
        return self.page.locator("input[name='q']").first

    def search(self, keyword: str):
        self.search_box.fill(keyword)
        self.search_box.press("Enter")
        self.page.wait_for_url(re.compile(r"/search"))
        return self
