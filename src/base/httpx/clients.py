from typing import Callable, Mapping, TYPE_CHECKING

from bs4 import BeautifulSoup
from httpx import AsyncClient as HttpxAsyncClient
from httpx import Client as HttpxClient

if TYPE_CHECKING:
    from ssl import SSLContext

    from httpx._types import AuthTypes, CertTypes, CookieTypes, HeaderTypes, ProxyTypes, QueryParamTypes, TimeoutTypes  # noqa
    from httpx._config import DEFAULT_LIMITS, DEFAULT_MAX_REDIRECTS, DEFAULT_TIMEOUT_CONFIG  # noqa
    from httpx._models import EventHook, Limits, Response  # noqa
    from httpx._transports.base import BaseTransport  # noqa
    from httpx._types import URL  # noqa


def parse_html_into_bs4(html: str) -> BeautifulSoup:
    return BeautifulSoup(html, "html.parser")


def parse_response_into_bs4(response: Response) -> BeautifulSoup:
    """Parse an HTTPx response into a BeautifulSoup object."""
    return parse_html_into_bs4(response.text)
