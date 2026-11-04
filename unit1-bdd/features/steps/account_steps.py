"""Login and registration steps (REQ-05, REQ-07)."""
import uuid

from behave import then, when

from pages import LoginPage, RegisterPage
from support.helpers import page


@when('the customer logs in with email "{email}" and password "{password}"')
def step_login(context, email, password):
    page(context, LoginPage).login(email, password)


@when("the customer chooses to reset the password")
def step_reset(context):
    page(context, LoginPage).open_password_reset()


@when("the customer registers without an email address")
def step_register_no_email(context):
    page(context, RegisterPage).register("Test", "User", "", "Passw0rd!2026")


@when("the customer registers with a new random email")
def step_register_random(context):
    email = f"bdd.{uuid.uuid4().hex[:10]}@example.com"
    page(context, RegisterPage).register("BDD", "Tester", email, "Passw0rd!2026")


@then("a login error should be shown")
def step_login_error(context):
    assert page(context, LoginPage).error_text().strip(), "No login error message shown"


@then("the customer should not be logged in")
def step_not_logged_in(context):
    url = context.driver.current_url
    assert "/account/login" in url or not url.rstrip("/").endswith("/account"), f"Unexpectedly logged in: {url}"


@then("the password reset form should be shown")
def step_reset_shown(context):
    assert page(context, LoginPage).reset_form_visible()


@then("a registration error should be shown")
def step_register_error(context):
    assert page(context, RegisterPage).error_text().strip(), "No registration error message shown"


@then("the customer should be logged in")
def step_logged_in(context):
    reg = page(context, RegisterPage)
    reg.wait.until(lambda d: d.current_url.rstrip("/").endswith("/account") or "Log out" in reg.body_text())
