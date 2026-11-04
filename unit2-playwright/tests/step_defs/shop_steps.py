"""Step definitions for the Unit 1 feature files, implemented on Playwright (pytest-bdd).

Same sentences as the Unit 1 repo (features/steps/*.py); differences from Unit 1:
  - steps receive pytest fixtures (shop, products, page) instead of behave's `context`
  - assertions use Playwright's retrying expect() instead of explicit WebDriverWait
  - the "item"/"items" pair is one regex step from the start (Day 4 finding F1)
"""
import re
import uuid

from playwright.sync_api import expect
from pytest_bdd import given, parsers, then, when

from pages import money_to_float


# --- Given ----------------------------------------------------------------------
@given("the customer is on the home page")
def on_home(shop):
    shop.home.open()


@given(parsers.parse('the customer is viewing the product "{name}"'))
def viewing_product(shop, products, name):
    shop.product.open_product(products[name]["handle"])


@given(parsers.parse('the customer has {quantity:d} of "{name}" in the cart'))
def has_in_cart(cart_with, quantity, name):
    cart_with(name, quantity)


@given("the customer is on the login page")
def on_login(shop):
    shop.login.open()


@given("the customer is on the registration page")
def on_register(shop):
    shop.register.open()


# --- When -----------------------------------------------------------------------
@when("the customer adds the product to the cart")
def add_current(shop):
    shop.product.add_to_cart(1)


@when("the customer opens the cart")
def open_cart(shop):
    shop.cart.open()


@when(parsers.parse('the customer changes the quantity of "{name}" to {quantity:d}'))
def change_qty(shop, name, quantity):
    shop.cart.open().set_quantity(name, quantity)


@when(parsers.parse('the customer removes "{name}" from the cart'))
def remove(shop, name):
    shop.cart.open().remove(name)


@when("the customer proceeds to checkout")
def proceed_to_checkout(shop):
    shop.cart.open().checkout()


@when("the customer browses the full catalog")
def browse_catalog(shop):
    shop.catalog.open()


@when(parsers.parse('the customer logs in with email "{email}" and password "{password}"'))
def log_in(shop, email, password):
    shop.login.login(email, password)


@when("the customer chooses to reset the password")
def reset_password(shop):
    shop.login.open_password_reset()


@when("the customer registers without an email address")
def register_without_email(shop):
    shop.register.register("Test", "User", "", "Passw0rd!2026")


@when("the customer registers with a new random email")
def register_random(shop):
    shop.register.register("BDD", "Tester", f"bdd.{uuid.uuid4().hex[:10]}@example.com", "Passw0rd!2026")


@when(parsers.parse('the customer searches for "{keyword}"'))
def search(shop, keyword):
    shop.home.search(keyword)


# --- Then -----------------------------------------------------------------------
@then(parsers.re(r"the cart should contain (?P<count>\d+) items?"), converters={"count": int})
def cart_count(shop, count):
    cart = shop.cart.open()
    expect(cart.mini_cart).to_have_text(re.compile(rf"My Cart \({count}\)"))
    assert cart.total_quantity() == count


@then(parsers.parse('the cart total should be "{expected}"'))
def cart_total(shop, expected):
    assert shop.cart.open().total() == money_to_float(expected)


@then("the cart should be empty")
def cart_empty(shop):
    expect(shop.cart.open().quantity_inputs).to_have_count(0)


@then("the checkout page should be shown")
def checkout_shown(page):
    expect(page).to_have_url(re.compile(r"checkout"))


@then(parsers.parse('the checkout should list "{name}"'))
def checkout_lists(page, name):
    expect(page.get_by_text(name).first).to_be_visible()


@then(parsers.parse('the product "{name}" should be listed at its catalog price'))
def listed_price(shop, products, name):
    tile = shop.catalog.tile(products[name]["handle"])
    expect(tile).to_contain_text(name)
    expect(tile).to_contain_text(products[name]["price"])


@then(parsers.parse('the product "{name}" should be shown as "{status}"'))
def listed_status(shop, products, name, status):
    tile = shop.catalog.tile(products[name]["handle"])
    if status == "sold out":
        expect(tile).to_contain_text("Sold Out", ignore_case=True)
    else:
        expect(tile).not_to_contain_text("Sold Out", ignore_case=True)


@then(parsers.parse('the product page should show the name "{name}"'))
def detail_name(shop, name):
    expect(shop.product.title).to_have_text(name)


@then(parsers.parse('the product page should show the price "{price}"'))
def detail_price(page, price):
    expect(page.get_by_text(price).first).to_be_visible()


@then("the customer should not be able to add it to the cart")
def cannot_add(shop):
    assert not shop.product.can_add_to_cart(), "Sold-out product can still be added to the cart"


@then("a login error should be shown")
def login_error(shop):
    expect(shop.login.error).to_be_visible()


@then("the customer should not be logged in")
def not_logged_in(page):
    expect(page).not_to_have_url(re.compile(r"/account/?$"))


@then("the password reset form should be shown")
def reset_shown(shop):
    expect(shop.login.reset_form).to_be_visible()


@then("a registration error should be shown")
def register_error(shop):
    expect(shop.register.error).to_be_visible()


@then("the customer should be logged in")
def logged_in(page):
    expect(page).to_have_url(re.compile(r"/account/?$"))


@then(parsers.parse('the results should include "{name}"'))
def result_includes(shop, name):
    expect(shop.search.result_links.filter(has_text=name).first).to_be_visible()


@then("no products should be shown in the results")
def no_results(shop):
    expect(shop.search.result_links).to_have_count(0)
