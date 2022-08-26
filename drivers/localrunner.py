import logging
import os
from dataclasses import dataclass
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromiumService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from webdriver_manager.core.utils import ChromeType
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from drivers.base_driver import LocalRunner


LOGGER = logging.getLogger(__name__)


@dataclass
class ChromeRunner(LocalRunner):
    """Chrome driver"""

    headless: bool

    @property
    def capabilities(self) -> webdriver.ChromeOptions:
        """List out capabilities"""
        LOGGER.info(">> Browser: Chrome")

        options = webdriver.ChromeOptions()
        if self.headless is True:
            LOGGER.info(
                "...Headless mode enabled (chrome)")
            options.add_argument("--headless")
        options.add_argument("start-maximized")
        options.add_argument("--disable-extensions")
        options.add_argument("--log-level=3")
        return options

    def start_driver(self) -> webdriver:
        """Starts Chrome Driver and returns driver instance."""
        driver_ = webdriver.Chrome(
            service=ChromiumService(
                ChromeDriverManager(
                    chrome_type=ChromeType.CHROMIUM).install()
            ),
            options=self.capabilities)
        return driver_


@dataclass
class FirefoxRunner(LocalRunner):

    headless: bool

    @property
    def capabilities(self) -> webdriver.FirefoxOptions:
        """Returns FireFox capabilities"""
        options = FirefoxOptions()

        if self.headless:
            LOGGER.info("...Headless mode enabled (firefox)")
            options.headless = True
        return options

    def start_driver(self) -> webdriver:
        """Starts Firefox Driver and returns driver instance."""
        driver_ = webdriver.Firefox(
            service=FirefoxService(
                GeckoDriverManager().install(),
                log_path=os.devnull
            ),
            options=self.capabilities
        )
        driver_.maximize_window()
        return driver_
