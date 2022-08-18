import tests.config as config
import logging
import pytest
import os
# selenium dependencies
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromiumService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.remote.webdriver import WebDriver
# webdriver manager dependencies
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.core.utils import ChromeType
# imported pages
from pages.login_page import LoginPage
from pages.dynamic_loading_pages import DynamicLoadingPage
from _pytest.fixtures import FixtureRequest
from _pytest.config.argparsing import Parser

LOGGER = logging.getLogger(__name__)


@pytest.fixture
def driver(request: FixtureRequest, headless: bool) -> WebDriver:

    # configurations from CLI
    config.base_url = request.config.getoption("--baseurl")
    config.browser = request.config.getoption("--browser").lower()

    if config.host == "saucelabs":
        LOGGER.info(f"Running tests on Saucelabs")
    else:
        LOGGER.info(f"Running tests on localhost")
        if config.browser == "chrome":
            LOGGER.info("Running with Chrome")
            chrome_options = webdriver.ChromeOptions()
            if headless == True:
                LOGGER.info("Headless mode enabled")
                chrome_options.add_argument("--headless")
            chrome_options.add_argument("--start-maximized")
            chrome_options.add_argument("--log-level=3")
            chrome_options.add_argument("--disable-extensions")

            driver_ = webdriver.Chrome(
                service=ChromiumService(
                    ChromeDriverManager(
                        chrome_type=ChromeType.CHROMIUM).install()
                ),
                options=chrome_options)
        elif config.browser == "firefox":
            LOGGER.info("Running with Firefox")
            options = FirefoxOptions()
            if headless:
                options.headless = True
            driver_ = webdriver.Firefox(
                options=options,
                service=FirefoxService(GeckoDriverManager().install(),
                                    log_path=os.devnull),
            )
            driver_.maximize_window()

        yield driver_

        def quit():
            driver_.quit()

        request.addfinalizer(quit)


@pytest.fixture
def login(driver: WebDriver) -> LoginPage:
    login_page = LoginPage(driver)
    return login_page


@pytest.fixture
def dynamic_loading(driver: WebDriver) -> DynamicLoadingPage:
    dynamic_loading_page = DynamicLoadingPage(driver)
    return dynamic_loading_page


def pytest_addoption(parser: Parser) -> None:
    parser.addoption(
        "--headless",
        action="store",
        default=False,
        help="my option: type1 or type2",
        choices=("True", "False")
    )
    parser.addoption("--baseurl",
                     action="store",
                     default="http://the-internet.herokuapp.com/",
                     help="base url for the test")
    parser.addoption("--browser",
                     action="store",
                     default="chrome",
                     help="browser for the test",
                     choices=("chrome", "firefox")
                     )
    parser.addoption("--host",
                     action="store",
                     default="saucelabs",
                     help="host for the test: localhost or saucelabs",
                     choices=("localhost", "saucelabs"))
    parser.addoption("--platform",
                     action="store",
                     default="Windows 10",
                     help="OS platform for the test")


@pytest.fixture
def headless(request: FixtureRequest) -> bool:
    return bool(request.config.getoption("--headless").capitalize())