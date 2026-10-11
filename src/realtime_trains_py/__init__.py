# Import external libraries
import os
import requests

from datetime import datetime as dt
from typing import Literal

# Import necessary items from other files
from realtime_trains_py.async_files.async_live_board import AsyncLiveBoard
from realtime_trains_py.async_files.async_live_service import AsyncLiveService
from realtime_trains_py.internal.details import DefaultBoard, ServiceData
from realtime_trains_py.internal.errors import (
    APIResponseError,
    TooManyArguments,
    NoDataFound,
)
from realtime_trains_py.live.live_board import LiveBoard
from realtime_trains_py.live.live_service import LiveService
from realtime_trains_py.internal.utilities import (
    check_token,
    create_file,
    create_parameters,
    validate_date,
    validate_uid,
)
from realtime_trains_py.parsing.create_board import create_board
from realtime_trains_py.parsing.create_service import create_service_record
from realtime_trains_py.parsing.lookup import location_lookup, code_lookup

# Define the complexity and mode types, and their corresponding mappings to the API parameters
Complexity = Literal["simple", "simple_normal", "complex", "complex_custom"]
Mode = Literal["DMI_yellow", "DMI_white", "LCD"]
_COMPLEXITY_MAP = {
    "simple": "s",
    "simple_normal": "s.n",
    "complex": "c",
    "complex_custom": "c.c",
}
_MODE_MAP = {"DMI_yellow": "DMI.Y", "DMI_white": "DMI.W", "LCD": "LCD"}


