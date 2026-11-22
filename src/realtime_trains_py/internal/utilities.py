# Import external libraries
import datetime as dt
import json
import re

from os import mkdir, path
from typing import Any

# Import necessary items from other files
from realtime_trains_py.internal.errors import (
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
    "purple": "\033[1;35m",
    "cyan": "\033[1;36m",
    "clear": "\033c\r",  # Clear screen
    "c_line": "\033[K\r",  # Clear line
    "s_strike": "\033[9m",  # Start strikethrough
    "e_strike": "\033[m",  # End strikethrough
}


def check_cancel(expected: str, scheduled: str = "", remove_exp: bool = False) -> str:
    # If cancelled, set colour to red
    if expected == "Cancelled":
        return f"{fmt['red']}{expected}{fmt['white']}"

    # If on time, set colour to green
    elif expected == "On time":
        return f"{fmt['green']}{expected}{fmt['white']}"

    # If not on time and a scheduled time is provided, check the delay time
    if "Exp" in expected and scheduled != "":
        delay = check_delay(scheduled.split(" ")[-1], expected.split(" ")[-1])

        # If the delay is greater than 20 minutes (1200 seconds), set the colour to red
        if delay >= 1200:
            colour = fmt["red"]

        # If the delay is greater than 10 minutes (600 seconds), set the colour to purple
        elif delay >= 600:
            colour = fmt["purple"]

        # If the delay is less than 0 seconds, set the colour to cyan
        elif delay <= 0:
            colour = fmt["cyan"]

        # If the delay falls in none of the above time regions, set the colour to yellow
        else:
            colour = fmt["yellow"]

        # Remove "Exp" if applicable then return the value
        if remove_exp:
            return f"{colour} {expected.split(" ")[-1]} {fmt['white']}"

        else:
            return f"{colour}{expected}{fmt["white"]}"

    return f"{fmt['yellow']}{expected}{fmt['white']}"


def check_delay(schedule: str, expected: str):
    # Check the time between the scheduled and expected times in seconds. Return the
    # integer value of this delay
    return int(
        (
            dt.datetime.strptime(expected, "%H:%M")
            - dt.datetime.strptime(schedule, "%H:%M")
        ).total_seconds()
    )


def check_folder(folder) -> None:
    if not path.isdir(folder):
        mkdir(folder)


def create_file(folder: str, name: str, contents) -> str:
    # Create file name by adding directory and type
    check_folder(folder)
    file_name: str = f"{folder}/{name}.json"

    # Check if file exists
    if not path.isfile(file_name):
        with open(file_name, mode="x", encoding="utf-8") as file:
            json.dump(contents, file, ensure_ascii=False, indent=4)

    else:
        raise FileWriteError(file_name)

    return file_name


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
    # Create the parameters for the API request based on the parameters provided. The
    # tiploc parameter is required, but the filter_from, filter_to, time, and date
    # parameters are optional. If the optional parameters are not provided, they will
    # be set to an empty string in the parameters dictionary.
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

    # If there was a time, validate the time and set the value
    if time_from:
        parameters["timeFrom"] = f" {validate_time(time_from)}"

    # If there was a date, validate the date and add the previously defined value of
    # timeFrom if a time was provided. If not, use 0000
    if date_from:
        parameters["timeFrom"] = (
            validate_date(date_from)
            + f" {parameters["timeFrom"] if time_from else "0000"}"
        )

        if not time_to and not time_from and not date_to:
            parameters["timeTo"] = f"{validate_date(date_from)} 2359"

            return parameters

    # If there was no date, prepend the current date to timeFrom
    else:
        parameters["timeFrom"] = (
            dt.datetime.now().strftime("%Y-%m-%d") + parameters["timeFrom"]
        )

    # If neither a date or time were provided, set the timeFrom to now
    if not time_from and not date_from:
        parameters["timeFrom"] = dt.datetime.now().strftime("%Y-%m-%d %H%M")

        # If neither a date or time were provided, set the timeFrom to 4 hours from now
        # and return parameters
        if not time_to and not date_to:
            parameters["timeTo"] = (dt.datetime.now() + dt.timedelta(hours=4)).strftime(
                "%Y-%m-%d %H%M"
            )

            return parameters

    # If there was a time, validate the time and set the value
    if time_to:
        parameters["timeTo"] = validate_time(time_to)

    # If there was a date, validate the date and add the previously defined value of
    # timeTo if a time was provided. If not, use 0000
    if date_to:
        parameters["timeTo"] = (
            validate_date(date_to) + f" {parameters["timeTo"] if time_to else "0000"}"
        )

    # If there was no date, prepend the date provided previously (in timeFrom) to timeTo
    else:
        parameters["timeTo"] = (
            dt.datetime.strptime(parameters["timeFrom"], "%Y-%m-%d %H%M").strftime(
                "%Y-%m-%d"
            )
            + f" {parameters["timeTo"]}"
        )

    # If neither a date or time were provided, set the timeTo to 4 hours from the date
    # provided previously (in timeFrom)
    if not time_to and not date_to:
        parameters["timeTo"] = (
            dt.datetime.strptime(parameters["timeFrom"], "%Y-%m-%d %H%M")
            + dt.timedelta(hours=4)
        ).strftime("%Y-%m-%d %H%M")

    return parameters


def get_scheduled_time(data, time) -> str:
    return data.pop(time).split("T")[1][:5]


def save_file(
    file_name: str,
    data: Any,
    local_folder: str | None = None,  # Folder provided in method
    global_folder: str | None = None,  # Folder provided at __init__
) -> str:
    # If a local folder was provided, save data to the local folder
    if local_folder:
        return create_file(local_folder, file_name, data)

    # If a global folder was provided, save data to the global folder
    elif global_folder:
        return create_file(global_folder, file_name, data)

    # If not folder was provided, save data to the default folder
    else:
        return create_file("realtime_trains_py_data", file_name, data)


def validate_date(date: str) -> str:
    # Validate the date provided by the user. The date must be in the format YYYY-MM-DD,
    # and must be a valid date. If the date is not valid, raise an error.
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
    # Validate the time provided by the user. The time must be in the format HHMM or
    # HH:MM, and must be a valid time. If the time is not valid, raise an error.
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


def validate_uid(uid: str) -> str:
    # Validate the service UID provided by the user. The UID must be a string which
    # can start with a capital letter and must have 5 digits (e.g. A12345 or 12345).
    # If the UID is not valid, raise an error.
    if re.fullmatch("[A-Z]?[0-9]{5}", uid) is None:
        raise InvalidUIDProvided(uid)

    return uid
