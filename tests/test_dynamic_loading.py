import pytest
from pages.dynamic_loading_pages import DynamicLoadingPage


@pytest.mark.xfail(reason="added xtra 'h' on _hello_world_text")
def test_finish_loading_page(dynamic_loading: DynamicLoadingPage):
    """Testing with valid credentials. Should show success message."""
    dynamic_loading.click_start_button()
    # assert dynamic_loading.is_loading_bar_present()
    assert dynamic_loading.is_hello_world_text_present()
