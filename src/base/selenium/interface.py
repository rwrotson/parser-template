from contextlib import asynccontextmanager, contextmanager
from pathlib import Path
from types import TracebackType
from typing import (
    Any,
    AsyncGenerator,
    Callable,
    Generator,
    Literal,
    NotRequired,
    Self,
    Sequence,
    TypedDict,
    get_args,
)

from bs4 import BeautifulSoup
from selenium.types import WaitExcTypes
from selenium.webdriver.common.bidi.script import Script
from selenium.webdriver.common.by import By
from selenium.webdriver.common.fedcm.dialog import Dialog
from selenium.webdriver.common.print_page_options import PrintOptions
from selenium.webdriver.common.timeouts import Timeouts
from selenium.webdriver.common.virtual_authenticator import (
    Credential,
    VirtualAuthenticatorOptions,
)
from selenium.webdriver.remote.bidi_connection import BidiConnection
from selenium.webdriver.remote.fedcm import FedCM
from selenium.webdriver.remote.file_detector import FileDetector
from selenium.webdriver.remote.mobile import Mobile
from selenium.webdriver.remote.script_key import ScriptKey
from selenium.webdriver.remote.switch_to import SwitchTo
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.remote.websocket_connection import WebSocketConnection
from selenium.webdriver.common.options import ArgOptions as Options

from base.selenium.drivers import SupportedBrowser, create_driver
from base.selenium.waits import wait_until


class CookieData(TypedDict):
    name: str
    value: str
    path: NotRequired[str]
    domain: NotRequired[str]
    secure: NotRequired[bool]
    httpOnly: NotRequired[bool]
    expiry: NotRequired[int]
    sameSite: NotRequired[str]


type LogType = Literal["browser", "driver", "client", "server", "performance", "profiler"]


