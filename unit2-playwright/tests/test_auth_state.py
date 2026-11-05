"""Authentication state reuse (Day 6) – risk R04 High.

Unit 1 logged in through the UI in every scenario that needed it. Here the session fixture
`customer_state` logs in once, saves cookies + localStorage, and each test starts already logged in.
Run with:  SAUCE_EMAIL=... SAUCE_PASSWORD=... pytest -m auth
"""
import re

import pytest
from playwright.sync_api import Browser, expect

pytestmark = [pytest.mark.auth, pytest.mark.high, pytest.mark.R04]


def test_saved_auth_state_opens_account_without_login(browser: Browser, base_url, customer_state):
    context = browser.new_context(base_url=base_url, storage_state=str(customer_state))
    page = context.new_page()
    page.goto("/account")
    expect(page).not_to_have_url(re.compile(r"/account/login"))
    expect(page.get_by_role("link", name=re.compile("log ?out", re.I))).to_be_visible()
    context.close()


def test_auth_state_does_not_leak_into_other_tests(page):
    """Isolation check: the default `page` fixture has its own context, so it is NOT logged in."""
    page.goto("/account")
    expect(page).to_have_url(re.compile(r"/account/login"))
