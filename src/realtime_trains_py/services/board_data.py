from datetime import datetime
try:
    from realtime_trains_py.services.utilities import format_time, validate_date, validate_time 
except:
    from services.utilities import create_file, format_time, validate_date, validate_time 
from tabulate import tabulate

import requests


class DepartureBoardSimple():
    def __init__(self, gbtt_departure, terminus, platform, realtime_departure, service_uid):
        self.gbtt_departure = gbtt_departure
        self.terminus = terminus
        self.platform = platform
        self.realtime_departure = realtime_departure
        self.service_uid = service_uid

class ArrivalBoardSimple():
    def __init__(self, gbtt_arrival, terminus, origin, platform, realtime_arrival, service_uid):
        self.gbtt_arrival = gbtt_arrival
        self.terminus = terminus
        self.origin = origin
        self.platform = platform
        self.realtime_arrival = realtime_arrival
        self.service_uid = service_uid

class DepartureBoardAdvanced():
    def __init__(self, gbtt_departure, terminus, platform, realtime_departure, service_uid):
        self.gbtt_departure = gbtt_departure
        self.terminus = terminus
        self.platform = platform
        self.realtime_departure = realtime_departure
        self.service_uid = service_uid

class ArrivalBoardAdvanced():
    def __init__(self, gbtt_arrival, terminus, origin, platform, realtime_arrival, service_uid):
        self.gbtt_arrival = gbtt_arrival
        self.terminus = terminus
        self.origin = origin
        self.platform = platform
        self.realtime_arrival = realtime_arrival
        self.service_uid = service_uid


