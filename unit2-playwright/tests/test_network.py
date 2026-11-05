"""Network control (Day 6-7): interception, request assertions, fault injection, throttling.

Third-party risk (manual in Unit 1): the shop keeps working when third-party services fail.
"""
import pytest
from playwright.sync_api import expect

pytestmark = [pytest.mark.network, pytest.mark.regression]


@pytest.mark.medium
def test_third_party_calls_are_blocked_and_shop_still_works(shop, page, block_third_party, products):
    shop.home.open()
    # A third-party call made from the page is aborted by the autouse route.
    failed = page.evaluate("""() => fetch('https://www.facebook.com/tr?probe=1').then(() => false, () => true)""")
    assert failed, "third-party request was not blocked"
    assert any("facebook.com" in url for url in block_third_party)
    # The core flow still works without those services.
    shop.product.open_product(products["Grey jacket"]["handle"])
    shop.product.add_to_cart()
    assert shop.cart.open().total_quantity() == 1


@pytest.mark.critical
def test_add_to_cart_posts_the_product_form(shop, page, products):
    shop.product.open_product(products["Striped top"]["handle"])
    with page.expect_request(lambda r: "/cart/add" in r.url and r.method == "POST") as request_info:
        shop.product.add_button.click()
    assert "id=" in (request_info.value.post_data or ""), "add-to-cart POST carries no product id"


@pytest.mark.critical
@pytest.mark.negative
def test_failed_add_to_cart_request_does_not_add_the_product(shop, page, products):
    # Fault injection: the server answers 500 to the add-to-cart call.
    page.route("**/cart/add*", lambda route: route.fulfill(status=500, body="Internal Server Error"))
    shop.product.open_product(products["Noir jacket"]["handle"])
    shop.product.add_button.click()
    page.unroute("**/cart/add*")
    expect(shop.cart.open().quantity_inputs).to_have_count(0)


@pytest.mark.high
@pytest.mark.only_browser("chromium")
def test_catalog_loads_on_a_slow_network(shop, page, context, products):
    # Chromium DevTools protocol: 400 ms latency, ~1.5 Mbit/s, to expose timing assumptions.
    cdp = context.new_cdp_session(page)
    cdp.send("Network.enable")
    cdp.send("Network.emulateNetworkConditions",
             {"offline": False, "latency": 400, "downloadThroughput": 190_000, "uploadThroughput": 90_000})
    shop.catalog.open()
    expect(shop.catalog.tile(products["Bronze sandals"]["handle"])).to_contain_text("£39.99", timeout=15_000)
