from __future__ import annotations
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from pages.base_page import BasePage


class LoginPage(BasePage):

    _username_input = {"by": By.ID, "value": "username"}
    _password_input = {"by": By.ID, "value": "password"}
    _submit_button = {"by": By.CSS_SELECTOR, "value": "button[type='submit']"}
    _success_message = {"by": By.CSS_SELECTOR, "value": ".flash.success"}
    _failure_message = {"by": By.CSS_SELECTOR, "value": ".flash.error"}
    _login_form = {"by": By.ID, "value": "login"}

    def __init__(self, driver: WebDriver):
        self.driver = driver
        self._visit("login")
        assert self._is_displayed(self._login_form)

    def with_(self, username: str, password: str):
        """Logging in with username and password. Also clicks submit button."""
        self._type(locator=self._username_input, input_text=username)
        self._type(locator=self._password_input, input_text=password)
        self._click(self._submit_button)

    def success_message_present(self):
        """Display success message if present."""
        return self._is_displayed(self._success_message)

    def failure_message_present(self):
        """Display failure message if present."""
        return self._is_displayed(self._failure_message)
