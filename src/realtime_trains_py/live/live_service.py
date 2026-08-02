# Import external libraries
import sys
import time
import requests

from datetime import datetime

# Import necessary items from other files
from realtime_trains_py.internal.details import ServiceData
from realtime_trains_py.internal.errors import AuthenticationError
from realtime_trains_py.internal.utilities import check_cancel, validate_uid, fmt
from realtime_trains_py.parsing.create_service import create_service_record


class LiveService:
    # Take the request token and the token to create a new request token when the old request token expires
    def __init__(self, headers: dict[str, str], request_token: str) -> None:
        self.__headers = headers
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

    def watch_service(self, service_uid: str, mode: str) -> None:
        # Output a helpful message to the user: Press Ctrl+C to close live departure board.
        sys.stdout.write(f"{fmt['grey']}Press Ctrl+C to stop watching this service.\n")
        time.sleep(2)

        # Set next update time to now (update instantly)
        next_update: int = int(time.time())

        validate_uid(service_uid)

        while True:
            # Update the board every 90 seconds
            if int(time.time()) == next_update:

                # Send API request
                response = self.__session.get(
                    "https://data.rtt.io/rtt/service",
                    params={
                        "uniqueIdentity": f"gb-nr:{service_uid}:{datetime.now().strftime('%Y-%m-%d')}"
                    },
                    headers=self.__headers,
                )

                if response.status_code == 200:
                    # Create the service record
                    service_record = create_service_record(
                        response.json()["service"], service_uid, "s.n"
                    )

                    # Clear the board and arrange the output
                    sys.stdout.write(
                        f"{fmt['clear']}{arrange_output(service=service_record)}"
                    )

                    # Add 90 to next update
                    next_update += 90

                elif response.status_code == 401:
                    # Check the request token and update the headers with the new token
                    self.__update_api_request_token()

                    next_update = int(time.time())

                # If no data is found, display a "Check timetable for services" message
                else:
                    # Clear the screen and output a message to the user to check the timetable for services
                    sys.stdout.write(
                        f"{fmt['clear']}{fmt['blue']}{service_uid}:\n {fmt['grey']}Check timetable for services\n"
                    )

                    next_update += 90

            # Display the current time at the bottom of the board and update it every second
            sys.stdout.write(
                f"{datetime.now().strftime('         %H:%M:%S')}{fmt['c_line']}"
            )
            time.sleep(1)


def arrange_output(service: ServiceData) -> str:
    # Set the initial line
    lines = f"{fmt['blue']}{service.service_uid}:{fmt['white']} {service.start_time} {service.origin} to {service.destination}\n  │\n"

    # Iterate over each calling point
    for calling_point in service.calling_points:

        # If the stop name isn't the desination, add the calling point line to the line
        if service.destination != calling_point.stop_name:
            lines += calling_point_line(
                calling_point.expected_departure,
                calling_point.scheduled_departure,
                calling_point.stop_name,
                calling_point.platform,
            )

        # If the stop name is the destination, add the final calling point to the line
        else:
            lines += final_calling_point(
                calling_point.expected_arrival,
                calling_point.scheduled_arrival,
                calling_point.stop_name,
                calling_point.platform,
            )

    # Add the operator to the lines
    lines += f"{fmt['white']}Operated by {fmt['blue']}{service.operator} {fmt['white']}"

    # If there is a number of coaches, add this information to the lines
    if service.coaches != 0:
        lines += f"\nFormed of {service.coaches} coaches."

    return lines + "\n\n"


def final_calling_point(exp_dep: str, sch_dep: str, stop: str, platform: str):
    # Check if the calling point is cancelled
    exp_dep = check_cancel(exp_dep)

    # If the calling point is cancelled, strike through the scheduled arrival time and display the expected arrival time in red.
    # Otherwise, display the scheduled arrival time in green.
    if "Exp" in exp_dep or "Cancelled" in exp_dep:
        #   ╰─ 10:30 Cancelled Stevenage P3
        return f"  {fmt['white']}╰─ {fmt['grey']}{fmt['s_strike']}{sch_dep}{fmt['e_strike']} {exp_dep}{fmt['white']} {stop} {f"P{platform}" if platform != "-" else ""} \n\n"

    else:
        #   ╰─ 10:30 Stevenage P3
        return f"  {fmt['white']}╰─ {fmt['green']}{sch_dep}{fmt['white']} {stop} {f"P{platform}" if platform != "-" else ""} \n\n"


def calling_point_line(exp_arr: str, sch_arr: str, stop: str, platform: str):
    # Check if the calling point is cancelled
    exp_arr = check_cancel(exp_arr)

    # If the calling point is cancelled, strike through the scheduled arrival time and display the expected arrival time in red.
    # Otherwise, display the scheduled arrival time in green.
    if "Exp" in exp_arr or "Cancelled" in exp_arr:
        #   ├─ 10:30 Cancelled Stevenage P3
        #   │
        return f"  {fmt['white']}├─ {fmt['grey']}{fmt['s_strike']}{sch_arr}{fmt['e_strike']} {exp_arr}{fmt['white']} {stop} {f"P{platform}" if platform != "-" else ""} \n  │\n"

    else:
        #   ├─ 10:30 Stevenage P3
        #   │
        return f"  {fmt['white']}├─ {fmt['green']}{sch_arr}{fmt['white']} {stop} {f"P{platform}" if platform != "-" else ""} \n  │\n"
