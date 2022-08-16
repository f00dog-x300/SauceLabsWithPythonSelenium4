from pages.login_page import LoginPage

def test_valid_credentials(login: LoginPage):
    login.with_("tomsmith", "SuperSecretPassword!")
    assert login.success_message_present()


def test_with_invalid_credentials(login: LoginPage):
    login.with_("tomsmith", "badpassword")
    assert login.failure_message_present()
