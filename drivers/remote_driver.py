import logging
import os
from selenium import webdriver
from drivers.base_driver import BaseRunner
import config as setting
from dataclasses import dataclass


LOGGER = logging.getLogger(__name__)


@dataclass
class BSRunner(BaseRunner):

    testname: str

    @property
    def capabilities(self) -> webdriver.Remote:
        """Gets config from CLI and conf.py"""

        desired_cap = {
            "bstack:options": {
                "os": setting.PLATFORM,
                "osVersion": setting.OS_VERSION,
                "local": "false",
                "seleniumVersion": "4.1.2",
                "networkLogs": True,
                "sessionName": self.testname,
            },
            "browserName": setting.BROWSER,
            "browserVersion": "latest",
        }

        LOGGER.info(f"bs_stackoptions: {desired_cap}")
        return desired_cap

    def start_driver(self) -> webdriver:
        """Connects to Browserstack and returns driver instance."""
        _username = os.environ["BS_USERNAME"]
        _access_key = os.environ["BS_ACCESS_KEY"]

        URL = f"https://{_username}:{_access_key}@hub.browserstack.com/wd/hub"  # pylint: disable=invalid-name
        driver_ = webdriver.Remote(
            command_executor=URL,
            desired_capabilities=self.capabilities
        )
        LOGGER.info(f"... testing: {self.testname}")
        driver_.maximize_window()
        return driver_


@dataclass
class SauceRunner(BaseRunner):

    testname: str

    @property
    def capabilities(self) -> dict:
        """Gets config from CLI and conf.py"""
        capabilities = {
            "browserName": setting.BROWSER,
            "platformName": f"{setting.PLATFORM} {setting.OS_VERSION}",
            "sauce:options": {
                "name": self.testname
            }
        }
        LOGGER.info(f"sauce capabilities: {capabilities}")
        return capabilities

    def start_driver(self) -> webdriver:
        """Connects to Saucelabs and returns driver instance."""
        _credentials = f"{os.environ['SAUCE_USERNAME']}:{os.environ['SAUCE_ACCESS_KEY']}"
        _url = f"https://{_credentials}@ondemand.saucelabs.com/wd/hub"
        driver_ = webdriver.Remote(
            command_executor=_url,
            desired_capabilities=self.capabilities
        )
        LOGGER.info(f"... testing> {self.testname}")
        driver_.maximize_window()
        return driver_