class RealtimeTrainsPy:
    def __init__(
        self, request_token: str, complexity: Complexity = "simple", folder: str = ""
    ) -> None:
        """
        :param str request_token: (Required) A string representing your request token for authentication.
        :param complexity: (Optional) A string representing your chosen complexity level.
        Choose from: `complex`, `complex_custom`, `simple` or `simple_normal`. If not provided, defaults to `simple`.
        :param str folder: (Optional) **Only available for complex (custom) mode** A string representing the folder you want the file saved in.

        ---
        ## Examples
        ```python
        rtt = RealtimeTrainsPy(request_token="<a_request_token>", complexity="simple")

        rtt = RealtimeTrainsPy(request_token="<a_request_token>", complexity="complex")
        ```

        [Check out the wiki for more examples and information.](https://github.com/anonymous44401/realtime-trains-py/wiki) | [Join the discord](https://discord.gg/invite/Kv2FAn7SVf)
        """

        self.__api_complexity = _COMPLEXITY_MAP[complexity]
        self.__folder = folder

        if self.__api_complexity == "c":
            # Check if realtime_trains_py_data folder exists and create it if not
            if not os.path.isdir("realtime_trains_py_data"):
                os.mkdir("realtime_trains_py_data")

        self.__headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {check_token(request_token=request_token)}",
        }

        self.__live_board = LiveBoard(self.__headers, request_token)
        self.__async_live_board = AsyncLiveBoard(self.__headers, request_token)
        self.__live_service = LiveService(self.__headers, request_token)
        self.__async_live_service = AsyncLiveService(self.__headers, request_token)

    def get_departures(
        self,
        tiploc: str,
        filter_from: str | None = None,
        filter_to: str | None = None,
        date: str | None = None,
        rows: int | None = None,
        time: str | None = None,
        raw: bool = False,
        detailed: bool = False,
        folder: str = "",
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
        :param bool raw: (Optional) A boolean representing whether you want raw data.
        :param bool detailed: (Optional) A boolean representing whether you want detailed data. This functionality may be limited to your authorisation token.
        :param str folder: (Optional) **Only available for complex (custom) mode** A string representing the folder you want the file saved in.

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

        [Check out the wiki for more examples and information.](https://github.com/anonymous44401/realtime-trains-py/wiki) | [Join the discord](https://discord.gg/invite/Kv2FAn7SVf)
        """

        # Get the API response using the auth details provided
        api_response = requests.get(
            "https://data.rtt.io/rtt/location",
            headers=self.__headers,
            params=create_parameters(
                tiploc, filter_from, filter_to, time, date, detailed
            ),
        )

        if api_response.status_code == 200:
            service_data = api_response.json()

            if raw == True:
                return service_data

            elif self.__api_complexity == "c":
                # If complexity is c, save the JSON data to a new .json file in the realtime_trains_py_data folder using the create_file
                # function and return an empty DefaultBoard data class since the data is saved to a file and not returned as a data class object
                create_file(
                    f"realtime_trains_py_data/{tiploc.upper()}_on_{dt.now().strftime('%Y-%m-%d') if date is None else date}_board_data",
                    service_data,
                )

                return DefaultBoard([], "")

            elif self.__api_complexity == "c.c":
                # If complexity is c.c, save the JSON data to a new .json file using the create_file
                # function and return an empty DefaultBoard data class since the data is saved to a file and not returned as a data class object
                file = f"{tiploc.upper()}_on_{dt.now().strftime('%Y-%m-%d') if date is None else date}_board_data"

                if folder != "":
                    file = f"{folder}/{file}"

                elif self.__folder != "":
                    file = f"{self.__folder}/{file}"

                create_file(file, service_data)

                return DefaultBoard([], "")

            return create_board(service_data, rows, self.__api_complexity)

        elif api_response.status_code == 404:
            raise NoDataFound()

        else:
            raise APIResponseError(
                f"Failed to connect to the RTT API server: {api_response.status_code} \nResponse message: {api_response.text}"
            )

    def get_service(
        self,
        service_uid: str,
        date: str = dt.now().strftime("%Y-%m-%d"),
        raw: bool = False,
        detailed: bool = False,
        folder: str = "",
    ) -> ServiceData:
        """
        ## Get Service
        This function retrieves the service information for a given service UID on a provided date.

        :param str service_uid: (Required) A string representing the Service Unique Identity (UID) code.
        :param str date: (Optional) A string representing the date in the format YYYY-MM-DD.
        :param bool raw: (Optional) A boolean representing whether you want raw data.
        :param bool detailed: (Optional) A boolean representing whether you want detailed data. This functionality may be limited to your authorisation token.
        :param str folder: (Optional) **Only available for complex (custom) mode** A string representing the folder you want the file saved in.

        ---
        ## Examples
        ```python
        get_service(service_uid="G54071", date="2024-11-16")

        get_service(service_uid="G26171")

        get_service(service_uid="G26171", raw=True)
        ```

        [Check out the wiki for more examples and information.](https://github.com/anonymous44401/realtime-trains-py/wiki) | [Join the discord](https://discord.gg/invite/Kv2FAn7SVf)
        """

        validate_uid(service_uid)

        # Get the api response using the auth details provided
        api_response = requests.get(
            "https://data.rtt.io/rtt/service",
            params={
                "uniqueIdentity": f"gb-nr:{service_uid}:{validate_date(date)}",
                "detailed": f"{detailed}",
            },
            headers=self.__headers,
        )

        if api_response.status_code == 200:
            service_data = api_response.json()["service"]

            if raw == True:
                return service_data

            elif self.__api_complexity == "c":
                # Create a new file
                create_file(
                    f"realtime_trains_py_data/{service_uid}_on_{date}_service_data",
                    service_data,
                )

                # Return an empty ServiceData data class since the data is saved to a file and not returned as an object
                return ServiceData("", "", "", "", [], "", "", 0)

            elif self.__api_complexity == "c.c":
                # Create a new file
                file = f"{service_uid}_on_{date}_service_data"

                if folder != "":
                    file = f"{folder}/{file}"

                elif self.__folder != "":
                    file = f"{self.__folder}/{file}"

                create_file(file, service_data)

                # Return an empty ServiceData data class since the data is saved to a file and not returned as an object
                return ServiceData("", "", "", "", [], "", "", 0)

            return create_service_record(
                service_data, service_uid, self.__api_complexity
            )

        elif api_response.status_code == 404:
            raise NoDataFound()

        else:
            raise APIResponseError(
                f"Failed to connect to the RTT API server: {api_response.status_code} \nResponse message: {api_response.text}"
            )

    def get_live(self, tiploc: str, mode: Mode = "LCD", refresh: int = 90) -> None:
        """
        ## Get Live
        This function retrieves the live departure board for a given station. The board is updated every 90 seconds.
        To exit the board, press Ctrl + C.

        :param str tiploc: (Required) A string representing the Timing Point Location Code (TIPLOC) or Computer Reservation Code (CRS) of the station.
        :param Mode mode: (Optional) A string representing the mode of the live board.
        Choose from: `DMI_yellow`, `DMI_white` or `LCD`. If not provided, the default is `LCD`.
        :param int refresh: (Optional) An integer representing your custom refresh time. If not provided, the default is 90.

        _The recommended refresh time is 90 seconds to prevent API overuse and being rate limited. Using a refresh time that is less than 90 is done at your own risk._

        ---
        ## Examples
        ```python
        get_live(tiploc="ELYY") # Live board for Ely

        get_live(tiploc="PBRO", mode="DMI_yellow") # Live board for Peterborough, with mode set to DMI (Yellow)
        ```

        [Check out the wiki for more examples and information.](https://github.com/anonymous44401/realtime-trains-py/wiki) | [Join the discord](https://discord.gg/invite/Kv2FAn7SVf)
        """

        self.__live_board._get_live(
            tiploc=tiploc.upper(), mode=_MODE_MAP[mode], refresh=refresh
        )

    async def get_live_async(
        self, tiploc: str, mode: Mode = "LCD", refresh: int = 90
    ) -> None:
        """
        ## ASYNC Get Live
        This function retrieves the live departure board for a given station. The board is updated every 90 seconds.
        To exit the board, press Ctrl + C.

        :param str tiploc: (Required) A string representing the Timing Point Location Code (TIPLOC) or Computer Reservation Code (CRS) of the station.
        :param Mode mode: (Optional) A string representing the mode of the live board.
        Choose from: `DMI_yellow`, `DMI_white` or `LCD`. If not provided, the default is `LCD`.
        :param int refresh: (Optional) An integer representing your custom refresh time. If not provided, the default is 90.

        _The recommended refresh time is 90 seconds to prevent API overuse and being rate limited. Using a refresh time that is less than 90 is done at your own risk._

        ---
        ## Examples
        ```python
        get_live(tiploc="ELYY") # Live board for Ely

        get_live(tiploc="PBRO", mode="DMI_yellow") # Live board for Peterborough, with mode set to DMI (Yellow)
        ```

        [Check out the wiki for more examples and information.](https://github.com/anonymous44401/realtime-trains-py/wiki) | [Join the discord](https://discord.gg/invite/Kv2FAn7SVf)
        """

        await self.__async_live_board._get_live(
            tiploc=tiploc.upper(), mode=_MODE_MAP[mode], refresh=refresh
        )

    def watch_service(
        self, service_uid: str, mode: Mode = "LCD", refresh: int = 90
    ) -> None:
        """
        ## Watch Service

        ### NEW for version 2027.2.0

        This function retrieves the service information for a given service UID on a provided date. The service information is updated every 90 seconds.
        To stop watching the service, press Ctrl + C.

        :param str service_uid: (Required) A string representing the Service Unique Identity (UID) code.
        :param Mode mode: (Optional) A string representing the mode of the live board.
        Choose from: `DMI_yellow`, `DMI_white` or `LCD`. If not provided, the default is `LCD`.
        :param int refresh: (Optional) An integer representing your custom refresh time. If not provided, the default is 90.

        _The recommended refresh time is 90 seconds to prevent API overuse and being rate limited. Using a refresh time that is less than 90 is done at your own risk._

        ---
        ## Examples
        ```python
        watch_service(service_uid="G54071") # Watch G54071

        watch_service(service_uid="G26171") # Watch G26171
        ```

        [Check out the wiki for more examples and information.](https://github.com/anonymous44401/realtime-trains-py/wiki) | [Join the discord](https://discord.gg/invite/Kv2FAn7SVf)
        """

        self.__live_service.watch_service(
            service_uid=service_uid, mode=_MODE_MAP[mode], refresh=refresh
        )

    async def watch_service_async(
        self, service_uid: str, mode: Mode = "LCD", refresh: int = 90
    ) -> None:
        """
        ## ASYNC Watch Service

        ### NEW for version 2027.2.0

        This function retrieves the service information for a given service UID on a provided date. The service information is updated every 90 seconds.
        To stop watching the service, press Ctrl + C.

        :param str service_uid: (Required) A string representing the Service Unique Identity (UID) code.
        :param Mode mode: (Optional) A string representing the mode of the live board.
        Choose from: `DMI_yellow`, `DMI_white` or `LCD`. If not provided, the default is `LCD`.
        :param int refresh: (Optional) An integer representing your custom refresh time. If not provided, the default is 90.

        _The recommended refresh time is 90 seconds to prevent API overuse and being rate limited. Using a refresh time that is less than 90 is done at your own risk._

        ---
        ## Examples
        ```python
        watch_service(service_uid="G54071") # Watch G54071

        watch_service(service_uid="G26171") # Watch G26171
        ```

        [Check out the wiki for more examples and information.](https://github.com/anonymous44401/realtime-trains-py/wiki) | [Join the discord](https://discord.gg/invite/Kv2FAn7SVf)
        """

        await self.__async_live_service.watch_service(
            service_uid=service_uid, mode=_MODE_MAP[mode], refresh=refresh
        )

    def lookup(
        self,
        location: str | None = None,
        code: str | None = None,
    ) -> None:
        """
        ## Lookup

        ### NEW for version 2027.2.0

        This function retrieves the CRS and/or TIPLOC codes for a given location.

        :param str location: (Optional) A string representing the lookup location.
        :param str code: (Optional) A string representing the lookup CRS code or TIPLOC.

        ---
        ## Examples
        ```python
        lookup(location="Stevenage")

        lookup(code="SVG")

        lookup() # Get all CRS and TIPLOCs saved to a new .json file
        ```

        [Check out the wiki for more examples and information.](https://github.com/anonymous44401/realtime-trains-py/wiki) | [Join the discord](https://discord.gg/invite/Kv2FAn7SVf)
        """

        # Send API request
        api_response = requests.get(
            "https://data.rtt.io/data/locations_ungrouped",
            headers=self.__headers,
        )

        # Set raw to false if a location is given. Otherwise set raw to true
        if location is not None and code is not None:
            raise TooManyArguments(
                f" Method: 'lookup' only takes one argument. Remove one of: \n - Code: '{code}' \n - Location: '{location}'."
            )

        elif (location is not None and code is None) or (
            code is not None and location is None
        ):
            raw = False

        else:
            raw = True

        if api_response.status_code == 200:
            if raw == True:
                return api_response.json()

            elif location is not None:
                location_lookup(location=location, data=api_response.json())

            elif code is not None:
                code_lookup(code=code, data=api_response.json())

            return

        elif api_response.status_code == 404:
            raise NoDataFound()

        else:
            raise APIResponseError(
                f"Failed to connect to the RTT API server: {api_response.status_code} \nResponse message: {api_response.text}"
            )
