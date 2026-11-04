"""Login and registration pages: /account/login, /account/register"""
from selenium.webdriver.common.by import By

from .base_page import BasePage

ERRORS = ".errors, .form-error, [role='alert']"


class LoginPage(BasePage):
    path = "/account/login"
    FORM = "form[action*='/account/login']"

    def login(self, email: str, password: str):
        self.type(By.CSS_SELECTOR, f"{self.FORM} input[name='customer[email]']", email)
        self.type(By.CSS_SELECTOR, f"{self.FORM} input[name='customer[password]']", password)
        self.submit(By.CSS_SELECTOR, f"{self.FORM} [type='submit']")

    def error_text(self) -> str:
        return self.find(By.CSS_SELECTOR, ERRORS).text

    def open_password_reset(self):
        self.click(By.LINK_TEXT, "Forgot your password?")

    def reset_form_visible(self) -> bool:
        form = self.find(By.CSS_SELECTOR, "form[action*='/account/recover']")
        self.wait.until(lambda d: form.is_displayed())
        return True


class RegisterPage(BasePage):
    path = "/account/register"
    FORM = "form[action*='/account']"

    def register(self, first: str, last: str, email: str, password: str):
        for field, value in (("first_name", first), ("last_name", last),
                             ("email", email), ("password", password)):
            self.type(By.CSS_SELECTOR, f"{self.FORM} input[name='customer[{field}]']", value)
        self.submit(By.CSS_SELECTOR, f"{self.FORM} [type='submit']")

    def error_text(self) -> str:
        return self.find(By.CSS_SELECTOR, ERRORS).text
