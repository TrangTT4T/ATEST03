"""Shared fixtures and hooks for the Playwright suite (Unit 2).

Inherited from Unit 1: feature files, dataset/products.json, tags (@critical, @smoke ...), Page Object pattern,
one fresh browser state per scenario, screenshot on failure.
New in Unit 2: pytest fixtures instead of behave hooks, network control, tracing, auth state, xdist.

Fixture map (Day 5-6):
  browser (session) -> context (one per test: isolation) -> page (one per test)
  products           test data from dataset/products.json
  block_third_party  autouse network control: only the store and Shopify hosts are reached
  shop               Page Objects bound to this test's page
  cart_with          factory fixture: put N of a product in the cart
  customer_state     login once, reuse the saved storage state (auth)
"""
import json
import os
from pathlib import Path
from types import SimpleNamespace
from urllib.parse import urlparse

import pytest
from playwright.sync_api import Browser, BrowserContext, Page

from pages import BasePage, CartPage, CatalogPage, LoginPage, ProductPage, RegisterPage, SearchPage

pytest_plugins = ["steps.shop_steps"]  # Gherkin step definitions (pytest-bdd)

ROOT = Path(__file__).resolve().parent.parent
DATASET = ROOT / "dataset"  # same files as unit1-bdd/dataset
AUTH_FILE = ROOT / ".auth" / "customer.json"
SHOPIFY_SUFFIXES = (".shopify.com", ".myshopify.com", ".shopifycdn.com", ".shopifycloud.com", ".shopifysvc.com")


# --- data ---------------------------------------------------------------------
@pytest.fixture(scope="session")
def products() -> dict:
    with open(DATASET / "products.json", encoding="utf-8") as fh:
        return json.load(fh)["products"]


# --- browser context (isolation) ------------------------------------------------
@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """Every test gets a fresh context with these options: own cookies, own cart, own storage."""
    return {**browser_context_args, "viewport": {"width": 1366, "height": 900}, "locale": "en-GB"}


# --- network control (Day 6-7) --------------------------------------------------
def _is_allowed(url: str, store_host: str) -> bool:
    host = urlparse(url).hostname or ""
    if urlparse(url).scheme in ("data", "blob"):
        return True
    return host in (store_host, "localhost", "127.0.0.1") or host.endswith(SHOPIFY_SUFFIXES)


@pytest.fixture(autouse=True)
def block_third_party(request, context: BrowserContext, base_url: str):
    """Abort requests to third-party hosts (social widgets, analytics, Sauce app).

    Removes the main source of flakiness that the store does not own.
    Opt out with @pytest.mark.allow_third_party. Yields the list of blocked URLs.
    """
    blocked: list[str] = []
    if request.node.get_closest_marker("allow_third_party"):
        yield blocked
        return
    store_host = urlparse(base_url).hostname

    def handle(route):
        if _is_allowed(route.request.url, store_host):
            route.continue_()
        else:
            blocked.append(route.request.url)
            route.abort()

    context.route("**/*", handle)
    yield blocked


# --- page objects ---------------------------------------------------------------
@pytest.fixture
def shop(page: Page) -> SimpleNamespace:
    return SimpleNamespace(home=BasePage(page), catalog=CatalogPage(page), product=ProductPage(page),
                           cart=CartPage(page), login=LoginPage(page), register=RegisterPage(page),
                           search=SearchPage(page))


@pytest.fixture
def cart_with(shop, products):
    """Factory fixture: cart_with("Noir jacket", 2) puts 2 Noir jackets in this test's cart."""
    def _add(name: str, quantity: int = 1):
        shop.product.open_product(products[name]["handle"])
        shop.product.add_to_cart(quantity)
        return shop.cart.open()
    return _add


# --- authentication state (Day 6) ------------------------------------------------
@pytest.fixture(scope="session")
def customer_state(browser: Browser, base_url: str) -> Path:
    """Log in once per session and save cookies/localStorage; tests reuse the file."""
    email, password = os.getenv("SAUCE_EMAIL"), os.getenv("SAUCE_PASSWORD")
    if not (email and password):
        pytest.skip("Set SAUCE_EMAIL and SAUCE_PASSWORD to run @auth tests")
    context = browser.new_context(base_url=base_url)
    page = context.new_page()
    login = LoginPage(page).open()
    login.login(email, password)
    page.wait_for_url("**/account**")
    AUTH_FILE.parent.mkdir(exist_ok=True)
    context.storage_state(path=str(AUTH_FILE))
    context.close()
    return AUTH_FILE
