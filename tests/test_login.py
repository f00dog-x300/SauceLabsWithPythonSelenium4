import pytest
from pages.login_page import LoginPage


def test_valid_credentials(login: LoginPage):
    """Testing with valid credentials. Should show success message."""
    login.with_("tomsmith", "SuperSecretPassword!")
    assert login.success_message_present()

@pytest.mark.bad_credentials
@pytest.mark.parametrize("username, password", [
    ("timsmith", "SuperSecretPassword!"),
    ("tomsmith", "BadPassword!"),
    ("timsmith", "BadPassword!"),
])
def test_with_invalid_credentials(login: LoginPage, username: str, password: str):
    """Testing with invalid credentials. Should show failure message."""
    login.with_(username, password)
    assert login.failure_message_present()
