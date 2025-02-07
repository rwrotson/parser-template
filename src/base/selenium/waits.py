from typing import Callable

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from selenium.types import WaitExcTypes

from base.selenium.types import Locator


def wait_until(
    driver: WebDriver,
    condition: Callable[[WebDriver], bool],
    *,
    timeout: int = 10,
    poll_frequency: float = 0.5,
    ignored_exceptions: WaitExcTypes | None = None,
) -> None:
    wait = WebDriverWait(driver, timeout=timeout, poll_frequency=poll_frequency, ignored_exceptions=ignored_exceptions)
    wait.until(condition)


def wait_until_locator_is_visible(
    driver: WebDriver,
    locator: Locator,
    *,
    timeout: int = 10,
    poll_frequency: float = 0.5,
    ignored_exceptions: WaitExcTypes | None = None,
) -> None:
    wait = WebDriverWait(driver, timeout=timeout, poll_frequency=poll_frequency, ignored_exceptions=ignored_exceptions)
    wait.until(ec.visibility_of_element_located(locator))  # noqa


def wait_until_locator_is_clickable(
    driver: WebDriver,
    locator: Locator,
    *,
    timeout: int = 10,
    poll_frequency: float = 0.5,
    ignored_exceptions: WaitExcTypes | None = None,
) -> None:
    wait = WebDriverWait(driver, timeout=timeout, poll_frequency=poll_frequency, ignored_exceptions=ignored_exceptions)
    wait.until(ec.element_to_be_clickable(locator))  # noqa
