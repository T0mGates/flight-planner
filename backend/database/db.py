from models import Flight

class Database():
    _data: dict[int, Flight]    = {}
    _next_id                    = 1

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