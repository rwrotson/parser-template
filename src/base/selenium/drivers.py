from pathlib import Path
from typing import Literal, TypedDict

from fake_useragent import UserAgent
from selenium.webdriver import Chrome as ChromeDriver
from selenium.webdriver import (
    ChromeOptions,
    ChromeService,
    EdgeOptions,
    EdgeService,
    FirefoxOptions,
    FirefoxService,
    IeOptions,
)
from selenium.webdriver import Edge as EdgeDriver
from selenium.webdriver import Firefox as FirefoxDriver
from selenium.webdriver import Ie as IeDriver
from selenium.webdriver import Remote as RemoteDriver
from selenium.webdriver.common.options import ArgOptions as Options
from selenium.webdriver.common.service import Service
from selenium.webdriver.ie.service import Service as IEService
from undetected_chromedriver import Chrome as UndetectedChromeDriver
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.manager import DriverManager
from webdriver_manager.core.os_manager import ChromeType
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager, IEDriverManager
from webdriver_manager.opera import OperaDriverManager

type SupportedBrowser = Literal[
    "chrome",
    "undetected_chrome",
    "chromium",
    "brave",
    "edge",
    "firefox",
    "ie",
    "opera",
]

type WebDriver = ChromeDriver | UndetectedChromeDriver | EdgeDriver | FirefoxDriver | IeDriver | RemoteDriver


class BrowserDriver(TypedDict):
    manager_obj: DriverManager
    driver_type: type[WebDriver]
    service_type: type[Service]
    options_type: type[Options]


_BROWSER_PARAMS_MAP: dict[SupportedBrowser, BrowserDriver] = {
    "chrome": {
        "manager_obj": ChromeDriverManager(),
        "driver_type": ChromeDriver,
        "service_type": ChromeService,
        "options_type": ChromeOptions,
    },
    "undetected_chrome": {
        "manager_obj": ChromeDriverManager(chrome_type=ChromeType.GOOGLE),
        "driver_type": UndetectedChromeDriver,
        "service_type": ChromeService,
        "options_type": ChromeOptions,
    },
    "chromium": {
        "manager_obj": ChromeDriverManager(chrome_type=ChromeType.CHROMIUM),
        "driver_type": ChromeDriver,
        "service_type": ChromeService,
        "options_type": ChromeOptions,
    },
    "brave": {
        "manager_obj": ChromeDriverManager(chrome_type=ChromeType.BRAVE),
        "driver_type": ChromeDriver,
        "service_type": ChromeService,
        "options_type": ChromeOptions,
    },
    "edge": {
        "manager_obj": EdgeChromiumDriverManager(),
        "driver_type": EdgeDriver,
        "service_type": EdgeService,
        "options_type": EdgeOptions,
    },
    "firefox": {
        "manager_obj": GeckoDriverManager(),
        "driver_type": FirefoxDriver,
        "service_type": FirefoxService,
        "options_type": FirefoxOptions,
    },
    "ie": {
        "manager_obj": IEDriverManager(),
        "driver_type": IeDriver,
        "service_type": IEService,
        "options_type": IeOptions,
    },
    "opera": {
        "manager_obj": OperaDriverManager(),
        "driver_type": RemoteDriver,
        "service_type": ChromeService,
        "options_type": ChromeOptions,
    },
}


def _parse_executable_path[T: DriverManager](executable_path: Path | str | None, driver_manager: T) -> str:
    if not executable_path:
        executable_path = driver_manager.install()

    return str(executable_path)


def _parse_options[T: Options](options: list[str] | T | None, options_type: type[Options]) -> T:
    if options and not isinstance(options, list) and not isinstance(options, options_type):
        raise ValueError(f"Unsupported options type: {type(options)}")

    if not options:
        return options_type()

    if isinstance(options, list):
        options_obj = options_type()
        for option in options:
            options_obj.add_argument(option)
        return options_obj

    return options


def _add_user_agent[T: Options](options: T, user_agent: UserAgent | str) -> T:
    if isinstance(user_agent, UserAgent):
        user_agent = user_agent.random

    options.add_argument(f"user-agent={user_agent}")

    return options


def create_driver(
    browser: SupportedBrowser,
    *,
    executable_path: Path | str | None = None,
    options: list[str] | Options | None = None,
    user_agent: UserAgent | str | None = None,
    keep_alive: bool = True,
) -> RemoteDriver:
    """Create a Selenium WebDriver instance for the specified browser."""
    try:
        browser_driver = _BROWSER_PARAMS_MAP[browser]
    except KeyError:
        raise ValueError(f"Unsupported browser: {browser}")

    driver_manager_obj = browser_driver["manager_obj"]
    driver_type = browser_driver["driver_type"]
    service_type = browser_driver["service_type"]
    options_type = browser_driver["options_type"]

    executable_path = _parse_executable_path(executable_path, driver_manager_obj)
    options = _parse_options(options=options, options_type=options_type)

    if user_agent:
        _add_user_agent(options=options, user_agent=user_agent)

    if browser == "undetected_chrome":
        return driver_type(executable_path=executable_path, options=options, keep_alive=keep_alive)

    if browser == "opera":
        service = ChromeService(executable_path=executable_path)
        service.start()

        options: ChromeOptions
        options.add_experimental_option("w3c", True)

        return driver_type(
            command_executor=service.service_url,
            options=options,
            keep_alive=keep_alive,
        )

    return driver_type(
        service=service_type(
            executable_path=executable_path,
        ),
        options=options,
        keep_alive=keep_alive,
    )


def create_headless_chrome_driver() -> ChromeDriver:
    options = ChromeOptions()

    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    options.experimental_options["prefs"] = {
        "profile": {
            "default_content_settings": {
                "images": 2,
            }
        }
    }

    return create_driver("chrome", options=options)
