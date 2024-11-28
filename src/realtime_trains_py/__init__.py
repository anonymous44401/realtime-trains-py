from services.boardData import Boards
from services.serviceData import Service, ServiceDetails


class RealtimeTrainsPy():
    def __init__(self, complexity = "s", username: str = None, password: str = None) -> None: 
        if username == None or password == None:
            raise ValueError("Missing details. Both username and password must be provided. Not all required fields were provided.")

        else:
            self._username = username
            self.__password = password
            if complexity not in ["s", "a", "c"]:
                raise ValueError("Complexity not recognised. Select a valid type.")
        
        self.__services = ServiceDetails(username = self._username, password = self.__password, complexity = complexity)
        self.__boards = Boards(username = self._username, password = self.__password, complexity = complexity)

    def get_departures(self, tiploc: str, filter: str = None, date: str = None, rows: int = None, time: str = None) -> list | str:
        """
        **tiploc** *(mandatory)*
            A string representing the Timing Point Location Code (TIPLOC) or Computer Reservation Code (CRS) of the station.

        **filter** *(optional)*
            A string representing the Timing Point Location Code (TIPLOC) or Computer Reservation Code (CRS) of the filter station.

        **date** *(optional)*
            A string representing the date in the format YYYY/MM/DD.

        **rows** *(optional)*
            An integer representing the maximum number of rows to return. (Only available for simple and advanced complexity.)

        **time** *(optional)*
            A string representing the time in the format HHMM. 
        """
        data = self.__boards._get_dep_board_details(tiploc = tiploc, filter = filter, date = date, rows = rows, time = time)

        return data

    def get_arrivals(self, tiploc: str, filter: str = None, date: str = None, rows: int = None, time: str = None) -> list | str:
        """
        **tiploc** *(mandatory)*
            A string representing the Timing Point Location Code (TIPLOC) or Computer Reservation Code (CRS) of the station.

        **filter** *(optional)*
            A string representing the Timing Point Location Code (TIPLOC) or Computer Reservation Code (CRS) of the filter station.

        **date** *(optional)*
            A string representing the date in the format YYYY/MM/DD.

        **rows** *(optional)*
            An integer representing the maximum number of rows to return. (Only available for simple and advanced complexity.)

        **time** *(optional)*
            A string representing the time in the format HHMM. 
        """
        data = self.__boards._get_arr_board_details(tiploc = tiploc, filter = filter, date = date, rows = rows, time = time)

        return data

    def get_service(self, service_uid: str, date: str = None, time: str = None) -> Service:
        """
        **service_uid** *(mandatory)*
            A string representing the Service Unique Identity (UID) code.

        **date** *(optional)*
            A string representing the date in the format YYYY/MM/DD.

        **time** *(optional)*
            A string representing the time in the format HHMM. 
        """
        data = self.__services._get_service_details(service_uid = service_uid, date = date, time = time)

        return data