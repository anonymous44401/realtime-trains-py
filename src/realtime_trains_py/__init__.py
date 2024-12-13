try:
    from realtime_trains_py.services.service_data import ServiceDetails
    from realtime_trains_py.services.board_data import Boards
except:
    from services.service_data import ServiceDetails
    from services.board_data import Boards


class RealtimeTrainsPy():
    def __init__(self, complexity = "s", username: str = None, password: str = None) -> None: 
        """
        ## Initialize realtime_trains_py.
        **complexity** *(optional)*
            A string representing the complexity level of the data. The default is "s".
        
        **username** *(required)*
            A string representing the username for authentication.

        **password** *(required)*
            A string representing the password for authentication.

        ## Example
        ```python
        rtt = RealtimeTrainsPy(complexity = "s", username = "your_username", password = "your_password")
        ```
        """
        if username == None or password == None:
            raise ValueError("Missing details. Both username and password must be provided. Not all required fields were provided.")

        else:
            self._username = username
            self.__password = password
            if complexity.lower() not in ["s", "s.p", "s.n", "a", "a.p", "a.n", "c"]:
                raise ValueError("Complexity not recognised. Select a valid type.")
        
        self.__services = ServiceDetails(username = self._username, password = self.__password, complexity = complexity.lower())
        self.__boards = Boards(username = self._username, password = self.__password, complexity = complexity)

    def get_departures(self, tiploc: str, filter: str = None, date: str = None, rows: int = None, time: str = None) -> list | str:
        """
        ### Parameters
        **tiploc** *(required)*

            A string representing the Timing Point Location Code (TIPLOC) or Computer Reservation Code (CRS) of the station.

        **filter** *(optional)*
            A string representing the Timing Point Location Code (TIPLOC) or Computer Reservation Code (CRS) of the filter station.

        **date** *(optional)*
            A string representing the date in the format YYYY/MM/DD.

        **rows** *(optional)*
            An integer representing the maximum number of rows to return. (Only available for simple and advanced complexity.)

        **time** *(optional)*
            A string representing the time in the format HHMM. 


        ### Example data
        ```python
        get_departures(tiploc = "KNGX", filter = "STEVNGE", date = "2024/11/16", time = "1800", rows = 10)
        ```
        """
        return self.__boards._get_dep_board_details(tiploc = tiploc, filter = filter, date = date, rows = rows, time = time)
    

    def get_arrivals(self, tiploc: str, filter: str = None, date: str = None, rows: int = None, time: str = None) -> list | str:
        """
        **tiploc** *(required)*

            A string representing the Timing Point Location Code (TIPLOC) or Computer Reservation Code (CRS) of the station.

        **filter** *(optional)*
            A string representing the Timing Point Location Code (TIPLOC) or Computer Reservation Code (CRS) of the filter station.

        **date** *(optional)*
            A string representing the date in the format YYYY/MM/DD.

        **rows** *(optional)*
            An integer representing the maximum number of rows to return. (Only available for simple and advanced complexity.)

        **time** *(optional)*
            A string representing the time in the format HHMM. 

        ### Example data
        ```python
        get_arrivals(tiploc = "KNGX", filter = "STEVNGE", date = "2024/11/16", time = "1800", rows = 10)
        ```
        """
        return self.__boards._get_arr_board_details(tiploc = tiploc, filter = filter, date = date, rows = rows, time = time)

    def get_service(self, service_uid: str, date: str = None) -> list | str:
        """
        **service_uid** *(required)*
            A string representing the Service Unique Identity (UID) code.

        **date** *(optional)*
            A string representing the date in the format YYYY/MM/DD.

        **time** *(optional)*
            A string representing the time in the format HHMM. 

        ### Example data
        ```python
        get_service(service_uid = "G54071", date = "2024/11/16", time = "1800")
        ```
        """
        return self.__services._get_service_details(service_uid = service_uid, date = date)
    
    def get_station(self, tiploc: str, filter: str = None, date: str = None, rows: int = None, time: str = None) -> list | str:
        """
        Docs soon
        """
        return self.__boards._get_stat_board_details(tiploc = tiploc, filter = filter, date = date, rows = rows, time = time)