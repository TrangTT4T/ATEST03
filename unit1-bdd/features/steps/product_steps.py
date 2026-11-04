"""Catalog and product detail steps (REQ-04, REQ-06)."""
from behave import then, when

from pages import CatalogPage, ProductPage
from support.helpers import page, product


@when("the customer browses the full catalog")
def step_browse_catalog(context):
    page(context, CatalogPage).open()


@then('the product "{name}" should be listed at its catalog price')
def step_listed_price(context, name):
    data = product(context, name)
    text = page(context, CatalogPage).tile_text(data["handle"])
    assert name in text, f"Tile for {name!r} not found, got: {text!r}"
    assert data["price"] in text, f"Expected {data['price']} for {name}, tile says: {text!r}"


@then('the product "{name}" should be shown as "{status}"')
def step_listed_status(context, name, status):
    text = page(context, CatalogPage).tile_text(product(context, name)["handle"])
    sold_out = "sold out" in text.lower()
    assert sold_out == (status == "sold out"), f"{name} expected {status!r}, tile says: {text!r}"


@then('the product page should show the name "{name}"')
def step_detail_name(context, name):
    actual = page(context, ProductPage).title()
    assert actual.strip() == name, f"Expected title {name!r}, found {actual!r}"


@then('the product page should show the price "{price}"')
def step_detail_price(context, price):
    assert price in page(context, ProductPage).body_text(), f"Price {price} not shown on product page"


@then("the customer should not be able to add it to the cart")
def step_cannot_add(context):
    assert not page(context, ProductPage).can_add_to_cart(), "Sold-out product can still be added to the cart"
