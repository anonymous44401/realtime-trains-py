# Import external libraries
from datetime import datetime
from typing import Literal

# Import necessary items from other files
from realtime_trains_py.internal.boards import Boards
from realtime_trains_py.internal.details import DefaultBoard
from realtime_trains_py.internal.live_board import LiveBoard
from realtime_trains_py.internal.services import (
    ServiceData,
    ServiceDetails,
)
from realtime_trains_py.internal.utilities import check_token, complex_setup

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
        api_complexity = _COMPLEXITY_MAP[complexity]

        if api_complexity == "c":
            complex_setup()

        api_request_token = check_token(request_token=request_token)

        self.__services = ServiceDetails(
            api_request_token=api_request_token, complexity=api_complexity
        )
        self.__boards = Boards(
            api_request_token=api_request_token, complexity=api_complexity
        )
        self.__live_board = LiveBoard(
            api_request_token=api_request_token, request_token=request_token
        )

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
        return self.__boards._get_dep_board_details(
            tiploc=tiploc.upper(),
            filter_from=filter_from.upper(),
            filter_to=filter_to.upper(),
            date=date,
            rows=rows,
            time=time,
        )

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
        return self.__services._get_service_details(
            service_uid=service_uid.upper(), date=date
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
