import              json

from backend.models import  Flight
from backend.scheduler.main import load_data

class Database():
    _data: dict[int, Flight]    = {}
    _next_id                    = 1

    @classmethod
    def init(cls):
        # TODO (noah)
        flight_data = load_data('canadian_flights_1000.json').to_dict(orient='records')

        for flight in flight_data:
            cls.add_flight(Flight(**flight))

    @classmethod
    def add_flight(cls, flight: Flight)->bool:
        cls._data[cls._next_id]         = flight.model_dump()
        cls._data[cls._next_id]["id"]   = cls._next_id
        cls._next_id                    += 1
        return True

    @classmethod
    def get_flights(cls)->dict[int, Flight]:
        return cls._data
    
    @classmethod
    def get_flight_by_id(cls, id: int)->Flight:
        return cls._data.get(id, {})