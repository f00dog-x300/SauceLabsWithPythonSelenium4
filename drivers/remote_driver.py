import logging
from selenium import webdriver
from drivers.base_driver import LocalRunner


LOGGER = logging.getLogger(__name__)

class BSRunner(LocalRunner):

    headless: bool

    @property
    def capabilities(self) -> webdriver.Remote:
        """Gets config from CLI and conf.py"""
        pass

    def start_driver(self) -> webdriver:
        """Connects to Browserstack and returns driver instance."""
        pass 