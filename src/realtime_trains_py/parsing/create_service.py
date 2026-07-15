from datetime import datetime
from tabulate import tabulate

from realtime_trains_py.internal.details import ServiceLocationData, ServiceData
from realtime_trains_py.parsing.parse_service_data import parse_service_data


def create_service_record(service_data, service_uid: str, complexity: str) -> ServiceData:
    # Extract the relevant data from the API response and create a ServiceData data class to return
    operator = service_data["scheduleMetadata"]["operator"].pop("name")
    origin = service_data["origin"][0]["location"].pop("description")
    start_time = (
        service_data["origin"][0]["temporalData"]
        .pop("scheduleAdvertised")
        .split("T")[1][:5]
    )
    destination = service_data["destination"][0]["location"].pop("description")
    end_time = (
        service_data["destination"][0]["temporalData"]
        .pop("scheduleAdvertised")
        .split("T")[1][:5]
    )
    coaches = 0

    calling_points: list[ServiceLocationData] = []
    calling_point_data: list[list[str]] = []

    # Iterate through the locations in the service data and create ServiceLocationData data classes for each location.
    # If the complexity is simple, create a 2D array to print as a table later.
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
                f"{service_uid} \n  {start_time} {origin} to {destination} \n  A {operator} service formed of {coaches} coaches.\n\n  Generated at {datetime.now().strftime('%H:%M:%S on %d/%m/%y.')}"
            )

        else:
            print(
                f"{service_uid} \n  {start_time} {origin} to {destination} \n  Operated by {operator} \n\n  Generated at {datetime.now().strftime('%H:%M:%S on %d/%m/%y.')}"
            )

        # Print the table for the service and return an empty ServiceData object since the data is printed and not returned as an object
        print(
            tabulate(
                calling_point_data,
                tablefmt="rounded_grid",
                headers=[
                    "Stop Name",
                    "Scheduled Arrival",
                    "Expected Arrival",
                    "Platform",
                    "Line",
                    "Scheduled Departure",
                    "Expected Departure",
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