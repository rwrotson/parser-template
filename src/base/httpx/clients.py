from typing import TYPE_CHECKING, Callable, Mapping

from bs4 import BeautifulSoup
from httpx import AsyncClient as HttpxAsyncClient
from httpx import Client as HttpxClient

if TYPE_CHECKING:
    from ssl import SSLContext

    from httpx._config import (  # noqa
        DEFAULT_LIMITS,
        DEFAULT_MAX_REDIRECTS,
        DEFAULT_TIMEOUT_CONFIG,
    )
    from httpx._models import EventHook, Limits, Response  # noqa
    from httpx._transports.base import BaseTransport  # noqa
    from httpx._types import (  # noqa
        URL,  # noqa
        AuthTypes,
        CertTypes,
        CookieTypes,
        HeaderTypes,
        ProxyTypes,
        QueryParamTypes,
        TimeoutTypes,
    )


def parse_html_into_bs4(html: str) -> BeautifulSoup:
    return BeautifulSoup(html, "html.parser")


def parse_response_into_bs4(response: Response) -> BeautifulSoup:
    """Parse an HTTPx response into a BeautifulSoup object."""
    return parse_html_into_bs4(response.text)
