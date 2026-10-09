# Import external libraries
import sys
import time
import requests

from datetime import datetime

# Import necessary items from other files
from realtime_trains_py.internal.errors import AuthenticationError
from realtime_trains_py.internal.utilities import validate_uid, fmt
from realtime_trains_py.parsing.create_service import create_service_record
from realtime_trains_py.parsing.parse_service_board import arrange_output


class LiveService:
    # Take the request token and the token to create a new request token when the old request token expires
    def __init__(self, headers: dict[str, str], request_token: str) -> None:
        self.__headers = headers
        self.__session = requests.Session()
        self.__request_token = request_token

    def __update_api_request_token(self) -> None:
        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.__request_token}",
        }

        # Test the connection by sending a request to the API info endpoint, with the auth details provided
        if (
            self.__session.get(
                "https://data.rtt.io/api/info", headers=headers
            ).status_code
            != 200
        ):
            response = self.__session.get(
                "https://data.rtt.io/api/get_access_token", headers=headers
            )
            if response.status_code != 200:
                raise AuthenticationError("Request token provided isn't valid.")

            else:
                self.__headers["Authorization"] = f"Bearer {response.json()['token']}"

    def watch_service(self, service_uid: str, mode: str, refresh: int = 90) -> None:
        # Output a helpful message to the user: Press Ctrl+C to close live departure board.
        sys.stdout.write(f"{fmt['grey']}Press Ctrl+C to stop watching this service.\n")
        time.sleep(2)

        # Set next update time to now (update instantly)
        next_update: int = int(time.time())

        validate_uid(service_uid)

        while True:
            # Update the board every refresh time
            if int(time.time()) == next_update:

                # Send API request
                response = self.__session.get(
                    "https://data.rtt.io/rtt/service",
                    params={
                        "uniqueIdentity": f"gb-nr:{service_uid}:{datetime.now().strftime('%Y-%m-%d')}"
                    },
                    headers=self.__headers,
                )

                if response.status_code == 200:
                    # Create the service record
                    service_record = create_service_record(
                        response.json()["service"], service_uid, "s.n"
                    )

                    # Clear the board and arrange the output
                    sys.stdout.write(
                        f"{fmt['clear']}{arrange_output(service=service_record, mode=mode)}"
                    )

                    # Add refresh to next update
                    next_update += refresh

                elif response.status_code == 401:
                    # Check the request token and update the headers with the new token
                    self.__update_api_request_token()

                    next_update = int(time.time())

                # If no data is found, display a "Check timetable for services" message
                else:
                    # Clear the screen and output a message to the user to check the timetable for services
                    sys.stdout.write(
                        f"{fmt['clear']}{fmt['blue']}{service_uid}:\n {fmt['grey']}Check timetable for services\n"
                    )

                    next_update += refresh

            # Display the current time at the bottom of the board and update it every second
            sys.stdout.write(
                f"{datetime.now().strftime('         %H:%M:%S')}{fmt['c_line']}"
            )
            time.sleep(1)
