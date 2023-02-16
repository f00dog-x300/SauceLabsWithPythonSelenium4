import logging
import os
import pytest
import config as setting
from datetime import datetime
from pathlib import Path
from selenium.webdriver.remote.webdriver import WebDriver
from _pytest.fixtures import FixtureRequest
from _pytest.config.argparsing import Parser
from pages.login_page import LoginPage
from pages.dynamic_loading_pages import DynamicLoadingPage
from drivers.localrunner import ChromeRunner, FirefoxRunner
from drivers.remote_driver import BSRunner, SauceRunner


LOGGER = logging.getLogger(__name__)


@pytest.fixture
def driver(request: FixtureRequest, headless: bool) -> WebDriver:
    """Webdriver that initiates the browser and sets up the test environment.
    Utilizes request pytest fixture and headless option."""

    # uses values from CLI commands else uses pre-set values from config.py
    setting.BASE_URL = request.config.getoption(
        "--baseurl") or setting.BASE_URL
    setting.BROWSER = request.config.getoption(
        "--browser").lower() or setting.BROWSER
    setting.HOST = request.config.getoption("--host").lower() or setting.HOST
    setting.OS_VERSION = request.config.getoption(
        "--os-version") or setting.OS_VERSION
    setting.PLATFORM = request.config.getoption(
        "--platform") or setting.PLATFORM

    test_name = request.node.name

    if setting.HOST in ("saucelabs", "saucelabs-tunnel"):
        LOGGER.info(">> Running tests on Saucelabs")
        sauce_driver = SauceRunner(testname=test_name)
        driver_ = sauce_driver.start_driver()

    elif setting.HOST == "browserstack":
        LOGGER.info(">> Running tests on Browserstack")
        bs_runner = BSRunner(testname=test_name)
        driver_ = bs_runner.start_driver()

    elif setting.HOST == "localhost":
        LOGGER.info(">> Running tests on localhost")

        if setting.BROWSER == "chrome":
            LOGGER.info(f"... browser: {setting.BROWSER}")
            chrome_runner = ChromeRunner(headless=headless, testname=test_name)
            driver_ = chrome_runner.start_driver()

        elif setting.BROWSER == "firefox":
            LOGGER.info(f"... browser: {setting.BROWSER}")
            ff_runner = FirefoxRunner(headless=headless, testname=test_name)
            driver_ = ff_runner.start_driver()

    yield driver_

    def quit() -> None:
        """Allows for the driver to be quit after the test 
        has finished. Also reports to host if pass or failed 
        test."""
        # TODO: explore using capsys here to capture stdout and stderr
        test_result = "passed" if (request.node.rep_call.passed) else "failed"

        if setting.HOST == "saucelabs":
            driver_.execute_script(f"sauce:job-result={test_result}")

        if setting.HOST == "browserstack":
            LOGGER.info(f">> Browserstack result: {test_result}")

            if test_result == "passed":
                driver_.execute_script(
                    'browserstack_executor: {"action": "setSessionStatus", "arguments": {"status":"passed", "reason": "Assertions have been validated!"}}')

            elif test_result == "failed":
                driver_.execute_script(
                    'browserstack_executor: {"action": "setSessionStatus", "arguments": {"status":"failed", "reason": "An assertion has failed!"}}')

        driver_.quit()

    request.addfinalizer(quit)


@pytest.fixture
def login(driver: WebDriver) -> LoginPage:
    """Page fixture for the login page. Returns a LoginPage object."""
    login_page = LoginPage(driver)
    return login_page


@pytest.fixture
def dynamic_loading(driver: WebDriver) -> DynamicLoadingPage:
    """Page fixture for the dynamic loading page. Returns a DynamicLoadingPage object."""
    dynamic_loading_page = DynamicLoadingPage(driver)
    return dynamic_loading_page


def pytest_addoption(parser: Parser) -> None:
    """Adds CLI options to pytest."""
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
                     choices=("localhost", "saucelabs", "saucelabs-tunnel", "browserstack"))
    parser.addoption("--platform",
                     action="store",
                     help="OS platform for the test",
                     choices=("Windows", "OS X", "Linux"))
    parser.addoption("--os-version",
                     action="store",
                     help="OS version for the test",
                     choices=("10", "11", "Monterey", "Big Sur"))


@pytest.fixture
def headless(request: FixtureRequest) -> bool:
    """CLI option to run tests in headless mode"""
    is_headless = request.config.getoption("--headless").capitalize()
    return True if is_headless == "True" else False


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo) -> None:  # pylint: disable=unused-argument
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
    CLI."""
    # set custom options only if none are provided from command line
    if not config.option.htmlpath:
        now = datetime.now()
        # create report target dir
        reports_dir = Path("reports", now.strftime("%Y-%m-%d"))
        reports_dir.mkdir(parents=True, exist_ok=True)
        # custom report file
        report = reports_dir / f"report_{now.strftime('%H%M')}.html"
        # adjust plugin options
        config.option.htmlpath = report
        config.option.self_contained_html = True


@pytest.hookimpl(tryfirst=True)
def pytest_sessionfinish(session, exitstatus):  # pylint: disable=unused-argument
    """Adds metadata to the HTML report."""
    session.config._metadata["project"] = "Demo"
    # session.config._metadata["person running"] = os.getlogin()
    session.config._metadata["tags"] = ["pytest", "selenium", "python"]
    session.config._metadata["browser"] = session.config.getoption("--browser")

    if session.config.getoption("--host") in ("saucelabs", "saucelabs-tunnel", "browserstack"):

        if session.config.getoption("--host") in ("saucelabs", "saucelabs-tunnel"):
            session.config._metadata["host"] = "saucelabs"

        else:
            session.config._metadata["host"] = "browserstack"

        session.config._metadata["platform"] = session.config.getoption(
            "--platform")
        session.config._metadata["browser version"] = session.config.getoption(
            "--browserversion")
