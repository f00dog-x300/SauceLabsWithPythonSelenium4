import tests.config as config
import logging
import pytest
import os
from datetime import datetime
from pathlib import Path
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
    config.host = request.config.getoption("--host").lower()

    if config.host == "saucelabs":
        LOGGER.info(f">> Running tests on Saucelabs")
        test_name = request.node.name
        capabilities = {
            "browserName": config.browser,
            "platformName": config.platform,
            "sauce:options": {
                "name": test_name
            }

        }
        _credentials = f"{os.environ['SAUCE_USERNAME']}:{os.environ['SAUCE_ACCESS_KEY']}"
        _url = f"https://{_credentials}@ondemand.saucelabs.com/wd/hub"
        driver_ = webdriver.Remote(
            command_executor=_url,
            desired_capabilities=capabilities
        )

    elif config.host == "browserstack":
        LOGGER.info(f">> Running tests on Browserstack")
        test_name = request.node.name
        bstack_options = {
            "browserVersion": config.browser,
            "os": config.platform,
            "sessionName": "pytest-browserstack",
            "build": test_name,
            # "userName": os.environ['BS_USERNAME'],
            # "accessKey": os.environ['BS_ACCESS_KEY']
        }
        URL = f"https://{os.environ['BS_USERNAME']}:{os.environ['BS_ACCESS_KEY']}@hub.browserstack.com/wd/hub"
        # options.set_capability("bstack:options", bstack_options)
        driver_ = webdriver.Remote(
            command_executor=URL,
            desired_capabilities=bstack_options
        )

    elif config.host == "localhost":
        LOGGER.info(f">> Running tests on localhost")

        if config.browser == "chrome":
            LOGGER.info(">> Browser: Chrome")
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
            LOGGER.info(">> Browser: Firefox")
            options = FirefoxOptions()

            if headless:
                LOGGER.info("Headless mode enabled")
                options.headless = True

            driver_ = webdriver.Firefox(
                options=options,
                service=FirefoxService(GeckoDriverManager().install(),
                                       log_path=os.devnull),
            )
            driver_.maximize_window()

    yield driver_

    def quit() -> None:
        """Allows for the driver to be quit after the test 
        has finished. Also reports to host if pass or failed 
        test."""
        if config.host == "saucelabs":
            sauce_result = "failed" if request.node.rep_call.failed else "passed"  # added
            driver_.execute_script(f"sauce:job-result={sauce_result}")
        if config.host == "browserstack":
            bs_result = "failed" if request.node.rep_call.failed else "passed"  # added
            test_status = {
                "action": "setSessionStatus",
                "arguments": {
                    "status": bs_result,
                    "reason": "An assertion failed or an exception was thrown",
                }
            }
            driver_.execute_script(
                f"browserstack_executor: {test_status}")
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
    parser.addoption("--headless",
                     action="store",
                     default=False,
                     help="Whether or not to run tests in headless mode",
                     choices=("True", "False")
                     )
    parser.addoption("--baseurl",
                     action="store",
                     default="http://the-internet.herokuapp.com",
                     help="base url for the test")
    parser.addoption("--browser",
                     action="store",
                     default="chrome",
                     help="browser for the test",
                     choices=("chrome", "firefox")
                     )
    parser.addoption("--browserversion",
                     action="store",
                     default="latest",
                     help="browser version for the test",)
    parser.addoption("--host",
                     action="store",
                     default="localhost",
                     help="host for the test: localhost, saucelabs, browserstack",
                     choices=("localhost", "saucelabs", "browserstack"))
    parser.addoption("--platform",
                     action="store",
                     default="Windows 10",
                     help="OS platform for the test")


@pytest.fixture
def headless(request: FixtureRequest) -> bool:
    """CLI option to run tests in headless mode"""
    return bool(request.config.getoption("--headless").capitalize())


# reporting section
@pytest.hookimpl(hookwrapper=True, tryfirst=True)  # added all below
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo) -> None:
    """Sets the result of each test in the report."""
    pytest_html = item.config.pluginmanager.getplugin("html")
    outcome = yield
    report_path = "reports"

    report = outcome.get_result()
    # # set an report attribute for each phase of a call
    setattr(item, "rep_" + report.when, report)

    extra = getattr(report, "extra", [])
    if report.when == "call":
        feature_request = item.funcargs["request"]
        driver = feature_request.getfixturevalue("driver")
        nodeid = item.nodeid
        xfail = hasattr(report, "wasxfail")
        if (report.skipped and xfail) or (report.failed and not xfail):
            file_name = f"{nodeid}_{datetime.today().strftime('%Y-%m-%d_%H_%M')}.png".replace(
                "/", "_").replace("::", "_").replace(".py", "")
            img_path = os.path.join(report_path, "screenshots", file_name)
            driver.save_screenshot(img_path)
            screenshot = driver.get_screenshot_as_base64()  # the hero
            extra.append(pytest_html.extras.image(screenshot, ""))
        report.extra = extra


@pytest.hookimpl(tryfirst=True)
def pytest_configure(config):
    """Configures the report name and folders before test begins. 
    will be ignored if report name is preset in pytest.ini or through
    cli"""
    # set custom options only if none are provided from command line
    if not config.option.htmlpath:
        now = datetime.now()
        # create report target dir
        reports_dir = Path('reports', now.strftime('%Y-%m-%d'))
        reports_dir.mkdir(parents=True, exist_ok=True)
        # custom report file
        report = reports_dir / f"report_{now.strftime('%H%M')}.html"
        # adjust plugin options
        config.option.htmlpath = report
        config.option.self_contained_html = True


@pytest.hookimpl(tryfirst=True)
def pytest_sessionfinish(session, exitstatus):
    session.config._metadata["project"] = "Sauce Labs Demo"
    session.config._metadata["person running"] = os.getlogin()
    session.config._metadata["tags"] = ["pytest", "selenium", "python"]
    session.config._metadata["browser"] = session.config.getoption("--browser")
    if session.config.getoption("--host") == "saucelabs":
        session.config._metadata["host"] = "saucelabs"
        session.config._metadata["platform"] = session.config.getoption(
            "--platform")
        session.config._metadata["browser version"] = session.config.getoption(
            "--browserversion")
