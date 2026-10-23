# Import external libraries
import asyncio
import sys
import time
import requests

from datetime import datetime as dt

# Import necessary items from other files
from realtime_trains_py.internal.details import LocationData
from realtime_trains_py.internal.errors import AuthenticationError
from realtime_trains_py.internal.utilities import check_cancel, validate_tiploc, fmt
from realtime_trains_py.parsing.live_first_service import first_service
from realtime_trains_py.parsing.parse_service_data import parse_service_data


class AsyncLiveBoard:
    # Take the request token and the token to create a new request token when the old request token expires
    def __init__(self, headers: dict[str, str], request_token: str) -> None:
        self.__headers = headers
        self.__session = requests.Session()
        self.__request_token = request_token

    async def __update_api_request_token(self) -> None:
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

    async def _get_live(self, tiploc: str, mode: str = "LCD", refresh=90) -> None:
        # Output a helpful message to the user: Press Ctrl+C to close live departure board.
        sys.stdout.write(f"{fmt['grey']}Press Ctrl+C to close live departure board.\n")
        await asyncio.sleep(2)

        next_update: int = int(time.time())

        while True:
            departure_board: list[LocationData] = []
            # Update the departure board every refresh time
            if int(time.time()) == next_update:

                response = self.__session.get(
                    "https://data.rtt.io/rtt/location",
                    params={
                        "code": f"gb-nr:{validate_tiploc(tiploc)}",
                        "timeTolerance": "false",
                        "detailed": "false",
                    },
                    headers=self.__headers,
                )

                if response.status_code == 200:
                    departure_data = response.json()
                    # Get the requested location name
                    requested_location = departure_data["query"]["location"].pop(
                        "description"
                    )

                    # Get the service details for the first 3 services in the departure data and append them to a list
                    if "services" in departure_data:
                        for service in departure_data["services"][:3]:
                            departure_board.append(
                                parse_service_data(service, "station_board")
                            )

                    else:
                        sys.stdout.write(
                            f"{fmt['clear']}{fmt['blue']}{requested_location} Live:\n {fmt['grey']}Check timetable for services\n"
                        )

                        next_update = int(time.time()) + refresh
                        continue

                    # Show the first line and update colours based on the given mode. If the mode is DMI.Y, set the text colour to yellow. If the
                    # mode is DMI.W, set the text colour to white. If the mode is LCD, set the text colour to default.

                    match mode:
                        case "DMI.Y":
                            line_one = f"{fmt['yellow']}{requested_location} Live:\n"

                        case "DMI.W":
                            line_one = f"{fmt['white']}{requested_location} Live:\n"

                        case _:
                            line_one = f"{fmt['blue']}{requested_location} Live:\n{fmt['white']}"

                    line_two = line_three = line_three = line_four = ""
                    first = True
                    second = False

                    # For each service in the departure board, get the details of the first 3 services and print them to the screen
                    for service in departure_board:
                        if first:
                            # Get the details of the first service, including subsequent calling points, service operator and number of coaches if available
                            line_two = first_service(
                                # Service data request
                                all_service_data=self.__session.get(
                                    "https://data.rtt.io/rtt/service",
                                    params={
                                        "uniqueIdentity": f"gb-nr:{service.service_uid}:{dt.now().strftime('%Y-%m-%d')}",
                                        "timeTolerance": "false",
                                        "detailed": "false",
                                    },
                                    headers=self.__headers,
                                ).json()["service"],
                                service=service,
                                requested_location=requested_location,
                                mode=mode,
                            )
                            first = False
                            second = True

                        else:
                            # If the service terminates at the requested location, display that it terminates here and its origin.
                            # Otherwise, display the scheduled departure time, destination, platform and whether it's on time, delayed or cancelled.
                            if service.terminus == requested_location:
                                line = f"{service.scheduled_arrival} Terminates here. Service from {service.origin}  {service.expected_arrival if mode != 'LCD' else check_cancel(service.expected_arrival)}\n"

                            else:
                                line = f"{service.scheduled_departure} {service.terminus} {service.platform}  {service.expected_departure if mode != 'LCD' else check_cancel(service.expected_departure)}\n"

                            if second:
                                second = False
                                line_three = f"2nd {line}"

                            else:
                                line_four = f"3rd {line}"

                    # Clear the screen and print the live board information to the screen
                    sys.stdout.write(
                        f"{fmt['clear']}{line_one}{line_two}{line_three}{line_four}"
                    )

                elif response.status_code == 401:
                    # Check the request token and update the headers with the new token
                    await self.__update_api_request_token()

                    next_update = int(time.time())
                    continue

                # If no data is found, display a "Check timetable for services" message
                else:
                    match mode:
                        case "DMI.Y":
                            line_one = f"{fmt['yellow']}{tiploc} Live:\n"

                        case "DMI.W":
                            line_one = f"{fmt['white']}{tiploc} Live:\n"

                        case _:
                            line_one = f"{fmt['blue']}{tiploc} Live:\n{fmt['white']}"
                    # Clear the screen and output a message to the user to check the timetable for services
                    sys.stdout.write(
                        f"{fmt['clear']}{line_one} {fmt['grey']}Check timetable for services\n"
                    )

                next_update = int(time.time()) + refresh

            # Display the current time at the bottom of the board and update it every second
            sys.stdout.write(f"{dt.now().strftime('         %H:%M:%S')}{fmt['c_line']}")
            await asyncio.sleep(1)
