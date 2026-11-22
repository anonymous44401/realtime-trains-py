# Import external libraries
from datetime import datetime as dt
from typing import Literal, Any

# Import necessary items from other files
from realtime_trains_py.async_files.async_live_board import AsyncLiveBoard
from realtime_trains_py.async_files.async_live_service import AsyncLiveService
from realtime_trains_py.internal.details import DefaultBoard, LookupData, ServiceData
from realtime_trains_py.internal.errors import (
    APIResponseError,
    NoDataFound,
)
from realtime_trains_py.internal.requests import (
    get_request,
    update_headers,
)
from realtime_trains_py.internal.utilities import (
    create_parameters,
    save_file,
    validate_date,
    validate_uid,
)
from realtime_trains_py.live.live_board import LiveBoard
from realtime_trains_py.live.live_service import LiveService
from realtime_trains_py.parsing.create_board import create_board
from realtime_trains_py.parsing.create_service import create_service_record
from realtime_trains_py.parsing.lookup import code_lookup, location_lookup, lookup_check

# Define the complexity and mode types, and their corresponding mappings to the API parameters
Complexity = Literal["simple", "advanced", "simple_normal", "complex", "complex_custom"]
Mode = Literal["DMI_yellow", "DMI_white", "LCD"]
_COMPLEXITY_MAP = {
    "simple": "s",
    "simple_normal": "a",
    "advanced": "a",
    "complex": "c",
    "complex_custom": "c",
}
_MODE_MAP = {"DMI_yellow": "DMI.Y", "DMI_white": "DMI.W", "LCD": "LCD"}


