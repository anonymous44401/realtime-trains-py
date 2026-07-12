# Import external libraries
import sys
import time
from datetime import datetime

import requests

# Import necessary items from other files
from realtime_trains_py.internal.details import StationBoardDetails
from realtime_trains_py.internal.errors import AuthenticationError
from realtime_trains_py.internal.utilities import check_cancel, get_dep_service_data, validate_tiploc


class LiveBoard:
    # Take the request token and the token to create a new request token when the old request token expires
    def __init__(self, api_request_token: str, request_token: str) -> None:
        self.__headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {api_request_token}",
        }
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

    def _get_live(self, tiploc: str, mode: str = "LCD") -> None:
        # Output a helpful message to the user: Press Ctrl+C to close live departure board.
        sys.stdout.write("\033[1;2mPress Ctrl+C to close live departure board.\n")
        time.sleep(2)

        first_run: bool = True

        params = {
            "code": f"gb-nr:{validate_tiploc(tiploc)}",
            "timeTolerance": "false",
            "detailed": "false",
        }

        while True:
            departure_board: list[StationBoardDetails] = []
            # Update the departure board every 60 seconds, on the minute
            if first_run or datetime.now().strftime("%S") == "00":
                first_run = False

                response = self.__session.get(
                    "https://data.rtt.io/rtt/location",
                    params=params,
                    headers=self.__headers,
                )

                if response.status_code == 200:
                    departure_data = response.json()
                    # Get the requested location name
                    requested_location = departure_data["query"]["location"].pop(
                        "description"
                    )

                    # Get the service details for the first 3 services in the departure data and append them to a list
                    for service in departure_data["services"][:3]:
                        departure_board.append(get_dep_service_data(service))

                    # Show the first line and update colours based on the given mode. If the mode is DMI.Y, set the text colour to yellow. If the
                    # mode is DMI.W, set the text colour to white. If the mode is LCD, set the text colour to default.

                    match mode:
                        case "DMI.Y":
                            line_one = f"\033[1;93m{requested_location} Live:\n"

                        case "DMI.W":
                            line_one = f"\033[1;39m{requested_location} Live:\n"

                        case _:
                            line_one = (
                                f"\033[1;34m{requested_location} Live:\n\033[1;39m"
                            )

                    line_two = line_three = line_four = line_five = ""
                    first = True
                    second = False

                    # For each service in the departure board, get the details of the first 3 services and print them to the screen
                    for service in departure_board:
                        if first:
                            # Get the details of the first service, including subsequent calling points, service operator and number of coaches if available
                            line_two, line_three = self.__first_service(
                                service, requested_location, mode
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
                                line_four = f"2nd {line}"

                            else:
                                line_five = f"3rd {line}"

                    # Clear the screen and print the live board information to the screen
                    sys.stdout.write(
                        f"\033c\r{line_one}{line_two}{line_three}{line_four}{line_five}"
                    )

                elif response.status_code == 401:
                    # Check the request token and update the headers with the new token
                    self.__update_api_request_token()

                    first_run = (
                        True  # To immediately retry the request with the new token
                    )

                # If no data is found, display a "Check timetable for services" message
                else:
                    first_run = False
                    # Clear the screen and output a message to the user to check the timetable for services, in blue text
                    sys.stdout.write(
                        f"\033c\r\033[1;34m{tiploc} Live:\n \033[1;30mCheck timetable for services\n"
                    )

            # Display the current time at the bottom of the board and update it every second
            sys.stdout.write(
                f"\033[1;3m{datetime.now().strftime('         %H:%M:%S')}\033[K\r"
            )
            time.sleep(1)

    def __first_service(
        self, service: StationBoardDetails, requested_location: str, mode
    ) -> tuple:
        params = {
            "uniqueIdentity": f"gb-nr:{service.service_uid}:{datetime.now().strftime('%Y-%m-%d')}",
            "timeTolerance": "false",
            "detailed": "false",
        }

        # Get the service data for the first service
        all_service_data = self.__session.get(
            "https://data.rtt.io/rtt/service", params=params, headers=self.__headers
        ).json()["service"]

        line_three = "Calling at: "

        # Prepare to unpack service info
        location_data = all_service_data["locations"]

        # If the service terminates at the requested location, display that it terminates here and its origin.
        # Otherwise, display the scheduled departure time, destination, platform and whether it's on time, delayed or cancelled.
        if service.terminus == requested_location:
            line_two = f"1st {service.scheduled_arrival} Terminates here. Service from {all_service_data['origin'][0]['location'].pop('description')}  {service.expected_arrival if mode != 'LCD' else check_cancel(service.expected_arrival)}\n"

        else:
            line_two = f"1st {service.scheduled_departure} {service.terminus} {service.platform}  {service.expected_departure if mode != 'LCD' else check_cancel(service.expected_departure)}\n"

        can_add_calling_points = False
        stops_outputted = (
            False  # Used to determine if any stops have been added to the line yet
        )
        number_of_stops = len(
            location_data
        )  # Number of stops in the service, used to determine how to format the calling points line
        coaches = 0
        stop_count = 0  # Keep track of the number of stops added
        for location in location_data:
            # Get the name of the next stop
            stop_name = location["location"].pop("description")
            stop_count += 1

            # If the stop count is equal to the number of stops, check if a number of coaches is given in the location data, get that number to display
            # later. Check if any stops have been outputted. If they have, add the stop name to the end of the line without an ampersand and set
            # can_add_calling_points to False. If they haven't, add the stop name with 'only' and break the loop.
            if stop_count == number_of_stops:
                if coaches == 0 and "numberOfVehicles" in location["locationMetadata"]:
                    coaches = location["locationMetadata"].pop("numberOfVehicles")

                if stops_outputted:
                    can_add_calling_points = False
                    line_three += f"{stop_name}"

                else:
                    # Only stop
                    #     Calling at: station only
                    line_three += f"{stop_name} only"
                    break

            # If can_add_calling_points is True, set stops_outputted to True. If the stop count is one less than the number of stops, add the stop
            # name with an ampersand. Otherwise, add the stop name with a comma. This is used to format the calling points line correctly
            # based on the number of stops in the service.
            if can_add_calling_points:
                stops_outputted = True
                if stop_count == number_of_stops - 1:
                    # Penultimate stop:
                    #     Calling at: ... station & station
                    line_three += f"{stop_name} & "

                else:
                    # Intermediate stop:
                    #     Calling at: station, station, station, ...
                    line_three += f"{stop_name}, "

            # If the stop name is the same as the requested location, set can_add_calling_points to True to start adding stops to the line.
            # This is used to only display the calling points after the requested location in the service, as the previous calling
            # points would have already been displayed on a previous board.
            elif stop_name == requested_location:
                can_add_calling_points = True

        line_three += (
            f". {all_service_data['scheduleMetadata']['operator'].pop('name')} service"
        )

        # If the number of coaches is given, add that to the end of the line. Otherwise add \n
        line_three += f" formed of {coaches} coaches\n" if coaches > 0 else "\n"

        return line_two, line_three
