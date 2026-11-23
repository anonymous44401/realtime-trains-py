from types import TracebackType
from typing import Any

import requests
from requests import Response, get

from realtime_trains_py.internal.errors import (
    AuthenticationError,
    HTTPConnectionError,
    HTTPTimeoutError,
    HTTPTransportError,
)

URL = "https://data.rtt.io/"
DEFAULT_TIMEOUT: int = 10


class HTTPTransport:
    """Synchronous HTTP transport managing connection pooling and request execution."""

    def __init__(
        self,
        session: requests.Session | None = None,
        base_url: str = URL,
    ) -> None:
        self._session = session if session is not None else requests.Session()
        self._owns_session = session is None
        self._base_url = base_url
        self._closed = False

    @property
    def session(self) -> requests.Session:
        return self._session

    @property
    def is_closed(self) -> bool:
        return self._closed

    def request(
        self,
        method: str,
        endpoint: str,
        headers: dict[str, str] | None = None,
        params: dict[str, Any] | None = None,
        timeout: int | float = DEFAULT_TIMEOUT,
    ) -> Response:
        if self._closed:
            raise HTTPTransportError("Cannot make requests on a closed HTTP transport.")

        cleaned_endpoint = endpoint.strip()
        if cleaned_endpoint.startswith(("http://", "https://")):
            url = cleaned_endpoint
        else:
            url = f"{self._base_url.rstrip('/')}/{cleaned_endpoint.lstrip('/')}"

        try:
            return self._session.request(
                method=method.upper(),
                url=url,
                headers=headers,
                params=params,
                timeout=timeout,
            )
        except requests.exceptions.Timeout as exc:
            raise HTTPTimeoutError(str(exc)) from exc
        except requests.exceptions.ConnectionError as exc:
            raise HTTPConnectionError(str(exc)) from exc
        except requests.exceptions.RequestException as exc:
            raise HTTPTransportError(str(exc)) from exc

    def get(
        self,
        endpoint: str,
        headers: dict[str, str] | None = None,
        params: dict[str, Any] | None = None,
        timeout: int | float = DEFAULT_TIMEOUT,
    ) -> Response:
        return self.request(
            method="GET",
            endpoint=endpoint,
            headers=headers,
            params=params,
            timeout=timeout,
        )

    def close(self) -> None:
        if not self._closed:
            try:
                if self._owns_session:
                    self._session.close()
            finally:
                self._closed = True

    def __enter__(self) -> "HTTPTransport":
        if self._closed:
            raise HTTPTransportError("Cannot enter a closed HTTP transport.")
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        self.close()


def get_request(
    endpoint: str,
    headers: dict[str, str],
    params: dict[str, Any] | None = None,
    timeout: int | float = DEFAULT_TIMEOUT,
    transport: HTTPTransport | None = None,
) -> Response:
    if transport is not None:
        return transport.get(
            endpoint,
            headers=headers,
            params=params,
            timeout=timeout,
        )

    try:
        return get(
            f"{URL}{endpoint}",
            headers=headers,
            params=params,
            timeout=timeout,
        )
    except requests.exceptions.Timeout as exc:
        raise HTTPTimeoutError(str(exc)) from exc
    except requests.exceptions.ConnectionError as exc:
        raise HTTPConnectionError(str(exc)) from exc
    except requests.exceptions.RequestException as exc:
        raise HTTPTransportError(str(exc)) from exc


def update_headers(
    request_token: str,
    transport: HTTPTransport | None = None,
) -> dict[str, str]:
    headers = {"Accept": "application/json", "Authorization": f"Bearer {request_token}"}

    owns_transport = False
    if transport is None:
        transport = HTTPTransport()
        owns_transport = True

    try:
        info_resp = transport.get("api/info", headers=headers)
        if info_resp.status_code != 200:
            token_resp = transport.get("api/get_access_token", headers=headers)
            if token_resp.status_code != 200:
                raise AuthenticationError("Request token provided isn't valid.")
            request_token = token_resp.json()["token"]
    finally:
        if owns_transport:
            transport.close()

    return {
        "Accept": "application/json",
        "Authorization": f"Bearer {request_token}",
    }
