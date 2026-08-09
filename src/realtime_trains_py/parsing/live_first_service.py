from typing import Any

from realtime_trains_py.internal.details import ServiceLocationData
from realtime_trains_py.internal.utilities import check_cancel


def first_service(
    all_service_data: Any,
    service: ServiceLocationData,
    requested_location: str,
    mode: str,
) -> str:
    calling_points_line = "Calling at: "

    # Prepare to unpack service info
    location_data = all_service_data["locations"]

    # If the service terminates at the requested location, display that it terminates here and its origin.
    # Otherwise, display the scheduled departure time, destination, platform and whether it's on time, delayed or cancelled.
    if service.terminus == requested_location:
        destination_line = f"1st {service.scheduled_arrival} Terminates here. Service from {all_service_data['origin'][0]['location'].pop('description')}  {service.expected_arrival if mode != 'LCD' else check_cancel(service.expected_arrival)}\n"

    else:
        destination_line = f"1st {service.scheduled_departure} {service.terminus} {service.platform}  {service.expected_departure if mode != 'LCD' else check_cancel(service.expected_departure)}\n"

    can_add_calling_points = False

    # Used to determine if any stops have been added to the line yet
    stops_outputted = False

    # Number of stops in the service, used to determine how to format the calling points line
    number_of_stops = len(location_data)
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
                calling_points_line += f"{stop_name}"

            else:
                # Only stop
                #     Calling at: station only
                calling_points_line += f"{stop_name} only"
                break

        # If can_add_calling_points is True, set stops_outputted to True. If the stop count is one less than the number of stops, add the stop
        # name with an ampersand. Otherwise, add the stop name with a comma. This is used to format the calling points line correctly
        # based on the number of stops in the service.
        if can_add_calling_points:
            stops_outputted = True
            if stop_count == number_of_stops - 1:
                # Penultimate stop:
                #     Calling at: ... station & station
                calling_points_line += f"{stop_name} & "

            else:
                # Intermediate stop:
                #     Calling at: station, station, station, ...
                calling_points_line += f"{stop_name}, "

        # If the stop name is the same as the requested location, set can_add_calling_points to True to start adding stops to the line.
        # This is used to only display the calling points after the requested location in the service, as the previous calling
        # points would have already been displayed on a previous board.
        elif stop_name == requested_location:
            can_add_calling_points = True

    calling_points_line += (
        f". {all_service_data['scheduleMetadata']['operator'].pop('name')} service"
    )

    # If the number of coaches is given, add that to the end of the line. Otherwise add \n
    calling_points_line += f" formed of {coaches} coaches\n" if coaches > 0 else "\n"

    return destination_line + calling_points_line
