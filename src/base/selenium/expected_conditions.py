from typing import Callable

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

from base.selenium.types import Locator


def _check_if_has_css_declaration(
    element: WebElement,
    search_property: str,
    search_value: str | None = None,
    *,
    is_case_sensitive: bool = False,
) -> bool:
    if (style := element.get_attribute("style")) is None:
        return False

    style = style.lower() if not is_case_sensitive else style
    search_property = search_property.lower() if not is_case_sensitive else search_property
    search_value = search_value.lower() if not is_case_sensitive else search_value

    css_declarations = style.split(";")
    for declaration in css_declarations:
        if len(declaration_items := [it.strip() for it in declaration.split(":")]) != 2:
            continue
        css_property, css_value = declaration_items

        if (css_property == search_property) and (search_value is None or css_value == search_value):
            return True

    return False


def element_has_css_declaration(
    locator: Locator,
    css_property: str,
    css_value: str,
    *,
    is_case_sensitive: bool = False,
) -> Callable[[WebDriver], bool]:
    def _predicate(driver: WebDriver) -> bool:
        return _check_if_has_css_declaration(
            element=driver.find_element(*locator),
            search_property=css_property,
            search_value=css_value,
            is_case_sensitive=is_case_sensitive,
        )

    return _predicate
