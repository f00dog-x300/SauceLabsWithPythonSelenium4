import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromiumService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.utils import ChromeType
from selenium.webdriver.common.by import By
from pages.login_page import LoginPage


@pytest.fixture
def login(request):
    driver_ = webdriver.Chrome(
        service=ChromiumService(
            ChromeDriverManager(
                chrome_type=ChromeType.CHROMIUM)
            .install()
        ))

    login_page = LoginPage(driver_)

    def quit():
        driver_.quit()

    request.addfinalizer(quit)
    return login_page


def test_valid_credentials(login):
    login.with_("tomsmith", "SuperSecretPassword!")
    assert login.success_message_present()