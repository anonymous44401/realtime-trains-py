# Import external libraries
import os

import requests

from datetime import datetime
from typing import Literal

from tabulate import tabulate

# Import necessary items from other files
from realtime_trains_py.internal.details import DefaultBoard, ServiceData
from realtime_trains_py.internal.errors import APIResponseError, NoDataFound
from realtime_trains_py.live.live_board import LiveBoard

from realtime_trains_py.internal.utilities import check_token, create_file, create_parameters, validate_date, validate_uid

from realtime_trains_py.parsing.create_board import create_board
from realtime_trains_py.parsing.create_service import create_service_record

# Define the complexity and mode types, and their corresponding mappings to the API parameters
Complexity = Literal["simple", "simple_normal", "complex"]
Mode = Literal["DMI_yellow", "DMI_white", "LCD"]
_COMPLEXITY_MAP = {"simple": "s", "simple_normal": "s.n", "complex": "c"}
_MODE_MAP = {"DMI_yellow": "DMI.Y", "DMI_white": "DMI.W", "LCD": "LCD"}


class RealtimeTrainsPy:
    def __init__(self, request_token: str, complexity: Complexity = "simple") -> None:
        """
        :param str request_token: (Required) A string representing your request token for authentication.
        :param complexity: (Optional) A string representing your chosen complexity level.
        Choose from: `complex`, `simple` or `simple_normal`. If not provided, defaults to `simple`.

        ---
        ## Examples
        ```python
        rtt = RealtimeTrainsPy(request_token="<a_request_token>", complexity="simple")

        rtt = RealtimeTrainsPy(request_token="<a_request_token>", complexity="complex")
        ```

        [Check out the wiki for more examples and information.](https://github.com/anonymous44401/realtime-trains-py/wiki)
        """
        self.__api_complexity = _COMPLEXITY_MAP[complexity]

        if self.__api_complexity == "c":
            # Check if realtime_trains_py_data folder exists and create it if not
            if not os.path.isdir("realtime_trains_py_data"):
                os.mkdir("realtime_trains_py_data")

        self.__headers = {
            "Accept": "application/json", 
            "Authorization": f"Bearer {check_token(request_token=request_token)}"
        }

        self.__live_board = LiveBoard(self.__headers, request_token)

    def get_departures(
        self,
        tiploc: str,
        filter_from: str | None = None,
        filter_to: str | None = None,
        date: str | None = None,
        rows: int | None = None,
        time: str | None = None,
    ) -> DefaultBoard:
        """
        ## Get Departures
        This function retrieves the departures and arrivals for a given station.

        :param str tiploc: (Required) A string representing the Timing Point Location Code (TIPLOC) or Computer Reservation Code (CRS) of the station.
        :param str filter_from: (Optional) A string representing the Timing Point Location Code (TIPLOC) or Computer Reservation Code (CRS) of the originating station.
        :param str filter_to: (Optional) A string representing the Timing Point Location Code (TIPLOC) or Computer Reservation Code (CRS) of the destination station.
        :param str date: (Optional) A string representing the date in the format YYYY-MM-DD.
        :param int rows: (Optional) An integer representing the maximum number of rows to return. (Only available for simple complexity.)
        :param str time: (Optional) A string representing the time in the formats HHMM or HH:MM.

        ---
        ## Examples
        ```python
        get_departures(
            tiploc="KNGX",
            filter_from="STEVNGE",
            filter_to="PBRO",
            date="2024-11-16",
            time="1800",
            rows=10
        )

        get_departures(tiploc="YORK", date="2024-11-16", time="1800")
        ```

        [Check out the wiki for more examples and information.](https://github.com/anonymous44401/realtime-trains-py/wiki)
        """
        # Get the API response using the auth details provided
        api_response = requests.get(
            "https://data.rtt.io/rtt/location",
            headers=self.__headers,
            params=create_parameters(tiploc, filter_from, filter_to, time, date),
        )

        if api_response.status_code == 200:
            service_data = api_response.json()

            if self.__api_complexity == "c":
                # If complexity is c, save the JSON data to a new .json file in the realtime_trains_py_data folder using the create_file
                # function and return an empty DefaultBoard data class since the data is saved to a file and not returned as a data class object
                create_file(
                    f"{tiploc.upper()}_on_{datetime.now().strftime('%Y-%m-%d') if date is None else date}_board_data",
                    service_data,
                )

                return DefaultBoard([], "")

            return create_board(service_data, rows, self.__api_complexity)
            
        elif api_response.status_code == 404:
            raise NoDataFound()

        else:
            raise APIResponseError(f"Failed to connect to the RTT API server: {api_response.status_code} \nResponse message: {api_response.text}")


    def get_service(
        self, service_uid: str, date: str = datetime.now().strftime("%Y-%m-%d")
    ) -> ServiceData:
        """
        ## Get Service
        This function retrieves the service information for a given service UID on a provided date.

        :param str service_uid: (Required) A string representing the Service Unique Identity (UID) code.
        :param str date: (Optional) A string representing the date in the format YYYY-MM-DD.

        ---
        ## Examples
        ```python
        get_service(service_uid="G54071", date="2024-11-16")

        get_service(service_uid="G26171")
        ```

        [Check out the wiki for more examples and information.](https://github.com/anonymous44401/realtime-trains-py/wiki)
        """
        validate_uid(service_uid)

        validate_date(date)

        # Get the api response using the auth details provided
        api_response = requests.get(
            "https://data.rtt.io/rtt/service",
            params={"uniqueIdentity": f"gb-nr:{service_uid}:{date}"},
            headers=self.__headers,
        )

        if api_response.status_code == 200:
            service_data = api_response.json()["service"]

            if self.__api_complexity == "c":
                # Create a new file
                create_file(f"{service_uid}_on_{date}_service_data", service_data)

                # Return an empty ServiceData data class since the data is saved to a file and not returned as an object
                return ServiceData("", "", "", "", [], "", "", 0)

            return create_service_record(service_data, service_uid, self.__api_complexity)

        elif api_response.status_code == 404:
            raise NoDataFound()

        else:
            raise APIResponseError(
                f"Failed to connect to the RTT API server: {api_response.status_code} \nResponse message: {api_response.text}"
            )

    def get_live(self, tiploc: str, mode: Mode = "LCD") -> None:
        """
        ## Get Live
        This function retrieves the live departure board for a given station. The board is updated every 60 seconds, on the minute.
        To exit the board, press Ctrl + C.

        :param str tiploc: (Required) A string representing the Timing Point Location Code (TIPLOC) or Computer Reservation Code (CRS) of the station.
        :param Mode mode: (Optional) A string representing the mode of the live board.
        Choose from: `DMI_yellow`, `DMI_white` or `LCD`. If not provided, the default is `LCD`.

        ---
        ## Examples
        ```python
        get_live(tiploc="ELYY") # Live board for Ely

        get_live(tiploc="PBRO", mode="DMI_yellow") # Live board for Peterborough, with mode set to DMI (Yellow)
        ```

        [Check out the wiki for more examples and information.](https://github.com/anonymous44401/realtime-trains-py/wiki)
        """
        self.__live_board._get_live(tiploc=tiploc.upper(), mode=_MODE_MAP[mode])

    def watch_service(self, service_uid: str, mode: Mode = "LCD") -> None:
        """
        ## Watch Service

        # NOT AVAILABLE (YET)

        This function retrieves the service information for a given service UID on a provided date. The service information is updated every 60 seconds, on the minute.
        To stop watching the service, press Ctrl + C.

        :param str service_uid: (Required) A string representing the Service Unique Identity (UID) code.
        :param Mode mode: (Optional) A string representing the mode of the live board.
        Choose from: `DMI_yellow`, `DMI_white` or `LCD`. If not provided, the default is `LCD`.

        ---
        ## Examples
        ```python
        watch_service(service_uid="G54071", mode="DMI_yellow")

        watch_service(service_uid="G26171")
        ```

        [Check out the wiki for more examples and information.](https://github.com/anonymous44401/realtime-trains-py/wiki)
        """
        raise NotImplementedError(
            "Calm down, eager beaver! This method is not implemented yet."
        )
