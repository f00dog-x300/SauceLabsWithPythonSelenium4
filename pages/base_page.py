from selenium import webdriver
import logging
import tests.config as config
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException


LOGGER = logging.getLogger(__name__)

class BasePage:

    def __init__(self, driver: webdriver):
        """Constructor method for the BasePage class."""
        self.driver = driver

    def _visit(self, url: str) -> None:
        """Visit a url. Requires url to be a string."""
        target_url = f"{config.base_url}/{url}"
        LOGGER.info(f"Visiting {target_url}")
        self.driver.get(f"{target_url}")

    def _find(self, locator: dict, timeout: int = 10) -> WebElement:
        """Find an element and give a default wait of 10 seconds.
        Takes in a dictionary with the "by" and "value" keys. Returns
        a webdriver element.
        """
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(
                    (locator["by"], locator["value"])
                )
            )
            return element
        except TimeoutException as e:
            print(f"Could not find element {locator}. Stacktrace: {e}")

    def _click(self, locator: dict) -> None:
        """Clicks an element. Requires a dictionary with the "by" and "value" keys."""
        self._find(locator).click()

    def _type(self, locator: dict, input_text: str) -> None:
        """Clears text field then types into an element. Requires a dictionary with
        the "by" and "value" keys and input text as string."""
        self._find(locator).clear()
        self._find(locator).send_keys(input_text)

    def _is_displayed(self, locator: dict, timeout: int = 10) -> None:
        """Checks if an element is displayed. Requires a dictionary with the "by" and "value" keys.
        Has default timeout of 10 seconds"""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located(
                    (locator["by"], locator["value"])
                )
            )
            return element.is_displayed()
        
        except TimeoutException as e:
            print(f"Element is currently not displayed in screen.")
            LOGGER.error(f">> Stacktrace: \n{e}")
            return False
