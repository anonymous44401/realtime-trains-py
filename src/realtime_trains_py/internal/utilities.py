# Import external libraries
import json
import os
import os.path
import re

import requests

# Import necessary items from other files
from realtime_trains_py.internal.details import StationBoardDetails
from realtime_trains_py.internal.errors import (
    AuthenticationError,
    FileWriteError,
    InvalidDateProvided,
    InvalidTimeProvided,
    InvalidTIPLOCProvided,
    InvalidUIDProvided,
)


def check_cancel(actual_departure: str) -> str:
    # Check if the service is cancelled or delayed. Change text colour accordingly. If cancelled, set the text to red.
    # If on time, set the text to green. Otherwise, set the text to yellow. At the end of the line, reset the text colour to default.
    if actual_departure == "Cancelled":
        return f"\033[1;31m{actual_departure}\033[1;39m"

    elif actual_departure == "On time":
        return f"\033[1;32m{actual_departure}\033[1;39m"

    return f"\033[1;33m{actual_departure}\033[1;39m"


def check_token(request_token: str) -> str:
    headers = {"Accept": "application/json", "Authorization": f"Bearer {request_token}"}

    # Test the connection by sending a request to the API info endpoint, with the auth details provided
    if requests.get("https://data.rtt.io/api/info", headers=headers).status_code != 200:
        response = requests.get(
            "https://data.rtt.io/api/get_access_token", headers=headers
        )
        if response.status_code != 200:
            raise AuthenticationError("Request token provided isn't valid.")

        else:
            return response.json()["token"]

    return request_token


def complex_setup() -> None:
    # Check if realtime_trains_py_data folder exists and create it if not
    if not os.path.isdir("realtime_trains_py_data"):
        os.mkdir("realtime_trains_py_data")


def create_file(name: str, contents) -> None:
    # Create file name by adding directory and type
    file_name: str = f"realtime_trains_py_data/{name}.json"

    # Check if file exists
    if not os.path.isfile(file_name):
        with open(file_name, "x", encoding="utf-8") as file:
            json.dump(contents, file, ensure_ascii=False, indent=4)
            print(f"Data saved to file: \n  {file_name}.")

    else:
        raise FileWriteError(file_name)


# Create a new search query for board data requests to the API
def create_parameters(
    tiploc: str,
    filter_from: str | None = None,
    filter_to: str | None = None,
    time: str | None = None,
    date: str | None = None,
) -> dict[str, str]:
    # If a date is provided validate the date
    if date is not None:
        validate_date(date)

    # If a time is provided validate the time
    if time is not None:
        time = validate_time(time)

    # Create the parameters for the API request based on the parameters provided. The tiploc parameter is required,
    # but the filter_from, filter_to, time, and date parameters are optional. If the optional parameters are not provided,
    # they will be set to an empty string in the parameters dictionary.
    parameters: dict[str, str] = {
        "code": f"gb-nr:{validate_tiploc(tiploc)}",
        "filterFrom": f"gb-nr:{filter_from.upper()}" if filter_from is not None else "",
        "filterTo": f"gb-nr:{filter_to.upper()}" if filter_to is not None else "",
        "timeFrom": "",
        "timeTolerance": "false",
        "detailed": "false",
    }

    # Add the timeFrom parameter based on the time and date parameters provided
    if time is not None and date is None:
        parameters["timeFrom"] = time

    elif time is not None and date is not None:
        parameters["timeFrom"] = f"{date} {time}"

    elif time is None and date is not None:
        parameters["timeFrom"] = date

    return parameters

def format_time(time: str) -> str:
    return "".join(time.split(":"))

def get_dep_service_data(service) -> StationBoardDetails:
    # Set initial values for the service details, which will be updated if the relevant data exists in the API response
    expected_departure: str = "-"
    expected_arrival: str = "-"
    platform: str = "-"
    scheduled_arrival: str = "-"
    scheduled_departure: str = "-"

    # Extract the temporal and location data for the service, which contains the details of the departure and arrival times, platform, and coaches.
    temporal_data = service["temporalData"]
    location_data = service["locationMetadata"]

    # Extract arrival data if it exists
    if "arrival" in temporal_data:
        # Check if the service is cancelled based on the API response, and set the expected arrival time accordingly.
        # If the service isn't cancelled, check if there is a realtime actual or forecast arrival time, and set the
        # expected arrival time accordingly. If the realtime data matches the scheduled arrival time, set the expected
        # arrival time to "On time".
        if "scheduleAdvertised" in temporal_data["arrival"]:
            scheduled_arrival = temporal_data["arrival"]["scheduleAdvertised"].split(
                "T"
            )[1][:5]

        if temporal_data["arrival"]["isCancelled"]:
            expected_arrival = "Cancelled"

        else:
            if "realtimeActual" in temporal_data["arrival"]:
                expected_arrival = temporal_data["arrival"]["realtimeActual"].split(
                    "T"
                )[1][:5]

            elif "realtimeForecast" in temporal_data["arrival"]:
                expected_arrival = temporal_data["arrival"]["realtimeForecast"].split(
                    "T"
                )[1][:5]

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
            scheduled_departure = temporal_data["departure"][
                "scheduleAdvertised"
            ].split("T")[1][:5]

        if temporal_data["departure"]["isCancelled"]:
            expected_departure = "Cancelled"

        else:
            if "realtimeActual" in temporal_data["departure"]:
                expected_departure = temporal_data["departure"]["realtimeActual"].split(
                    "T"
                )[1][:5]

            elif "realtimeForecast" in temporal_data["departure"]:
                expected_departure = temporal_data["departure"][
                    "realtimeForecast"
                ].split("T")[1][:5]

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

    return StationBoardDetails(
        scheduled_arrival,
        scheduled_departure,
        service["destination"][0]["location"]["description"],
        service["origin"][0]["location"]["description"],
        platform,
        expected_arrival,
        expected_departure,
        service["scheduleMetadata"].pop("identity"),
        (
            location_data.pop("numberOfVehicles")
            if "numberOfVehicles" in location_data
            else 0
        ),
    )


def validate_date(date: str) -> None:
    # Validate the date provided by the user. The date must be in the format YYYY-MM-DD, and must be a valid date.
    # If the date is not valid, raise an error.
    if (
        re.fullmatch(
            "[1-9][0-9][0-9]{2}-([0][1-9]|[1][0-2])-([1-2][0-9]|[0][1-9]|[3][0-1])",
            date,
        )
        is None
    ):
        raise InvalidDateProvided(date)


def validate_time(time: str) -> str:
    # Validate the time provided by the user. The time must be in the format HHMM, and must be a valid time.
    # If the time is not valid, raise an error.
    if re.fullmatch("([01][0-9]|2[0-3]):([0-5][0-9])", time) is None:
        if re.fullmatch("([01][0-9]|2[0-3])([0-5][0-9])", time) is None:
            raise InvalidTimeProvided(time)

        else:
            return time

    else:
        return format_time(time)




def validate_tiploc(tiploc: str) -> str:
    if len(tiploc) > 7 or len(tiploc) < 3:
        raise InvalidTIPLOCProvided(tiploc)

    return tiploc


def validate_uid(uid: str) -> None:
    # Validate the service UID provided by the user. The UID must be a string starting with a capital letter followed
    # by 5 digits (e.g. A12345). If the UID is not valid, raise an error.
    if re.fullmatch("[A-Z]?[0-9]{5}", uid) is None:
        raise InvalidUIDProvided(uid)