class Boards():
    def __init__(self, username: str = None, password: str = None, complexity: str = "s") -> None:
        self.__username = username
        self.__password = password
        self.__complexity = complexity

        self._board_url: str = "https://api.rtt.io/api/v1/json/search/"

    def _get_dep_board_details(self, tiploc, filter, rows, time, date: str = None) -> list | str:
        if date is None:
            new_date = (datetime.now()).strftime("%Y/%m/%d")

        else:
            new_date = date

        if time is None:
            new_time = (datetime.now()).strftime("%H%M")

        else:
            new_time = time

        if self.__complexity == "c" or (validate_date(new_date) and validate_time(new_time)):

            # https://api.rtt.io/api/v1/json/search/SDY/to/SVG
            
            search_query = "https://api.rtt.io/api/v1/json/search/" + str(tiploc)

            if filter is not None:
                search_query += "/to/" + str(filter)

            if date is not None:
                search_query +=  "/" + str(date)

            if time is not None:
                search_query += "/" + str(time)

            # print(search_query)
            api_response =  requests.get(search_query, auth = (self.__username, self.__password))

            if api_response.status_code == 200:
                service_data = api_response.json()

                # print(service_data["services"])

                if service_data["services"] == None:
                    raise ValueError("No data found.")

                if self.__complexity == "c":
                    split_date = new_date.split("/")
                    file_name = tiploc + "_on_" + split_date[0] + "." + split_date[1] + "." + split_date[2] + "_dep_board_data"

                    return create_file(file_name, service_data)
                
                elif self.__complexity == "a.p" or self.__complexity == "a":
                    departure_board: list = []
                    
                    services = service_data["services"]
                    requested_location = service_data["location"]["name"]
                    count = 0

                    for service in services:
                        location_detail = service["locationDetail"]
                        destination = location_detail["destination"]
                        status = location_detail["displayAs"]


                        if "gbttBookedDeparture" in location_detail:
                            gbtt_departure = location_detail["gbttBookedDeparture"]

                        else:
                            gbtt_departure = "Unknown"

                        if "platform" in location_detail:
                            platform = location_detail["platform"]

                        else:
                            platform = "Unknown"

                        if "realtimeDeparture" in location_detail:
                            realtime_departure = location_detail["realtimeDeparture"]

                        else:
                            realtime_departure = "Unknown"

                        if "serviceUid" in service:
                            service_uid = service["serviceUid"]

                        else:
                            service_uid = "Unknown"


                        if status != "CANCELLED_CALL":
                            if gbtt_departure == realtime_departure:
                                realtime_departure = "On time"
                                gbtt_departure = format_time(gbtt_departure)

                            elif realtime_departure == "Unknown":
                                gbtt_departure = format_time(gbtt_departure)

                            else:
                                realtime_departure = format_time(realtime_departure)
                                realtime_departure = "Exp " + realtime_departure
                                gbtt_departure = format_time(gbtt_departure)

                        else:
                            realtime_departure = "Cancelled"
                            gbtt_departure = format_time(gbtt_departure)

                        
                        terminus = destination.pop()["description"]

                        departure_board.append([gbtt_departure, terminus, platform, realtime_departure, service_uid])

                        count += 1
                        if count == rows:
                            break

                    print("Departure board for " + requested_location + ". Generated at " + datetime.now().strftime("%H:%M:%S on %d/%m/%y."))
                    print(tabulate(departure_board, tablefmt = "rounded_grid", headers = ["Booked Departure", "Destination", "Platform", "Booked Departure", "Service UID"]))

                    return "Departure board printed successfully" 

                elif self.__complexity == "a.n":
                    departure_board: list = []
                    
                    services = service_data["services"]
                    count = 0

                    for service in services:
                        location_detail = service["locationDetail"]
                        destination = location_detail["destination"]
                        status = location_detail["displayAs"]


                        if "gbttBookedDeparture" in location_detail:
                            gbtt_departure = location_detail["gbttBookedDeparture"]

                        else:
                            gbtt_departure = "Unknown"

                        if "platform" in location_detail:
                            platform = location_detail["platform"]

                        else:
                            platform = "Unknown"

                        if "realtimeDeparture" in location_detail:
                            realtime_departure = location_detail["realtimeDeparture"]

                        else:
                            realtime_departure = "Unknown"

                        if "serviceUid" in service:
                            service_uid = service["serviceUid"]

                        else:
                            service_uid = "Unknown"


                        if status != "CANCELLED_CALL":
                            if gbtt_departure == realtime_departure:
                                realtime_departure = "On time"
                                gbtt_departure = format_time(gbtt_departure)

                            elif realtime_departure == "Unknown":
                                gbtt_departure = format_time(gbtt_departure)

                            else:
                                realtime_departure = format_time(realtime_departure)
                                realtime_departure = "Exp " + realtime_departure
                                gbtt_departure = format_time(gbtt_departure)

                        else:
                            realtime_departure = "Cancelled"
                            gbtt_departure = format_time(gbtt_departure)

                        
                        terminus = destination.pop()["description"]

                        departure_board.append(DepartureBoardSimple(gbtt_departure, terminus, platform, realtime_departure, service_uid))

                        count += 1
                        if count == rows:
                            break

                    return departure_board 

                elif self.__complexity == "s.p" or self.__complexity == "s":
                    departure_board: list = []
                    
                    services = service_data["services"]
                    requested_location = service_data["location"]["name"]
                    count = 0

                    for service in services:
                        location_detail = service["locationDetail"]
                        destination = location_detail["destination"]
                        status = location_detail["displayAs"]


                        if "gbttBookedDeparture" in location_detail:
                            gbtt_departure = location_detail["gbttBookedDeparture"]

                        else:
                            gbtt_departure = "Unknown"

                        if "platform" in location_detail:
                            platform = location_detail["platform"]

                        else:
                            platform = "Unknown"

                        if "realtimeDeparture" in location_detail:
                            realtime_departure = location_detail["realtimeDeparture"]

                        else:
                            realtime_departure = "Unknown"

                        if "serviceUid" in service:
                            service_uid = service["serviceUid"]

                        else:
                            service_uid = "Unknown"


                        if status != "CANCELLED_CALL":
                            if gbtt_departure == realtime_departure:
                                realtime_departure = "On time"
                                gbtt_departure = format_time(gbtt_departure)

                            elif realtime_departure == "Unknown":
                                gbtt_departure = format_time(gbtt_departure)

                            else:
                                realtime_departure = format_time(realtime_departure)
                                realtime_departure = "Exp " + realtime_departure
                                gbtt_departure = format_time(gbtt_departure)

                        else:
                            realtime_departure = "Cancelled"
                            gbtt_departure = format_time(gbtt_departure)

                        
                        terminus = destination.pop()["description"]

                        departure_board.append([gbtt_departure, terminus, platform, realtime_departure, service_uid])

                        count += 1
                        if count == rows:
                            break

                    print("Departure board for " + requested_location + ". Generated at " + datetime.now().strftime("%H:%M:%S on %d/%m/%y."))
                    print(tabulate(departure_board, tablefmt = "rounded_grid", headers = ["Booked Departure", "Destination", "Platform", "Booked Departure", "Service UID"]))

                    return "Departure board printed successfully"  

                elif self.__complexity == "s.n":

                    departure_board: list = []
                    
                    services = service_data["services"]
                    count = 0

                    for service in services:
                        location_detail = service["locationDetail"]
                        destination = location_detail["destination"]
                        status = location_detail["displayAs"]


                        if "gbttBookedDeparture" in location_detail:
                            gbtt_departure = location_detail["gbttBookedDeparture"]

                        else:
                            gbtt_departure = "Unknown"

                        if "platform" in location_detail:
                            platform = location_detail["platform"]

                        else:
                            platform = "Unknown"

                        if "realtimeDeparture" in location_detail:
                            realtime_departure = location_detail["realtimeDeparture"]

                        else:
                            realtime_departure = "Unknown"

                        if "serviceUid" in service:
                            service_uid = service["serviceUid"]

                        else:
                            service_uid = "Unknown"


                        if status != "CANCELLED_CALL":
                            if gbtt_departure == realtime_departure:
                                realtime_departure = "On time"
                                gbtt_departure = format_time(gbtt_departure)

                            elif realtime_departure == "Unknown":
                                gbtt_departure = format_time(gbtt_departure)

                            else:
                                realtime_departure = format_time(realtime_departure)
                                realtime_departure = "Exp " + realtime_departure
                                gbtt_departure = format_time(gbtt_departure)

                        else:
                            realtime_departure = "Cancelled"
                            gbtt_departure = format_time(gbtt_departure)

                        
                        terminus = destination.pop()["description"]

                        departure_board.append(DepartureBoardSimple(gbtt_departure, terminus, platform, realtime_departure, service_uid))

                        count += 1
                        if count == rows:
                            break

                    return departure_board 


            elif api_response.status_code == 404:
                raise ValueError("An unexpected error occurred. Status code:", api_response.status_code)
            
            elif api_response.status_code == 401 or api_response.status_code == 403:
                raise ValueError("Access blocked: check your credentials. Status code:", api_response.status_code)

            else:
                raise ConnectionRefusedError("Failed to connect to the RTT API server. Try again in a few minutes. Status code:", api_response.status_code)

        else: 
            raise ValueError("Invalid date or time. Date or time provided did not meet requirements or fall into the valid date/time range.")

    def _get_arr_board_details(self, tiploc, filter, rows, time, date: str = None) -> list | str:
        if date is None:
            new_date = (datetime.now()).strftime("%Y/%m/%d")

        else:
            new_date = date

        if time is None:
            new_time = (datetime.now()).strftime("%H%M")

        else:
            new_time = time

        if self.__complexity == "c" or (validate_date(new_date) and validate_time(new_time)):
            search_query = "https://api.rtt.io/api/v1/json/search/" + str(tiploc)

            if filter is not None:
                search_query += "/to/" + str(filter)

            if date is not None:
                search_query +=  "/" + str(date)

            if time is not None:
                search_query += "/" + str(time)

            search_query += "/arrivals"

            # print(search_query)
            api_response =  requests.get(search_query, auth = (self.__username, self.__password))

            if api_response.status_code == 200:
                service_data = api_response.json()

                # print(service_data["services"])

                if service_data["services"] == None:
                    raise ValueError("No data found.")

                if self.__complexity == "c":
                    split_date = new_date.split("/")
                    file_name = tiploc + "_on_" + split_date[0] + "." + split_date[1] + "." + split_date[2] + "_arr_board_data"

                    return create_file(file_name, service_data)
                
                elif self.__complexity == "a.p" or self.__complexity == "a":
                    arrivals_board: list = []
                    
                    services = service_data["services"]
                    requested_location = service_data["location"]["name"]

                    count = 0

                    for service in services:
                        location_detail = service["locationDetail"]
                        destinations = location_detail["destination"]
                        origins = location_detail["origin"]
                        status = location_detail["displayAs"]

                        if "gbttBookedArrival" in location_detail:
                            gbtt_arrival = location_detail["gbttBookedArrival"]

                        else:
                            gbtt_arrival = "Unknown"

                        if "platform" in location_detail:
                            platform = location_detail["platform"]

                        else:
                            platform = "Unknown"

                        if "realtimeArrival" in location_detail:
                            realtime_arrival = location_detail["realtimeArrival"]

                        else:
                            realtime_arrival = "Unknown"

                        if "serviceUid" in service:
                            service_uid = service["serviceUid"]

                        else:
                            service_uid = "Unknown"

                        if status != "CANCELLED_CALL":
                            if gbtt_arrival == realtime_arrival:
                                realtime_arrival = "On time"
                                gbtt_arrival = format_time(gbtt_arrival)

                            elif realtime_arrival == "Unknown":
                                gbtt_arrival = format_time(gbtt_arrival)

                            else:
                                realtime_arrival = format_time(realtime_arrival)
                                realtime_arrival = "Exp " + realtime_arrival
                                gbtt_arrival = format_time(gbtt_arrival)

                        else:
                            realtime_arrival = "Cancelled"
                            gbtt_arrival = format_time(gbtt_arrival)

                        for destination in destinations:
                            terminus = destination["description"]
                            #print(terminus)
                        
                        origin = origins.pop()["description"]

                        arrivals_board.append([gbtt_arrival, terminus, origin, platform, realtime_arrival, service_uid])
                    
                        count += 1
                        if count == rows:
                            break

                    print("Arrivals board for " + requested_location + ". Generated at " + datetime.now().strftime("%H:%M:%S on %d/%m/%y."))
                    print(tabulate(arrivals_board, tablefmt = "rounded_grid", headers = ["Booked Arrival", "Destination", "Origin", "Platform", "Booked Arrival", "Service UID"]))

                    return "Arrivals board printed successfully"
                
                elif self.__complexity == "a.n":
                    
                    arrivals_board: list = []
                    
                    services = service_data["services"]
                    count = 0

                    for service in services:
                        location_detail = service["locationDetail"]
                        destinations = location_detail["destination"]
                        origins = location_detail["origin"]
                        status = location_detail["displayAs"]

                        if "gbttBookedArrival" in location_detail:
                            gbtt_arrival = location_detail["gbttBookedArrival"]

                        else:
                            gbtt_arrival = "Unknown"

                        if "platform" in location_detail:
                            platform = location_detail["platform"]

                        else:
                            platform = "Unknown"

                        if "realtimeArrival" in location_detail:
                            realtime_arrival = location_detail["realtimeArrival"]

                        else:
                            realtime_arrival = "Unknown"

                        if "serviceUid" in service:
                            service_uid = service["serviceUid"]

                        else:
                            service_uid = "Unknown"


                        if status != "CANCELLED_CALL":
                            if gbtt_arrival == realtime_arrival:
                                realtime_arrival = "On time"
                                gbtt_arrival = format_time(gbtt_arrival)

                            elif realtime_arrival == "Unknown":
                                gbtt_arrival = format_time(gbtt_arrival)

                            else:
                                realtime_arrival = format_time(realtime_arrival)
                                realtime_arrival = "Exp " + realtime_arrival
                                gbtt_arrival = format_time(gbtt_arrival)

                        else:
                            realtime_arrival = "Cancelled"
                            gbtt_arrival = format_time(gbtt_arrival)

                        for destination in destinations:
                            terminus = destination["description"]
                            #print(terminus)
                        
                        origin = origins.pop()["description"]

                        arrivals_board.append(ArrivalBoardSimple(gbtt_arrival, terminus, origin, platform, realtime_arrival, service_uid))
                    
                        count += 1
                        if count == rows:
                            break

                elif self.__complexity == "s.p" or self.__complexity == "s":
                    arrivals_board: list = []
                    
                    services = service_data["services"]
                    requested_location = service_data["location"]["name"]
                    count = 0

                    for service in services:
                        location_detail = service["locationDetail"]
                        destinations = location_detail["destination"]
                        origins = location_detail["origin"]
                        status = location_detail["displayAs"]

                        if "gbttBookedArrival" in location_detail:
                            gbtt_arrival = location_detail["gbttBookedArrival"]

                        else:
                            gbtt_arrival = "Unknown"

                        if "platform" in location_detail:
                            platform = location_detail["platform"]

                        else:
                            platform = "Unknown"

                        if "realtimeArrival" in location_detail:
                            realtime_arrival = location_detail["realtimeArrival"]

                        else:
                            realtime_arrival = "Unknown"

                        if "serviceUid" in service:
                            service_uid = service["serviceUid"]

                        else:
                            service_uid = "Unknown"

                        if status != "CANCELLED_CALL":
                            if gbtt_arrival == realtime_arrival:
                                realtime_arrival = "On time"
                                gbtt_arrival = format_time(gbtt_arrival)

                            elif realtime_arrival == "Unknown":
                                gbtt_arrival = format_time(gbtt_arrival)

                            else:
                                realtime_arrival = format_time(realtime_arrival)
                                realtime_arrival = "Exp " + realtime_arrival
                                gbtt_arrival = format_time(gbtt_arrival)

                        else:
                            realtime_arrival = "Cancelled"
                            gbtt_arrival = format_time(gbtt_arrival)

                        for destination in destinations:
                            terminus = destination["description"]
                            #print(terminus)
                        
                        origin = origins.pop()["description"]

                        arrivals_board.append([gbtt_arrival, terminus, origin, platform, realtime_arrival, service_uid])

                        count += 1
                        if count == rows:
                            break
                    
                    print("Arrivals board for " + requested_location + ". Generated at " + datetime.now().strftime("%H:%M:%S on %d/%m/%y."))
                    print(tabulate(arrivals_board, tablefmt = "rounded_grid", headers = ["Booked Arrival", "Destination", "Origin", "Platform", "Booked Arrival", "Service UID"]))

                    return "Arrivals board printed successfully"

                elif self.__complexity == "s.n":

                    arrivals_board: list = []
                    
                    services = service_data["services"]
                    count = 0

                    for service in services:
                        location_detail = service["locationDetail"]
                        destinations = location_detail["destination"]
                        origins = location_detail["origin"]
                        status = location_detail["displayAs"]

                        if "gbttBookedArrival" in location_detail:
                            gbtt_arrival = location_detail["gbttBookedArrival"]

                        else:
                            gbtt_arrival = "Unknown"

                        if "platform" in location_detail:
                            platform = location_detail["platform"]

                        else:
                            platform = "Unknown"

                        if "realtimeArrival" in location_detail:
                            realtime_arrival = location_detail["realtimeArrival"]

                        else:
                            realtime_arrival = "Unknown"

                        if "serviceUid" in service:
                            service_uid = service["serviceUid"]

                        else:
                            service_uid = "Unknown"

                        if status != "CANCELLED_CALL":
                            if gbtt_arrival == realtime_arrival:
                                realtime_arrival = "On time"
                                gbtt_arrival = format_time(gbtt_arrival)

                            elif realtime_arrival == "Unknown":
                                gbtt_arrival = format_time(gbtt_arrival)

                            else:
                                realtime_arrival = format_time(realtime_arrival)
                                realtime_arrival = "Exp " + realtime_arrival
                                gbtt_arrival = format_time(gbtt_arrival)

                        else:
                            realtime_arrival = "Cancelled"
                            gbtt_arrival = format_time(gbtt_arrival)

                        for destination in destinations:
                            terminus = destination["description"]
                            #print(terminus)
                        
                        origin = origins.pop()["description"]

                        arrivals_board.append(ArrivalBoardSimple(gbtt_arrival, terminus, origin, platform, realtime_arrival, service_uid))

                        count += 1
                        if count == rows:
                            break

                    return arrivals_board


            elif api_response.status_code == 404:
                raise ValueError("An unexpected error occurred. Status code:", api_response.status_code)
            
            elif api_response.status_code == 401 or api_response.status_code == 403:
                raise ValueError("Access blocked: check your credentials. Status code:", api_response.status_code)

            else:
                raise ConnectionRefusedError("Failed to connect to the RTT API server. Try again in a few minutes. Status code:", api_response.status_code)

        else: 
            raise ValueError("Invalid date or time. Date or time provided did not meet requirements or fall into the valid date/time range.")
        
    def _get_stat_board_details(self, tiploc, filter, rows, time, date: str = None) -> list | str:
        if date is None:
            new_date = (datetime.now()).strftime("%Y/%m/%d")

        else:
            new_date = date

        if time is None:
            new_time = (datetime.now()).strftime("%H%M")

        else:
            new_time = time

        if self.__complexity == "c" or (validate_date(new_date) and validate_time(new_time)):
            search_query = "https://api.rtt.io/api/v1/json/search/" + str(tiploc)

            if filter is not None:
                search_query += "/to/" + str(filter)

            if date is not None:
                search_query +=  "/" + str(date)

            if time is not None:
                search_query += "/" + str(time)

            departure_query = search_query
            arrival_query = search_query + "/arrivals"

            dep_api_response =  requests.get(departure_query, auth = (self.__username, self.__password))
            arr_api_response =  requests.get(arrival_query, auth = (self.__username, self.__password))

            if dep_api_response.status_code == 200 and arr_api_response.status_code == 200:
                departures_data = dep_api_response.json()
                arrivals_data = arr_api_response.json()

                if departures_data["services"] == None or arrivals_data["services"] == None:
                    raise ValueError("No data found.")
                
                if self.__complexity == "c":
                    split_date = new_date.split("/")
                    dep_file_name = tiploc + "_on_" + split_date[0] + "." + split_date[1] + "." + split_date[2] + "_dep_board_data"
                    arr_file_name = tiploc + "_on_" + split_date[0] + "." + split_date[1] + "." + split_date[2] + "_arr_board_data"

                    create_file(dep_file_name, departures_data)
                    create_file(arr_file_name, arrivals_data)

                    return "Departures and arrivals saved to files: " + dep_file_name + arr_file_name

                elif self.__complexity == "a.p" or self.__complexity == "a":
                    raise NotImplementedError

                elif self.__complexity == "a.n":
                    raise NotImplementedError

                elif self.__complexity == "s.p" or self.__complexity == "s":
                    raise NotImplementedError

                elif self.__complexity == "s.n":
                    raise NotImplementedError

            elif dep_api_response.status_code == 404 or arr_api_response == 404:
                raise ValueError("An unexpected error occurred. Status codes:", dep_api_response.status_code, arr_api_response.status_code)

            elif (dep_api_response == 401 or arr_api_response == 401) or (dep_api_response == 403 or arr_api_response == 403):
                raise ValueError("Access blocked: check your credentials. Status codes:", dep_api_response.status_code, arr_api_response.status_code)

            else:
                raise ConnectionRefusedError("Failed to connect to the RTT API server. Try again in a few minutes. Status codes:", dep_api_response.status_code, arr_api_response.status_code)

        else:
            raise ValueError("Invalid date or time. Date or time provided did not meet requirements or fall into the valid date/time range.")
