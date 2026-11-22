from requests import get, Response

from realtime_trains_py.internal.errors import AuthenticationError

URL = "https://data.rtt.io/"
DEFAULT_TIMEOUT = 10


def get_request(
    endpoint: str,
    headers: dict[str, str],
    params: dict[str, str] | None = None,
    timeout: int | float = DEFAULT_TIMEOUT,
) -> Response:
    # Send a request to the api using provided endpoint, headers and parameters
    return get(
        f"{URL}{endpoint}",
        headers=headers,
        params=params,
        timeout=timeout,
    )


def update_headers(request_token: str) -> dict[str, str]:
    headers = {"Accept": "application/json", "Authorization": f"Bearer {request_token}"}

    # Test the connection by sending a request to the API info endpoint, with the auth
    # details provided
    if get_request(endpoint="api/info", headers=headers).status_code != 200:
        response = get_request(endpoint="api/get_access_token", headers=headers)
        if response.status_code != 200:
            raise AuthenticationError("Request token provided isn't valid.")

        else:
            request_token = response.json()["token"]

    return {
        "Accept": "application/json",
        "Authorization": f"Bearer {request_token}",
    }
