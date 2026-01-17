from pydantic import BaseModel

class Flight(BaseModel):
    departure_airport: str
    arrival_airport: str
    route: str
    ACID: str
    Plane_type: str
    is_cargo: bool
    passengers: int