from random import choices
import pytest
from selenium.webdriver.chrome.service import Service as ChromiumService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.utils import ChromeType
from selenium import webdriver
from pages.login_page import LoginPage
from selenium.webdriver.remote.webdriver import WebDriver


@pytest.fixture
def driver(request, headless):
    chrome_options = webdriver.ChromeOptions()
    # if headless:
    if headless == "True":
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

    yield driver_

    def quit():
        driver_.quit()

    request.addfinalizer(quit)


@pytest.fixture
def login(driver: WebDriver):
    login_page = LoginPage(driver)
    return login_page


def pytest_addoption(parser):
    parser.addoption(
        "--headless",
        action="store",
        default=False,
        help="my option: type1 or type2",
        choices=("True", "False"),
    )


@pytest.fixture
def headless(request):
    return request.config.getoption("--headless")
