from __future__ import annotations  # allows for referencing same class
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver


class LoginPage:

    _username_input = {"by": By.ID, "value": "username"}
    _password_input = {"by": By.ID, "value": "password"}
    _submit_button = {"by": By.CSS_SELECTOR, "value": "button[type='submit']"}
    _success_message = {"by": By.CSS_SELECTOR, "value": ".flash.success"}
    _failure_message = {"by": By.CSS_SELECTOR, "value": ".flash.error"}

    def __init__(self, driver: WebDriver):
        self.driver = driver
        self.driver.get("http://the-internet.herokuapp.com/login")

    def with_(self, username: str, password: str):
        self.driver.find_element(self._username_input["by"],
                                 self._username_input["value"]).send_keys(username)
        self.driver.find_element(self._password_input["by"],
                                 self._password_input["value"]).send_keys(password)
        self.driver.find_element(self._submit_button["by"],
                                 self._submit_button["value"]).click()

    def success_message_present(self):
        return self.driver.find_element(
            self._success_message["by"],
            self._success_message["value"]
        ).is_displayed()

    def failure_message_present(self):
        return self.driver.find_element(
            self._failure_message["by"],
            self._failure_message["value"]
        ).is_displayed()

    def test_invalid_credentials(self, login: LoginPage):
        login.with_("tomsmith", "badpassword")
        assert login.failure_message_present()
