from requests import Session, Response

from realtime_trains_py.internal.errors import AuthenticationError

URL = "https://data.rtt.io/"
DEFAULT_TIMEOUT = 10


class RequestSession:
    def __init__(self, request_token):
        self.__session = Session()
        self.__request_token = request_token

        self._update_headers()

    def get_request(
        self,
        endpoint: str,
        params: dict[str, str] | None = None,
        timeout: int | float = DEFAULT_TIMEOUT,
    ) -> Response:
        # Send a request to the api using provided endpoint, headers and parameters
        return self.__session.get(
            f"{URL}{endpoint}",
            headers=self.__headers,
            params=params,
            timeout=timeout,
        )

    def _update_headers(self) -> None:
        self.__headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.__request_token}",
        }
        request_token = self.__request_token

        # Test the connection by sending a request to the API info endpoint, with the auth
        # details provided
        if self.get_request(endpoint="api/info").status_code != 200:
            response = self.get_request(endpoint="api/get_access_token")
            if response.status_code != 200:
                raise AuthenticationError("Request token provided isn't valid.")

            else:
                request_token = response.json()["token"]

        self.__headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {request_token}",
        }
