from pydantic import BaseModel

class Flight(BaseModel):
    departure_airport   : str
    arrival_airport     : str
    route               : str
    ACID                : str
    plane_type          : str
    route               : str
    is_cargo            : bool
    aircraft_speed      : float
    altitude            : int
    passengers          : int

class Airport(BaseModel):
    latlon              : str
    airport_name        : str

def raw_flight_data_to_flight_model(raw_data: dict)->Flight:
    raw_data["plane_type"]        = raw_data["Plane_type"]
    del raw_data["Plane_type"]

    return Flight(**raw_data)