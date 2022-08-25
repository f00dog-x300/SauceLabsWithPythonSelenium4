import logging
import os

from abc import ABC, abstractmethod
from dataclasses import dataclass

# webdriver manager dependencies
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromiumService
from webdriver_manager.core.utils import ChromeType
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from webdriver_manager.firefox import GeckoDriverManager


LOGGER = logging.getLogger(__name__)


class LocalRunner(ABC):
    """Base class for all drivers"""

    @property
    @abstractmethod
    def capabilities(self) -> dict:
        """Returns capabilities"""
        pass

    @abstractmethod
    def start_driver(self) -> webdriver:
        """Returns specific driver"""
        pass

@dataclass
class ChromeRunner(LocalRunner):
    """Chrome driver"""

    headless: bool 

    @property
    def capabilities(self) -> webdriver.ChromeOptions:
        LOGGER.info(">> Browser: Chrome")

        options = webdriver.ChromeOptions()
        if self.headless == True:
            LOGGER.info(
                f"Headless mode enabled: {type(self.headless)} - {self.headless}")
            options.add_argument("--headless")
        options.add_argument("start-maximized")
        options.add_argument("--disable-extensions")
        options.add_argument("--log-level=3")
        return options

    def start_driver(self) -> webdriver:
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
        options = FirefoxOptions()

        if self.headless:
            LOGGER.info("Headless mode enabled")
            options.headless = True
        return options
    
    def start_driver(self) -> webdriver:
        driver_ = webdriver.Firefox(
            service=FirefoxService(
                GeckoDriverManager().install(),
                log_path=os.devnull
            ),
            options=self.capabilities
        )
        return driver_
