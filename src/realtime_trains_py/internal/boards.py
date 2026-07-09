# Import external libraries
from datetime import datetime

import requests
from tabulate import tabulate

# Import necessary items from other files
from realtime_trains_py.internal.details import DefaultBoard, StationBoardDetails
from realtime_trains_py.internal.errors import APIResponseError, NoDataFound
from realtime_trains_py.internal.utilities import (
    create_file,
    create_parameters,
    get_dep_service_data,
)


class Boards:
    def __init__(self, api_request_token: str, complexity: str) -> None:
        self.__headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {api_request_token}",
        }
        self.__complexity = complexity

    def _get_dep_board_details(
        self,
        tiploc: str,
        filter_from: str | None = None,
        filter_to: str | None = None,
        rows: int | None = None,
        time: str | None = None,
        date: str | None = None,
    ) -> DefaultBoard:
        # Get the API response using the auth details provided
        api_response = requests.get(
            "https://data.rtt.io/rtt/location",
            headers=self.__headers,
            params=create_parameters(tiploc, filter_from, filter_to, time, date),
        )

        if api_response.status_code == 200:
            service_data = api_response.json()

            if self.__complexity == "c":
                # If complexity is c, save the JSON data to a new .json file in the realtime_trains_py_data folder using the create_file
                # function and return an empty DefaultBoard data class since the data is saved to a file and not returned as a data class object
                create_file(
                    f"{tiploc}_on_{datetime.now().strftime('%Y-%m-%d') if date is None else date}_board_data",
                    service_data,
                )

                return DefaultBoard([], "")

            departure_board: list[StationBoardDetails] = []
            departure_board_data: list[list[str | int]] = []
            requested_location: str = service_data["query"]["location"].pop(
                "description"
            )

            # For each service in the departure data, get the service data
            for service in service_data["services"][:rows]:
                service_info = get_dep_service_data(service)

                if self.__complexity.endswith("n"):
                    departure_board.append(service_info)

                else:
                    # Unpack the service details and append them to a list if complexity does not end with n
                    departure_board_data.append(
                        [
                            service_info.scheduled_arrival,
                            service_info.scheduled_departure,
                            service_info.origin,
                            service_info.terminus,
                            service_info.platform,
                            service_info.coaches,
                            service_info.expected_arrival,
                            service_info.expected_departure,
                            service_info.service_uid,
                        ]
                    )

            if self.__complexity.endswith("n"):
                return DefaultBoard(departure_board, requested_location)

            # Print the departure info and tabulate table with the headers defined
            print(
                f"Departure board for {requested_location}. Generated at {datetime.now().strftime('%H:%M:%S on %d/%m/%y')}."
            )
            print(
                tabulate(
                    departure_board_data,
                    tablefmt="rounded_grid",
                    headers=[
                        "Scheduled \nArrival",
                        "Scheduled \nDeparture",
                        "Origin",
                        "Destination",
                        "Platform",
                        "Coaches",
                        "Actual \nArrival",
                        "Actual \nDeparture",
                        "Service UID",
                    ],
                )
            )

            return DefaultBoard([], "")

        elif api_response.status_code == 404:
            raise NoDataFound()

        else:
            raise APIResponseError(
                f"Failed to connect to the RTT API server: {api_response.status_code} \nResponse message: {api_response.text}"
            )
