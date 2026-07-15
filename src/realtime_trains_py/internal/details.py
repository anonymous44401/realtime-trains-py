from dataclasses import dataclass

# Service Location Data dataclass
@dataclass(slots=True, frozen=True)
class ServiceLocationData:
    stop_name: str
    scheduled_arrival: str
    expected_arrival: str
    platform: str
    line: str
    scheduled_departure: str
    expected_departure: str
    coaches: int
    terminus: str
    origin: str
    service_uid: str

# Service Data dataclass
@dataclass(slots=True, frozen=True)
class ServiceData:
    service_uid: str
    operator: str
    origin: str
    destination: str
    calling_points: list[ServiceLocationData]
    start_time: str
    end_time: str
    coaches: int

# Default Board dataclass
@dataclass(slots=True, frozen=True)
class DefaultBoard:
    board: list[ServiceLocationData]
    location: str
