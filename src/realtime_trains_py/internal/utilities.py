# Import external libraries
import datetime
import json
import re
import requests

from os import path

# Import necessary items from other files
from realtime_trains_py.internal.errors import (
    AuthenticationError,
    FileWriteError,
    InvalidDateProvided,
    InvalidTimeProvided,
    InvalidTIPLOCProvided,
    InvalidUIDProvided,
)

# fmt dictionary for formatting codes
fmt: dict[str, str] = {
    "white": "\033[1;39m",
    "grey": "\033[1;2m",
    "red": "\033[1;31m",
    "yellow": "\033[1;33m",
    "green": "\033[1;32m",
    "blue": "\033[1;34m",
    "clear": "\033c\r",
    "c_line": "\033[K\r",
    "s_strike": "\033[9m",
    "e_strike": "\033[m",
}


def check_cancel(expected: str, scheduled: str = "", remove_exp: bool = False) -> str:
    # Check if the service is cancelled or delayed. Change text colour accordingly. If cancelled, set the text to red.
    # If on time, set the text to green. Otherwise, set the text to yellow. At the end of the line, reset the text colour to default.

    if expected == "Cancelled":
        return f"{fmt['red']}{expected}{fmt['white']}"

    elif expected == "On time":
        return f"{fmt['green']}{expected}{fmt['white']}"

    if "Exp" in expected and scheduled != "":
        if check_delay(scheduled.split(" ")[-1], expected.split(" ")[-1]) >= 600:

            if remove_exp:
                return f"{fmt['red']}{expected.split(" ")[-1]}{fmt['white']}"

            else:
                return f"{fmt['red']}{expected}{fmt['white']}"

        elif check_delay(scheduled.split(" ")[-1], expected.split(" ")[-1]) <= 0:

            if remove_exp:
                return f"{fmt['green']}{expected.split(" ")[-1]}{fmt['white']}"

            else:
                return f"{fmt['green']}{expected}{fmt['white']}"

        elif remove_exp:
            return f"{fmt['yellow']}{expected.split(" ")[-1]}{fmt['white']}"

    return f"{fmt['yellow']}{expected}{fmt['white']}"


def check_delay(schedule: str, expected: str):
    print(schedule, expected)
    return int(
        (
            datetime.datetime.strptime(expected, "%H:%M")
            - datetime.datetime.strptime(schedule, "%H:%M")
        ).total_seconds()
    )


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


def create_file(name: str, contents) -> None:
    # Create file name by adding directory and type
    file_name: str = f"{name}.json"

    # Check if file exists
    if not path.isfile(file_name):
        with open(file_name, mode="x", encoding="utf-8") as file:
            json.dump(contents, file, ensure_ascii=False, indent=4)
            print(f"Data saved to file: \n  {file_name}.")

    else:
        raise FileWriteError(file_name)


# Create a new search query for board data requests to the API
def create_parameters(
    tiploc: str,
    filter_from: str | None = None,
    filter_to: str | None = None,
    time_from: str | None = None,
    date_from: str | None = None,
    time_to: str | None = None,
    date_to: str | None = None,
    detailed: bool = False,
) -> dict[str, str]:
    # Create the parameters for the API request based on the parameters provided. The tiploc parameter is required,
    # but the filter_from, filter_to, time, and date parameters are optional. If the optional parameters are not provided,
    # they will be set to an empty string in the parameters dictionary.
    parameters: dict[str, str] = {
        "code": f"gb-nr:{validate_tiploc(tiploc.upper())}",
        "filterFrom": (
            f"gb-nr:{validate_tiploc(filter_from.upper())}"
            if filter_from is not None
            else ""
        ),
        "filterTo": (
            f"gb-nr:{validate_tiploc(filter_to.upper())}"
            if filter_to is not None
            else ""
        ),
        "timeFrom": "",
        "timeTo": "",
        "timeTolerance": "false",
        "detailed": f"{detailed}",
    }

    # Add the timeFrom parameter based on the time and date parameters provided
    if time_from is not None and date_from is None:
        parameters["timeFrom"] = validate_time(time_from)

    elif time_from is not None and date_from is not None:
        parameters["timeFrom"] = (
            f"{validate_date(date_from)} {validate_time(time_from)}"
        )

    elif time_from is None and date_from is not None:
        parameters["timeFrom"] = validate_date(date_from)

    if time_to is not None and date_to is None:
        parameters["timeTo"] = validate_time(time_to)

    elif time_to is not None and date_to is not None:
        parameters["timeTo"] = f"{validate_date(date_to)} {validate_time(time_to)}"

    elif time_to is None and date_to is not None:
        parameters["timeTo"] = validate_date(date_to)

    return parameters


def get_scheduled_time(data, time) -> str:
    return data.pop(time).split("T")[1][:5]


def validate_date(date: str) -> str:
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

    return date


def validate_time(time: str) -> str:
    # Validate the time provided by the user. The time must be in the format HHMM, and must be a valid time.
    # If the time is not valid, raise an error.
    if re.fullmatch("([01][0-9]|2[0-3]):([0-5][0-9])", time) is None:
        if re.fullmatch("([01][0-9]|2[0-3])([0-5][0-9])", time) is None:
            raise InvalidTimeProvided(time)

        else:
            return time

    else:
        return "".join(time.split(":"))


def validate_tiploc(tiploc: str) -> str:
    if len(tiploc) > 7 or len(tiploc) < 3:
        raise InvalidTIPLOCProvided(tiploc)

    return tiploc


def validate_uid(uid: str) -> None:
    # Validate the service UID provided by the user. The UID must be a string starting with a capital letter followed
    # by 5 digits (e.g. A12345). If the UID is not valid, raise an error.
    if re.fullmatch("[A-Z]?[0-9]{5}", uid) is None:
        raise InvalidUIDProvided(uid)
