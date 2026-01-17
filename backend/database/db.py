from backend.models         import  Flight, Airport, FlightFilters, raw_flight_data_to_flight_model
from backend.scheduler.main import  load_data
from backend.scheduler      import  constants
from backend.logging.logger import get_logger

log = get_logger()

class Database():
    _flight_data : dict[int, Flight]    = {}
    _airport_data: dict[str, Airport]   = {}
    _next_id                            = 1

    @classmethod
    def init(cls):
        flight_data = load_data('canadian_flights_1000.json').to_dict(orient='records')

        for flight in flight_data:
            cls.add_flight(raw_flight_data_to_flight_model(raw_data=flight))

        for code in constants.TRANSLATION.keys():
            latlon          = constants.TRANSLATION.get(code, "")
            airport_name    = constants.AIRPORT_NAME_MAP.get(code, "")

            if latlon and airport_name:
                cls._airport_data[code]                  = {}
                cls._airport_data[code]["latlon"]        = latlon
                cls._airport_data[code]["airport_name"]  = airport_name

    @classmethod
    def add_flight(cls, flight: Flight)->bool:
        cls._flight_data[cls._next_id]         = flight.model_dump()
        cls._flight_data[cls._next_id]["id"]   = cls._next_id
        cls._next_id                    += 1
        return True

    @classmethod
    def get_flights(cls, filters: FlightFilters)->dict[int, Flight]:
        to_ret = {}
        for flight in cls._flight_data.values():
            to_include = True

            if filters.destination:
                if flight["arrival_airport"] != filters.destination:
                    to_include = False

            if filters.origin:
                if flight["departure_airport"] != filters.origin:
                    to_include = False

            if to_include:
                to_ret[flight["id"]] = flight

            if len(to_ret.keys()) >= 100:
                break
            
        return to_ret
    
    @classmethod
    def get_flight_by_id(cls, id: int)->Flight:
        return cls._flight_data.get(id, {})
    
    @classmethod
    def get_all_airports_details(cls)->dict[str, Airport]:
        return cls._airport_data
    
    @classmethod
    def get_airport_details(cls, iata_code: str)->Airport | dict:
        return cls._airport_data.get(iata_code, {})