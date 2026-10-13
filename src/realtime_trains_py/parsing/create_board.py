from datetime import datetime as dt
from tabulate import tabulate

from realtime_trains_py.internal.details import DefaultBoard, LocationData
from realtime_trains_py.parsing.parse_service_data import parse_service_data


def create_board(service_data, rows, complexity: str, detailed: bool) -> DefaultBoard:
    departure_board: list[LocationData] = []
    departure_board_data: list[list[str | int]] = []
    requested_location: str = service_data["query"]["location"].pop("description")

    # For each service in the departure data, get the service data
    for service in service_data["services"][:rows]:
        service_info = parse_service_data(service, "station_board")

        if complexity.endswith("n"):
            departure_board.append(service_info)

        elif detailed:
            # Unpack the service details and append them to a list if complexity does not end with n
            departure_board_data.append(
                [
                    service_info.scheduled_arrival,
                    service_info.expected_arrival,
                    service_info.origin,
                    service_info.terminus,
                    service_info.platform,
                    service_info.coaches,
                    service_info.scheduled_departure,
                    service_info.expected_departure,
                    service_info.scheduled_pass,
                    service_info.expected_pass,
                    service_info.service_uid,
                ]
            )

        else:
            # Unpack the service details and append them to a list if complexity does not end with n
            departure_board_data.append(
                [
                    service_info.scheduled_arrival,
                    service_info.expected_arrival,
                    service_info.origin,
                    service_info.terminus,
                    service_info.platform,
                    service_info.coaches,
                    service_info.scheduled_departure,
                    service_info.expected_departure,
                    service_info.service_uid,
                ]
            )

    if complexity.endswith("n"):
        return DefaultBoard(departure_board, requested_location)

    # Print the departure info and tabulate table with the headers defined
    print(
        f"Departure board for {requested_location}. Generated at {dt.now().strftime('%H:%M:%S on %d/%m/%y')}."
    )

    if detailed:
        print(
            tabulate(
                departure_board_data,
                tablefmt="rounded_grid",
                headers=[
                    "Scheduled \nArrival",
                    "Expected \nArrival",
                    "Origin",
                    "Destination",
                    "Platform",
                    "Coaches",
                    "Scheduled \nDeparture",
                    "Expected \nDeparture",
                    "Scheduled \nPass",
                    "Expected \nPass",
                    "Service UID",
                ],
            )
        )

    else:
        print(
            tabulate(
                departure_board_data,
                tablefmt="rounded_grid",
                headers=[
                    "Scheduled \nArrival",
                    "Expected \nArrival",
                    "Origin",
                    "Destination",
                    "Platform",
                    "Coaches",
                    "Scheduled \nDeparture",
                    "Expected \nDeparture",
                    "Service UID",
                ],
            )
        )

    return DefaultBoard([], "")