class BaseBrowserInterface:
    def __init__(self, webdriver: WebDriver) -> None:
        self.webdriver = webdriver

    @classmethod
    def create(
        cls,
        browser: SupportedBrowser,
        *,
        executable_path: Path | str | None = None,
        options: list[str] | Options | None = None,
    ) -> Self:
        return cls(
            webdriver=create_driver(
                browser=browser,
                executable_path=executable_path,
                options=options,
            ),
        )

    def __repr__(self):
        wd = self.webdriver
        return f'<{type(wd).__module__}.{type(wd).__name__} (session="{wd.session_id}")>'

    def __enter__(self) -> WebDriver:
        return self.webdriver

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.webdriver.quit()

    @contextmanager
    def file_detector_context(
        self,
        file_detector_class: type[FileDetector],
        *args: Any,
        **kwargs: Any,
    ) -> Generator[None, None, None]:
        """Overrides the current file detector (if necessary) in limited context.
        Ensures the original file detector is set afterward.

        Parameters:
            - file_detector_class : Class of the desired file detector. If the class is different
                from the current file_detector, then the class is instantiated with args and kwargs
                and used as a file detector during the duration of the context manager.
            - args : Optional arguments that get passed to the file detector class during instantiation.
            - kwargs : Keyword arguments, passed the same way as args.
        """
        with self.webdriver.file_detector_context(file_detector_class, *args, **kwargs):
            yield

    @property
    def mobile(self) -> Mobile:
        """Returns the mobile object in the browser."""
        return self.webdriver._mobile  # noqa

    @property
    def name(self) -> str:
        """Returns the name of the underlying browser for this instance."""
        return self.webdriver.name

    def start_client(self):
        """Called before starting a new session.

        This method may be overridden to define custom startup behavior.
        """
        pass

    def stop_client(self):
        """Called after executing a quit command.

        This method may be overridden to define custom shutdown behavior.
        """
        pass

    def start_session(self, capabilities: dict) -> None:
        """Creates a new session with the desired capabilities."""
        self.webdriver.start_session(capabilities)

    def create_web_element(self, element_id: str) -> WebElement:
        """Creates a web element with the specified `element_id`."""
        return self.webdriver.create_web_element(element_id)

    def execute_cdp_cmd(self, cmd: str, cmd_args: dict):
        """Execute Chrome Devtools Protocol command and get returned result.

        The command and command args should follow chrome devtools protocol domains/commands, refer to link:
        https://chromedevtools.github.io/devtools-protocol/

        Returns:
            - A dict, empty dict {} if there is no result to return.
              To getResponseBody: {'base64Encoded': False, 'body': 'response body string'}
        """
        return self.webdriver.execute_cdp_cmd(cmd, cmd_args)

    def execute(self, driver_command: str, params: dict = None) -> dict:
        """Sends a command to be executed by a command.CommandExecutor.

        Parameters:
            - driver_command : The name of the command to execute as a string.
            - params : A dictionary of named Parameters to send with the command.

        Returns:
            - dict - The command's JSON response loaded into a dictionary object.
        """
        return self.webdriver.execute(driver_command, params)

    def get(self, url: str) -> None:
        """Navigate the browser to the specified URL in the current window or tab.

        The method does not return until the page is fully loaded (i.e. the onload event has fired).

        Parameters:
            - url : The URL to be opened by the browser. Must include the protocol, e.g.: http://, https://.
        """
        self.webdriver.get(url)

    @property
    def title(self) -> str:
        """Returns the title of the current page."""
        return self.webdriver.title

    def pin_script(self, script: str, script_key: str | None = None) -> ScriptKey:
        """Store common javascript scripts to be executed later by a unique hashable ID."""
        return self.webdriver.pin_script(script, script_key)

    def unpin(self, script_key: ScriptKey) -> None:
        """Remove a pinned script from storage."""
        self.webdriver.unpin(script_key)

    def get_pinned_scripts(self) -> list[str]:
        """Return a list of all pinned scripts."""
        return self.webdriver.get_pinned_scripts()

    def execute_script(self, script: str, *args: Any) -> dict:
        """Synchronously Executes JavaScript in the current window/frame.

        Parameters:
            - script : The javascript to execute.
            - *args : Any applicable arguments for your JavaScript.

        Example:
            driver.execute_script(
                "document.getElementById(arguments[0]).value = arguments[1];",
                "username",
                "test_user",
            )
        """
        return self.webdriver.execute_script(script, *args)

    def execute_async_script(self, script: str, *args: Any) -> dict:
        """Asynchronously Executes JavaScript in the current window/frame.

        Parameters:
            - script : The javascript to execute.
            - *args : Any applicable arguments for your JavaScript.

        Example:
            driver.execute_async_script(
                "document.getElementById(arguments[0]).value = arguments[1];",
                "username",
                "test_user",
            )
        """
        return self.webdriver.execute_async_script(script, *args)

    @property
    def current_url(self) -> str:
        """Gets the URL of the current page."""
        return self.webdriver.current_url

    @property
    def page_source(self) -> str:
        """Gets the source of the current page."""
        return self.webdriver.page_source

    def close(self) -> None:
        """Closes the current window."""
        self.webdriver.close()

    def quit(self) -> None:
        """Quits the driver and closes every associated window."""
        self.webdriver.quit()

    @property
    def current_window_handle(self) -> str:
        """Returns the handle of the current window."""
        return self.webdriver.current_window_handle

    @property
    def window_handles(self) -> list[str]:
        """Returns the handles of all windows within the current session."""
        return self.webdriver.window_handles

    def maximize_window(self) -> None:
        """Maximizes the current window that webdriver is using."""
        self.webdriver.maximize_window()

    def fullscreen_window(self) -> None:
        """Invokes the window manager-specific 'full screen' operation."""
        self.webdriver.fullscreen_window()

    def minimize_window(self) -> None:
        """Invokes the window manager-specific 'minimize' operation."""
        self.webdriver.minimize_window()

    def print_page(self, print_options: PrintOptions | None = None) -> str:
        """Takes PDF of the current page. Makes the best effort to return a PDF based on the provided Parameters."""
        return self.webdriver.print_page(print_options)

    @property
    def switch_to(self) -> SwitchTo:
        """Return an object containing all options to switch focus into."""
        return self.webdriver.switch_to

    # Navigation
    def back(self) -> None:
        """Goes one step backward in the browser history."""
        self.webdriver.back()

    def forward(self) -> None:
        """Goes one step forward in the browser history."""
        self.webdriver.forward()

    def refresh(self) -> None:
        """Refreshes the current page."""
        self.webdriver.refresh()

    # Options
    def get_cookies(self) -> list[CookieData]:
        """Returns a list of dictionaries, corresponding to cookies visible in the current session."""
        return self.webdriver.get_cookies()

    def get_cookie(self, name: str) -> CookieData | None:
        """Get a single cookie by name. Returns the cookie if found, None if not."""
        return self.webdriver.get_cookie(name)

    def delete_cookie(self, name: str) -> None:
        """Deletes a single cookie with the given name."""
        self.webdriver.delete_cookie(name)

    def delete_all_cookies(self) -> None:
        """Delete all cookies in the scope of the session."""
        self.webdriver.delete_all_cookies()

    def add_cookie(self, cookie_dict: CookieData) -> None:
        """Adds a cookie to your current session."""
        self.webdriver.add_cookie(cookie_dict)

    # Timeouts
    def implicitly_wait(self, time_to_wait_in_s: float) -> None:
        """Sets a sticky timeout to implicitly wait for an element to be found, or a command to complete.
        This method only needs to be called one time per session.
        To set the timeout for calls to execute_async_script, see set_script_timeout.
        """
        self.webdriver.implicitly_wait(time_to_wait_in_s)

    def set_script_timeout(self, time_to_wait_in_s: float) -> None:
        """Set the time that the script should wait during an execute_async_script call before throwing an error."""
        self.webdriver.set_script_timeout(time_to_wait_in_s)

    def set_page_load_timeout(self, time_to_wait_in_s: float) -> None:
        """Set the amount of time to wait for a page load to complete before throwing an error."""
        self.webdriver.set_page_load_timeout(time_to_wait_in_s)

    @property
    def timeouts(self) -> Timeouts:
        """Get all the timeouts that have been set on the current session."""
        return self.webdriver.timeouts

    @timeouts.setter
    def timeouts(self, timeouts: Timeouts) -> None:
        """Set all timeouts for the session. This will override any previously set timeouts."""
        self.webdriver.timeouts = timeouts

    def find_element(self, by: By = By.ID, value: str | None = None) -> WebElement:
        """Find an element given a By strategy and locator."""
        return self.webdriver.find_element(by, value)

    def find_elements(self, by: By = By.ID, value: str | None = None) -> list[WebElement]:
        """Find elements given a By strategy and locator."""
        return self.webdriver.find_elements(by, value)

    @property
    def capabilities(self) -> dict:
        """Returns the drivers current capabilities being used."""
        return self.webdriver.capabilities

    @staticmethod
    def _normalize_screenshot_filename(filename: Path | str) -> str:
        filename = str(filename)
        if not filename.lower().endswith(".png"):
            filename += ".png"
        return filename

    def get_screenshot_as_file(self, filename: Path | str) -> bool:
        """Saves a screenshot of the current window to a PNG image file.
        Returns False if there is any IOError, else returns True. Use full paths in your filename.
        """
        filename = self._normalize_screenshot_filename(filename)
        return self.webdriver.get_screenshot_as_file(filename)

    def save_screenshot(self, filename: str) -> bool:
        """Saves a screenshot of the current window to a PNG image file.
        Returns False if there is any IOError, else returns True.
        """
        filename = self._normalize_screenshot_filename(filename)
        return self.get_screenshot_as_file(filename)

    def get_screenshot_as_png(self) -> bytes:
        """Gets the screenshot of the current window as a binary data."""
        return self.webdriver.get_screenshot_as_png()

    def get_screenshot_as_base64(self) -> str:
        """Gets the screenshot of the current window as a base64 encoded string (useful in embedded images in HTML)."""
        return self.webdriver.get_screenshot_as_base64()

    def set_window_size(self, width: int, height: int, window_handle: str = "current") -> None:  # noqa
        """Sets the width and height of the current window. (window.resizeTo)"""
        self.webdriver.set_window_size(width, height, windowHandle=window_handle)

    def get_window_size(self, window_handle: str = "current") -> dict:
        """Gets the width and height of the current window."""
        return self.webdriver.get_window_size(windowHandle=window_handle)

    def set_window_position(self, x: float, y: float, window_handle: str = "current") -> dict:
        """Sets the x,y position of the current window. (window.moveTo)"""
        return self.webdriver.set_window_position(x=x, y=y, windowHandle=window_handle)

    def get_window_position(self, window_handle: str = "current") -> dict:
        """Gets the x,y position of the current window."""
        return self.webdriver.get_window_position(windowHandle=window_handle)

    def get_window_rect(self) -> dict:
        """Gets the x, y coordinates of the window as well as height and width of the current window."""
        return self.webdriver.get_window_rect()

    def set_window_rect(self, x: int = None, y: int = None, width: int = None, height: int = None) -> dict:
        """Sets the x, y coordinates of the window as well as height and width of the current window.

        This method is only supported for W3C compatible browsers.
        Other browsers should use `set_window_position` and `set_window_size`.
        """
        return self.webdriver.set_window_rect(x, y, width, height)

    @property
    def file_detector(self) -> FileDetector:
        """Gets the file detector to be used when sending keyboard input.
        By default, this is set to a file detector that does nothing.
        """
        return self.webdriver.file_detector

    @file_detector.setter
    def file_detector(self, detector: FileDetector) -> None:
        """Set the file detector to be used when sending keyboard input.
        By default, this is set to a file detector that does nothing.
        """
        self.webdriver.file_detector = detector

    @property
    def orientation(self) -> str:
        """Gets the current orientation of the device."""
        return self.webdriver.orientation

    @orientation.setter
    def orientation(self, value) -> None:
        """Sets the current orientation of the device."""
        self.webdriver.orientation = value

    @property
    def log_types(self) -> list[LogType]:
        """Gets a list of the available log types. This only works with w3c compliant browsers."""
        return self.webdriver.log_types

    def get_log(self, log_type: LogType):
        """Gets the log for a given log type."""
        return self.webdriver.get_log(log_type)

    def start_devtools(self) -> tuple[str, WebSocketConnection]:
        """Starts the DevTools service.

        Returns:
            - A tuple of the DevTools WebSocket URL and the DevTools version.
        """
        return self.webdriver.start_devtools()

    @asynccontextmanager
    async def bidi_connection(self) -> AsyncGenerator[BidiConnection, None]:
        async with self.webdriver.bidi_connection() as connection:
            yield connection

    @property
    def script(self) -> Script:
        """Returns the script object in the browser."""
        return self.webdriver.script

    # Virtual Authenticator Methods
    def add_virtual_authenticator(self, options: VirtualAuthenticatorOptions) -> None:
        """Adds a virtual authenticator with the given options."""
        self.webdriver.add_virtual_authenticator(options)

    @property
    def virtual_authenticator_id(self) -> str:
        """Returns the id of the virtual authenticator."""
        return self.webdriver.virtual_authenticator_id

    def remove_virtual_authenticator(self) -> None:
        """Removes a previously added virtual authenticator.
        The authenticator is no longer valid after removal, so no methods may be called.
        """
        self.webdriver.remove_virtual_authenticator()

    def add_credential(self, credential: Credential) -> None:
        """Injects a credential into the authenticator."""
        self.webdriver.add_credential(credential)

    def get_credentials(self) -> list[Credential]:
        """Returns the list of credentials owned by the authenticator."""
        return self.webdriver.get_credentials()

    def remove_credential(self, credential_id: str | bytearray) -> None:
        """Removes a credential from the authenticator."""
        self.webdriver.remove_credential(credential_id)

    def remove_all_credentials(self) -> None:
        """Removes all credentials from the authenticator."""
        self.webdriver.remove_all_credentials()

    def set_user_verified(self, verified: bool) -> None:
        """Sets whether the authenticator will simulate success or fail on user verification."""
        self.webdriver.set_user_verified(verified)

    def get_downloadable_files(self) -> dict:
        """Retrieves the downloadable files as a map of file names and their corresponding URLs."""
        return self.webdriver.get_downloadable_files()

    def download_file(self, file_name: str, target_directory: Path | str) -> None:
        """Downloads a file with the specified file name to the target directory."""
        self.webdriver.download_file(file_name=file_name, target_directory=str(target_directory))

    def delete_downloadable_files(self) -> None:
        """Deletes all downloadable files."""
        self.webdriver.delete_downloadable_files()

    @property
    def fedcm(self) -> FedCM:
        """Returns the Federated Credential Management (FedCM) dialog object for interaction."""
        return self.webdriver.fedcm

    @property
    def supports_fedcm(self) -> bool:
        """Returns whether the browser supports FedCM capabilities."""
        return self.webdriver.supports_fedcm

    @property
    def dialog(self) -> Dialog:
        """Returns the FedCM dialog object for interaction."""
        return self.webdriver.dialog

    def fedcm_dialog(
        self,
        timeout: int = 5,
        poll_frequency: float = 0.5,
        ignored_exceptions: Sequence[BaseException] | None = None,
    ) -> Dialog:
        """Waits for and returns the FedCM dialog."""
        return self.webdriver.fedcm_dialog(timeout, poll_frequency, ignored_exceptions)


