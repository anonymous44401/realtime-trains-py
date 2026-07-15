from typing import Literal

from realtime_trains_py.internal.details import ServiceLocationData


def parse_service_data(data, type: Literal["calling_point", "station_board"]) -> ServiceLocationData:
    # Parse data from the API response and return a ServiceLocationData data class based on the type parameter.

    # Set initial values for the service details, which will be updated if the relevant data exists in the API response
    expected_departure: str = "-"
    expected_arrival: str = "-"
    platform: str = "-"
    scheduled_arrival: str = "-"
    scheduled_departure: str = "-"
    line: str = "-"
    coaches = 0

    # Extract the temporal and location data for the service, which contains the details of the departure and arrival times, platform, and coaches.
    temporal_data = data["temporalData"]
    location_data = data["locationMetadata"]

    # Extract arrival data if it exists
    if "arrival" in temporal_data:
        # Check if the service is cancelled based on the API response, and set the expected arrival time accordingly.
        # If the service isn't cancelled, check if there is a realtime actual or forecast arrival time, and set the
        # expected arrival time accordingly. If the realtime data matches the scheduled arrival time, set the expected
        # arrival time to "On time".
        if "scheduleAdvertised" in temporal_data["arrival"]:
            scheduled_arrival = temporal_data["arrival"]["scheduleAdvertised"].split("T")[1][:5]

        if temporal_data["arrival"]["isCancelled"]:
            expected_arrival = "Cancelled"

        else:
            if "realtimeActual" in temporal_data["arrival"]:
                expected_arrival = temporal_data["arrival"]["realtimeActual"].split("T")[1][:5]

            elif "realtimeForecast" in temporal_data["arrival"]:
                expected_arrival = temporal_data["arrival"]["realtimeForecast"].split("T")[1][:5]

            expected_arrival = (
                "On time"
                if expected_arrival == scheduled_arrival
                else f"Exp {expected_arrival}"
            )

    # Extract departure data if it exists
    if "departure" in temporal_data:
        # Check if the service is cancelled based on the API response, and set the expected departure time accordingly.
        # If the service isn't cancelled, check if there is a realtime actual or forecast departure time, and set the
        # expected departure time accordingly. If the realtime data matches the scheduled departure time, set the expected
        # departure time to "On time".
        if "scheduleAdvertised" in temporal_data["departure"]:
            scheduled_departure = temporal_data["departure"]["scheduleAdvertised"].split("T")[1][:5]

        if temporal_data["departure"]["isCancelled"]:
            expected_departure = "Cancelled"

        else:
            if "realtimeActual" in temporal_data["departure"]:
                expected_departure = temporal_data["departure"]["realtimeActual"].split("T")[1][:5]

            elif "realtimeForecast" in temporal_data["departure"]:
                expected_departure = temporal_data["departure"]["realtimeForecast"].split("T")[1][:5]

            expected_departure = (
                "On time"
                if expected_departure == scheduled_departure
                else f"Exp {expected_departure}"
            )

    # Extract platform data if it exists
    if "platform" in location_data:
        # Check if there is forecast or actual platform data in the API response, and set the platform accordingly.
        if "forecast" in location_data["platform"]:
            platform = location_data["platform"]["forecast"]

        else:
            platform = location_data["platform"]["actual"]

    if type == "calling_point":
        # Extract line data if it exists
        if "line" in location_data:
            if "forecast" in location_data["line"]:
                line = location_data["line"]["forecast"]

            else:
                line = location_data["line"]["actual"]
                
        # If a number of coaches is given in the location data, get the number of coaches for the calling point. This is
        # usually the same throughout the service, but if it's given for any other calling point, it can mean that the service
        # gains or loses coaches.
        if "numberOfVehicles" in data["locationMetadata"]:
            coaches = data["locationMetadata"].pop("numberOfVehicles")    

        return ServiceLocationData(
            stop_name=data["location"].pop("description"),
            scheduled_arrival=scheduled_arrival,
            expected_arrival=expected_arrival,
            platform=platform,
            line=line,
            scheduled_departure=scheduled_departure,
            expected_departure=expected_departure,
            coaches=coaches,
            terminus="",
            origin="",
            service_uid="-"
        )
    
    return ServiceLocationData(
        stop_name="-",
        scheduled_arrival=scheduled_arrival,
        scheduled_departure=scheduled_departure,
        terminus=data["destination"][0]["location"]["description"],
        origin=data["origin"][0]["location"]["description"],
        platform=platform,
        expected_arrival=expected_arrival,
        expected_departure=expected_departure,
        service_uid=data["scheduleMetadata"].pop("identity"),
        coaches=(
            location_data.pop("numberOfVehicles")
            if "numberOfVehicles" in location_data
            else 0
        ),
        line=""
    )

