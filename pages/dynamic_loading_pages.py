from selenium.webdriver.common.by import By 
from selenium.webdriver.remote.webdriver import WebDriver
from pages.base_page import BasePage

class DynamicLoadingPage(BasePage):

    _start_button = {"by": By.XPATH, "value": "//button[contains(text(), 'Start')]"}
    _loading_bar = {"by": By.ID, "value": "loading"}
    _hello_world_text = {"by": By.ID, "value": "finish"}

    def __init__(self, driver: WebDriver):
        self.driver = driver
        self._visit("dynamic_loading/1")
        assert self._is_displayed(self._start_button)

    def click_start_button(self) -> None:
        self._click(self._start_button)
    
    def is_loading_bar_present(self) -> bool:
        return self._is_displayed(self._loading_bar)

    def is_hello_world_text_present(self) -> bool:
        return self._is_displayed(self._hello_world_text)