class RealtimeTrainsPy:
    def __init__(
        self,
        request_token: str,
        complexity: Complexity = "simple",
        folder: str | None = None,
    ) -> None:
        """
        :param str request_token: (Required) A string representing your request token for authentication.
        :param Literal["simple", "advanced", "simple_normal", "complex"] complexity: (Optional) A string representing your chosen complexity level.
        Choose from: `complex`, `simple`, `simple_normal` or `advanced`. If not provided, defaults to `simple`.
        :param str folder: (Optional) **Only available for complex mode** A string representing the folder you want the file saved in.

        ---
        ## Examples
        ```python
        rtt = RealtimeTrainsPy(request_token="<a_request_token>", complexity="simple")

        rtt = RealtimeTrainsPy(request_token="<a_request_token>", complexity="complex")
        ```

        [Check out the wiki for more examples and information](https://github.com/anonymous44401/realtime-trains-py/wiki) | [Join the discord](https://discord.gg/invite/Kv2FAn7SVf)
        """

        self._VERSION = "2027.2.2b2 [BETA] (B272220)"

        self.__headers = update_headers(request_token)

        self.__api_complexity = _COMPLEXITY_MAP[complexity]
        self.__folder = folder
        self.__request_token = request_token
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
        date_to: str | None = None,
        rows: int | None = None,
        time: str | None = None,
        time_to: str | None = None,
        raw: bool = False,
        detailed: bool = False,
        folder: str | None = None,
    ) -> DefaultBoard:
        """
        ## Get Departures
        This function retrieves the departures and arrivals for a given station.

        :param str tiploc: (Required) A string representing the Timing Point Location Code (TIPLOC) or Computer Reservation Code (CRS) of the station.
        :param str filter_from: (Optional) A string representing the Timing Point Location Code (TIPLOC) or Computer Reservation Code (CRS) of the originating station.
        :param str filter_to: (Optional) A string representing the Timing Point Location Code (TIPLOC) or Computer Reservation Code (CRS) of the destination station.
        :param str date: (Optional) A string representing the start date in the format YYYY-MM-DD.
        :param str date_to: (Optional) A string representing the end date in the format YYYY-MM-DD.
        :param int rows: (Optional) An integer representing the maximum number of rows to return. (Only available for simple and advanced/simple_normal complexity.)
        :param str time: (Optional) A string representing the start time in the formats HHMM or HH:MM.
        :param str time_to: (Optional) A string representing the end time in the formats HHMM or HH:MM.
        :param bool raw: (Optional) A boolean representing whether you want raw data.
        :param bool detailed: (Optional) A boolean representing whether you want detailed data. This functionality may be limited to your authorisation token.
        :param str folder: (Optional) **Only available for complex mode** A string representing the folder you want the file saved in.

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

        [Check out the wiki for more examples and information](https://github.com/anonymous44401/realtime-trains-py/wiki) | [Join the discord](https://discord.gg/invite/Kv2FAn7SVf)
        """
        params = create_parameters(
            tiploc, filter_from, filter_to, time, date, time_to, date_to, detailed
        )

        # Get the API response using the auth details provided
        api_response = get_request(
            "rtt/location", headers=self.__headers, params=params
        )

        if api_response.status_code == 401:
            # If code 401, retry request after updating headers (request token may have expired)
            self.__headers = update_headers(self.__request_token)

            api_response = get_request(
                "rtt/location", headers=self.__headers, params=params
            )

        if api_response.status_code == 200:
            service_data = api_response.json()

            if raw == True:
                return service_data

            elif self.__api_complexity == "c":
                # If complexity is c, save the JSON data to a new .json file using the save_file function
                save_file(
                    file_name=f"{tiploc.upper()}_on_{dt.now().strftime('%Y-%m-%d') if date is None else date}_board_data",
                    data=service_data,
                    local_folder=folder,
                    global_folder=self.__folder,
                )

                return DefaultBoard([], "")

            return create_board(service_data, rows, self.__api_complexity, detailed)

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
        folder: str | None = None,
    ) -> ServiceData:
        """
        ## Get Service
        This function retrieves the service information for a given service UID on a provided date.

        :param str service_uid: (Required) A string representing the Service Unique Identity (UID) code.
        :param str date: (Optional) A string representing the date in the format YYYY-MM-DD.
        :param bool raw: (Optional) A boolean representing whether you want raw data.
        :param bool detailed: (Optional) A boolean representing whether you want detailed data. This functionality may be limited to your authorisation token.
        :param str folder: (Optional) **Only available for complex mode** A string representing the folder you want the file saved in.

        ---
        ## Examples
        ```python
        get_service(service_uid="G54071", date="2024-11-16")

        get_service(service_uid="G26171")

        get_service(service_uid="G26171", raw=True)
        ```

        [Check out the wiki for more examples and information](https://github.com/anonymous44401/realtime-trains-py/wiki) | [Join the discord](https://discord.gg/invite/Kv2FAn7SVf)
        """

        params = {
            "uniqueIdentity": f"gb-nr:{validate_uid(service_uid)}:{validate_date(date)}",
            "detailed": f"{detailed}",
        }

        # Get the api response using the auth details provided
        api_response = get_request(
            "rtt/service",
            params=params,
            headers=self.__headers,
        )

        if api_response.status_code == 401:
            # If code 401, retry request after updating headers (request token may have expired)
            self.__headers = update_headers(self.__request_token)

            api_response = get_request(
                "rtt/service",
                params=params,
                headers=self.__headers,
            )

        if api_response.status_code == 200:
            service_data = api_response.json()["service"]

            if raw == True:
                return service_data

            elif self.__api_complexity == "c":
                # If complexity is c, save the JSON data to a new .json file using the save_file function
                save_file(
                    file_name=f"{service_uid}_on_{date}_service_data",
                    data=service_data,
                    local_folder=folder,
                    global_folder=self.__folder,
                )

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

        [Check out the wiki for more examples and information](https://github.com/anonymous44401/realtime-trains-py/wiki) | [Join the discord](https://discord.gg/invite/Kv2FAn7SVf)
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
        await rtt.get_live_async(tiploc="ELYY") # Live board for Ely

        await rtt.get_live_async(tiploc="PBRO", mode="DMI_yellow") # Live board for Peterborough, with mode set to DMI (Yellow)
        ```

        [Check out the wiki for more examples and information](https://github.com/anonymous44401/realtime-trains-py/wiki) | [Join the discord](https://discord.gg/invite/Kv2FAn7SVf)
        """

        await self.__async_live_board._get_live(
            tiploc=tiploc.upper(), mode=_MODE_MAP[mode], refresh=refresh
        )

    def watch_service(
        self, service_uid: str, mode: Mode = "LCD", refresh: int = 90
    ) -> None:
        """
        ## Watch Service

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

        [Check out the wiki for more examples and information](https://github.com/anonymous44401/realtime-trains-py/wiki) | [Join the discord](https://discord.gg/invite/Kv2FAn7SVf)
        """

        self.__live_service._watch_service(
            service_uid=validate_uid(service_uid), mode=_MODE_MAP[mode], refresh=refresh
        )

    async def watch_service_async(
        self, service_uid: str, mode: Mode = "LCD", refresh: int = 90
    ) -> None:
        """
        ## ASYNC Watch Service

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
        await rtt.watch_service_async(service_uid="G54071") # Watch G54071

        await rtt.watch_service_async(service_uid="G26171") # Watch G26171
        ```

        [Check out the wiki for more examples and information](https://github.com/anonymous44401/realtime-trains-py/wiki) | [Join the discord](https://discord.gg/invite/Kv2FAn7SVf)
        """

        await self.__async_live_service._watch_service(
            service_uid=validate_uid(service_uid), mode=_MODE_MAP[mode], refresh=refresh
        )

    def lookup(
        self,
        location: str | None = None,
        code: str | None = None,
        raw: bool = False,
        folder: str | None = None,
    ) -> list[LookupData] | bool | dict[str, Any]:
        """
        ## Lookup

        This function retrieves the CRS codes and/or TIPLOCs for a given location and retrieves the location for a given CRS code or TIPLOC.

        :param str location: (Optional) A string representing the lookup location.
        :param str code: (Optional) A string representing the lookup CRS code or TIPLOC.
        :param bool raw: (Optional) A boolean representing whether you want raw data.
        :param str folder: (Optional) **Only available for complex mode** A string representing the folder you want the file saved in.

        ---
        ## Examples
        ```python
        lookup(location="Stevenage") # Get an output of codes for Stevenage
        lookup(location="Stevenage", raw=True) # Get a list of LookupData objects returned

        lookup(code="SVG") # Get an output of locations for SVG
        lookup(code="SVG", raw=True) # Get a list of LookupData objects returned

        lookup() # Get all CRS and TIPLOCs saved to a new json file
        ```

        [Check out the wiki for more examples and information](https://github.com/anonymous44401/realtime-trains-py/wiki) | [Join the discord](https://discord.gg/invite/Kv2FAn7SVf)
        """

        # Send API request
        api_response = get_request(
            "data/locations_ungrouped",
            headers=self.__headers,
        )

        if api_response.status_code == 401:
            # If code 401, retry request after updating headers (request token may have expired)
            self.__headers = update_headers(self.__request_token)

            api_response = get_request(
                "data/locations_ungrouped",
                headers=self.__headers,
            )

        if api_response.status_code == 200:
            if raw and not location and not code:
                return api_response.json()

            elif code is None and location is None:
                # If a location and code weren't provided, save the JSON data to a new .json file using the save_file function
                save_file(
                    file_name=f"{dt.now().strftime('%Y-%m-%d')}_lookup_data",
                    data=api_response.json(),
                    local_folder=folder,
                    global_folder=self.__folder,
                )
                return [LookupData("", "")]

            elif location and code:
                return lookup_check(
                    code=code, location=location, data=api_response.json(), raw=raw
                )

            elif location is not None:
                return location_lookup(
                    location=location, data=api_response.json(), raw=raw
                )

            elif code is not None:
                return code_lookup(code=code, data=api_response.json(), raw=raw)

            return [LookupData("", "")]

        elif api_response.status_code == 404:
            raise NoDataFound()

        else:
            raise APIResponseError(
                f"Failed to connect to the RTT API server: {api_response.status_code} \nResponse message: {api_response.text}"
            )
