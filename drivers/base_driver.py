import logging
from abc import ABC, abstractmethod
from selenium import webdriver


LOGGER = logging.getLogger(__name__)


class BaseRunner(ABC):
    """Base class for all drivers"""

    @property
    @abstractmethod
    def capabilities(self) -> dict:
        """Returns capabilities"""
        pass

    @abstractmethod
    def start_driver(self) -> webdriver:
        """Returns specific driver"""
        pass