_By = Literal[
    "id",
    "name",
    "xpath",
    "link_text",
    "partial_link_text",
    "tag_name",
    "class_name",
    "css_selector",
]


def _parse_str_to_by_enum(by: _By) -> By:
    if by not in list(get_args(_By)):
        raise ValueError(f"Unsupported By type: {by}")

    return getattr(By, by.upper())


class BrowserInterface(BaseBrowserInterface):
    def get_page_as_bs4(self) -> BeautifulSoup:
        """Get the BeautifulSoup object of the current page source."""
        return BeautifulSoup(self.page_source, "html.parser")

    def wait_until(
        self,
        condition: Callable[[WebDriver], bool],
        *,
        timeout: int = 10,
        poll_frequency: float = 0.5,
        ignored_exceptions: WaitExcTypes | None = None,
    ) -> None:
        """Wait until the condition is met."""
        wait_until(
            self.webdriver,
            condition,
            timeout=timeout,
            poll_frequency=poll_frequency,
            ignored_exceptions=ignored_exceptions,
        )

    def find_element_by(
        self,
        by: _By,
        value: str,
        *,
        timeout_in_s: int | None = None,
        condition: Callable[[WebDriver], bool] | None = None,
    ) -> WebElement:
        """Find an element by some identifier."""
        if (timeout_in_s is not None) and (condition is None):
            self.webdriver.implicitly_wait(timeout_in_s)

        elif (timeout_in_s is not None) and (condition is not None):
            wait_until(self.webdriver, condition, timeout=timeout_in_s)

        return self.webdriver.find_element(by=_parse_str_to_by_enum(by), value=value)

    def find_elements_by(
        self,
        by: _By,
        value: str,
        *,
        timeout_in_s: int | None = None,
        condition: Callable[[WebDriver], bool] | None = None,
    ) -> list[WebElement]:
        """Find elements by some identifier."""
        if (timeout_in_s is not None) and (condition is None):
            self.webdriver.implicitly_wait(timeout_in_s)

        elif (timeout_in_s is not None) and (condition is not None):
            wait_until(self.webdriver, condition, timeout=timeout_in_s)

        return self.webdriver.find_elements(by=_parse_str_to_by_enum(by), value=value)

    def find_bs4_element_by(
        self,
        by: _By,
        value: str,
        *,
        timeout_in_s: int | None = None,
        condition: Callable[[WebDriver], bool] | None = None,
    ) -> BeautifulSoup:
        """Find an element by ID."""
        web_element = self.find_element_by(by, value, timeout_in_s=timeout_in_s, condition=condition)
        return BeautifulSoup(
            markup=web_element.get_attribute("outerHTML"),
            features="html.parser",
        )

    def find_bs4_elements_by(
        self,
        by: _By,
        value: str,
        *,
        timeout_in_s: int | None = None,
        condition: Callable[[WebDriver], bool] | None = None,
    ) -> list[BeautifulSoup]:
        """Find elements by ID."""
        web_elements = self.find_elements_by(by, value, timeout_in_s=timeout_in_s, condition=condition)
        return [
            BeautifulSoup(
                markup=web_element.get_attribute("outerHTML"),
                features="html.parser",
            )
            for web_element in web_elements
        ]