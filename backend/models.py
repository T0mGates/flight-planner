from datetime               import datetime
from typing                 import Optional
from pydantic               import BaseModel

class Flight(BaseModel):
    departure_airport   : str
    arrival_airport     : str
    route               : str
    ACID                : str
    plane_type          : str
    route               : str
    is_cargo            : bool
    aircraft_speed      : float
    departure_time      : int
    altitude            : int
    passengers          : int

class Airport(BaseModel):
    latlon              : str
    airport_name        : str

class FlightFilters():
    def __init__(
        self,
        start:          Optional[datetime] = None, 
        end:            Optional[datetime] = None,
        origin:         Optional[str] = None,
        destination:    Optional[str] = None
    ):
        self.start          = start
        self.end            = end
        self.origin         = origin
        self.destination    = destination

def raw_flight_data_to_flight_model(raw_data: dict)->Flight:
    raw_data["plane_type"]        = raw_data["Plane_type"]
    del raw_data["Plane_type"]

    return Flight(**raw_data)