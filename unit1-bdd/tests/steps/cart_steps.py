"""Cart and checkout steps (REQ-01, REQ-02, REQ-03)."""
from behave import given, then, use_step_matcher, when
from selenium.webdriver.support import expected_conditions as EC

from pages import CartPage, ProductPage, money_to_float
from helper_utility.helpers import page, product


@given('the customer has {quantity:d} of "{name}" in the cart')
def step_has_in_cart(context, quantity, name):
    product_page = page(context, ProductPage)
    product_page.open_product(product(context, name)["handle"])
    product_page.add_to_cart(quantity)


@when("the customer adds the product to the cart")
def step_add_current(context):
    page(context, ProductPage).add_to_cart(1)


@when("the customer opens the cart")
def step_open_cart(context):
    page(context, CartPage).open()


@when('the customer changes the quantity of "{name}" to {quantity:d}')
def step_change_qty(context, name, quantity):
    cart = page(context, CartPage).open()
    cart.set_quantity(name, quantity)


@when('the customer removes "{name}" from the cart')
def step_remove(context, name):
    cart = page(context, CartPage).open()
    cart.remove(name)


@when("the customer proceeds to checkout")
def step_checkout(context):
    cart = page(context, CartPage).open()
    cart.checkout()


# Day 4 review finding F1: one regex step replaces the "item" / "items" pair.
use_step_matcher("re")


@then(r"the cart should contain (?P<count>\d+) items?")
def step_cart_count(context, count):
    count = int(count)
    cart = page(context, CartPage).open()
    actual = cart.total_quantity()
    assert actual == count, f"Expected {count} item(s) in the cart, found {actual}"
    assert cart.mini_cart_count() == count, f"Mini-cart shows {cart.mini_cart_count()}, expected {count}"


use_step_matcher("parse")


@then('the cart total should be "{expected}"')
def step_cart_total(context, expected):
    cart = page(context, CartPage).open()
    actual = cart.total()
    assert actual == money_to_float(expected), f"Expected total {expected}, found £{actual:.2f}"


@then("the cart should be empty")
def step_cart_empty(context):
    cart = page(context, CartPage).open()
    assert cart.is_empty(), f"Cart still holds {cart.total_quantity()} item(s)"


@then("the checkout page should be shown")
def step_checkout_shown(context):
    cart = page(context, CartPage)
    cart.wait.until(EC.url_contains("checkout"))


@then('the checkout should list "{name}"')
def step_checkout_lists(context, name):
    cart = page(context, CartPage)
    cart.wait.until(lambda d: name in cart.body_text())
