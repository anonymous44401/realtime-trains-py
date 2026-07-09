from dataclasses import dataclass

### Service Details ###


# Calling Point dataclass
@dataclass(slots=True, frozen=True)
class CallingPoint:
    stop_name: str
    scheduled_arrival: str
    expected_arrival: str
    platform: str
    line: str
    scheduled_departure: str
    expected_departure: str
    coaches: int


# Service Data dataclass
@dataclass(slots=True, frozen=True)
class ServiceData:
    service_uid: str
    operator: str
    origin: str
    destination: str
    calling_points: list[CallingPoint]
    start_time: str
    end_time: str
    coaches: int


### Board Details ###


# Station Board Details dataclass
@dataclass(slots=True, frozen=True)
class StationBoardDetails:
    scheduled_arrival: str
    scheduled_departure: str
    terminus: str
    origin: str
    platform: str
    expected_arrival: str
    expected_departure: str
    service_uid: str
    coaches: int


# Default Board dataclass
@dataclass(slots=True, frozen=True)
class DefaultBoard:
    board: list[StationBoardDetails]
    location: str
