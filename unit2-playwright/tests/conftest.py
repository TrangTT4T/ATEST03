"""Shared fixtures and hooks for the Playwright suite (Unit 2).

Inherited from Unit 1: feature files, shared/ test data, risk + requirement tags, Page Object pattern,
one fresh browser state per scenario, screenshot on failure, traceability matrix.
New in Unit 2: pytest fixtures instead of behave hooks, network control, tracing, auth state, xdist.

Fixture map (Day 5-6):
  browser (session) -> context (one per test: isolation) -> page (one per test)
  products           test data from test_data/products.json
  block_third_party  autouse network control: only the store and Shopify hosts are reached
  shop               Page Objects bound to this test's page
  cart_with          factory fixture: put N of a product in the cart
  customer_state     login once, reuse the saved storage state (auth)
"""
import json
import os
import re
from collections import defaultdict
from pathlib import Path
from types import SimpleNamespace
from urllib.parse import urlparse

import pytest
from playwright.sync_api import Browser, BrowserContext, Page

from pages import BasePage, CartPage, CatalogPage, LoginPage, ProductPage, RegisterPage, SearchPage

pytest_plugins = ["step_defs.shop_steps"]  # Gherkin step definitions (pytest-bdd)

ROOT = Path(__file__).resolve().parent.parent
SHARED = ROOT / "shared"  # same files as the Unit 1 repo
AUTH_FILE = ROOT / ".auth" / "customer.json"
SHOPIFY_SUFFIXES = (".shopify.com", ".myshopify.com", ".shopifycdn.com", ".shopifycloud.com", ".shopifysvc.com")


# --- data ---------------------------------------------------------------------
@pytest.fixture(scope="session")
def products() -> dict:
    with open(SHARED / "products.json", encoding="utf-8") as fh:
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

    Removes the main source of flakiness that the store does not own (risk R09).
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


# --- traceability report (requirement -> tests -> result) ------------------------
_TRACE: dict[str, dict] = {}


def pytest_collection_modifyitems(items):
    # user_properties travel with every report, so this also works under pytest-xdist (-n).
    # Gherkin tags arrive as markers named "REQ-01", "R01"; plain tests use req("..") / risk("..").
    for item in items:
        names = [m.name for m in item.iter_markers()]
        reqs = sorted({n for n in names if re.fullmatch(r"REQ-\d+", n)} | {m.args[0] for m in item.iter_markers("req")})
        risks = sorted({n for n in names if re.fullmatch(r"R\d+", n)} | {m.args[0] for m in item.iter_markers("risk")})
        item.user_properties.append(("reqs", reqs or ["(none)"]))
        item.user_properties.append(("risks", risks))


def pytest_runtest_logreport(report):
    props = dict(report.user_properties)
    entry = _TRACE.setdefault(report.nodeid, {"reqs": props.get("reqs", ["(none)"]),
                                              "risks": props.get("risks", []), "outcome": "not run"})
    if report.when == "call" or report.outcome in ("failed", "skipped"):
        if entry["outcome"] in ("not run", "passed"):
            entry["outcome"] = report.outcome


def pytest_sessionfinish(session):
    if hasattr(session.config, "workerinput"):  # xdist worker: the controller writes the report
        return
    by_req = defaultdict(list)
    for nodeid, entry in _TRACE.items():
        for req in entry["reqs"]:
            by_req[req].append((nodeid, ",".join(entry["risks"]), entry["outcome"]))
    catalogue = json.loads((SHARED / "requirements.json").read_text(encoding="utf-8"))["requirements"]
    lines = ["# Traceability matrix (Unit 2)", "", "| REQ | Requirement | Risk | Test | Result |",
             "| --- | --- | --- | --- | --- |"]
    for req in sorted(set(by_req) | set(catalogue)):
        title = catalogue.get(req, {}).get("title", "(not in shared/requirements.json)")
        if req not in by_req:
            lines.append(f"| {req} | {title} | {catalogue[req]['risk']} | **no test ran in this session** | - |")
        for nodeid, risks, outcome in sorted(by_req.get(req, [])):
            name = nodeid.split("::", 1)[-1].encode("ascii", "backslashreplace").decode("unicode_escape")
            lines.append(f"| {req} | {title} | {risks} | `{name}` | {outcome} |")
    covered = len(set(by_req) & set(catalogue))
    lines += ["", f"Requirement coverage: {covered}/{len(catalogue)}."]
    out = ROOT / "reports" / "traceability.md"
    out.parent.mkdir(exist_ok=True)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
