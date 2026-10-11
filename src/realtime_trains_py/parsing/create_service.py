from datetime import datetime as dt
from tabulate import tabulate

from realtime_trains_py.internal.details import ServiceLocationData, ServiceData
from realtime_trains_py.parsing.parse_service_data import parse_service_data
from realtime_trains_py.internal.utilities import get_scheduled_time


def create_service_record(
    service_data, service_uid: str, complexity: str
) -> ServiceData:
    # Extract the relevant data from the API response and create a ServiceData data class to return
    operator = (
        service_data["scheduleMetadata"]["operator"].pop("name")
        if "name" in service_data["scheduleMetadata"]["operator"]
        else "Unknown"
    )

    origin = service_data["origin"][0]["location"].pop("description")
    if "scheduleAdvertised" in service_data["origin"][0]["temporalData"]:
        start_time = get_scheduled_time(
            service_data["origin"][0]["temporalData"], "scheduleAdvertised"
        )

    else:
        start_time = get_scheduled_time(
            service_data["origin"][0]["temporalData"], "scheduleInternal"
        )

    destination = service_data["destination"][0]["location"].pop("description")

    if "scheduleAdvertised" in service_data["destination"][0]["temporalData"]:
        end_time = get_scheduled_time(
            service_data["destination"][0]["temporalData"],
            "scheduleAdvertised",
        )

    else:
        end_time = get_scheduled_time(
            service_data["destination"][0]["temporalData"],
            "scheduleInternal",
        )

    coaches = 0

    calling_points: list[ServiceLocationData] = []
    calling_point_data: list[list[str]] = []

    # Iterate through the locations in the service data and create ServiceLocationData data classes for each location.
    # If the complexity is simple, create a 2D array to print as a table later.
    if "locations" in service_data:
        for locations in service_data["locations"]:
            calling_point = parse_service_data(locations, "calling_point")

            if calling_point.coaches != 0:
                coaches = calling_point.coaches

            if complexity == "s":
                calling_point_data.append(
                    [
                        calling_point.stop_name,
                        calling_point.scheduled_arrival,
                        calling_point.expected_arrival,
                        calling_point.platform,
                        calling_point.line,
                        calling_point.scheduled_departure,
                        calling_point.expected_departure,
                    ]
                )

            else:
                calling_points.append(calling_point)

    if complexity == "s":
        if coaches != 0:
            print(
                f"{service_uid} \n  {start_time} {origin} to {destination} \n  A {operator} service formed of {coaches} coaches.\n\n  Generated at {dt.now().strftime('%H:%M:%S on %d/%m/%y.')}"
            )

        else:
            print(
                f"{service_uid} \n  {start_time} {origin} to {destination} \n  Operated by {operator} \n\n  Generated at {dt.now().strftime('%H:%M:%S on %d/%m/%y.')}"
            )

        # Print the table for the service and return an empty ServiceData object since the data is printed and not returned as an object
        print(
            tabulate(
                calling_point_data,
                tablefmt="rounded_grid",
                headers=[
                    "Stop Name",
                    "Scheduled \n\nArrival",
                    "Expected \n\nArrival",
                    "Platform",
                    "Line",
                    "Scheduled \n\nDeparture",
                    "Expected \n\nDeparture",
                ],
            )
        )
        return ServiceData("", "", "", "", [], "", "", 0)

    return ServiceData(
        service_uid,
        operator,
        origin,
        destination,
        calling_points,
        start_time,
        end_time,
        coaches,
    )
