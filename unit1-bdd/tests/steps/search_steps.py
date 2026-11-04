"""Search steps (REQ-08)."""
from behave import then, when
from selenium.webdriver.common.by import By

from pages import BasePage
from helper_utility.helpers import page


@when('the customer searches for "{keyword}"')
def step_search(context, keyword):
    page(context, BasePage).search(keyword)


@then('the results should include "{name}"')
def step_result_includes(context, name):
    links = context.driver.find_elements(By.CSS_SELECTOR, "a[href*='/products/']")
    names = [link.text for link in links]
    assert any(name in text for text in names), f"{name!r} not in results: {names}"


@then("no products should be shown in the results")
def step_no_results(context):
    links = context.driver.find_elements(By.CSS_SELECTOR, "a[href*='/products/']")
    assert not links, f"Expected no results, found {[l.text for l in links]}"
