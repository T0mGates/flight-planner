from datetime import datetime, timezone

from backend.models import (
    Flight,
    Airport,
    FlightFilters,
    raw_flight_data_to_flight_model,
)
from backend.scheduler.data_loader import load_data
from backend.scheduler import constants
from backend.logging.logger import get_logger
from backend.scheduler.models import FlightSchedule

log = get_logger()


class Database:
    _flight_data: dict[int, Flight] = {}
    _airport_data: dict[str, Airport] = {}

    @classmethod
    def init(cls):
        flight_data = FlightSchedule.from_json_file("canadian_flights_1000.json")

        for raw_flight in flight_data.to_database_flight():
            cls.add_flight(raw_flight)

        for code in constants.TRANSLATION.keys():
            latlon = constants.TRANSLATION.get(code, "")
            airport_name = constants.AIRPORT_NAME_MAP.get(code, "")

            if latlon and airport_name:
                cls._airport_data[code] = {}
                cls._airport_data[code]["latlon"] = latlon
                cls._airport_data[code]["airport_name"] = airport_name

    @classmethod
    def add_flight(cls, flight: Flight) -> bool:
        cls._flight_data[flight.ACID] = flight.model_dump()
        return True

    @classmethod
    def get_flights(
        cls, filters: FlightFilters, reverse: bool = False
    ) -> dict[int, Flight]:
        to_ret = {}
        l = (
            reversed(list(cls._flight_data.values()))
            if reverse
            else cls._flight_data.values()
        )
        for flight in l:
            if cls.include_flight_based_off_filter(
                flight_acid=flight["ACID"], filters=filters
            ):
                to_ret[flight["ACID"]] = flight

        return to_ret

    @classmethod
    def include_flight_based_off_filter(
        cls, flight_acid: str, filters: FlightFilters
    ) -> bool:
        flight = cls._flight_data.get(flight_acid, {})
        if not flight:
            return False

        to_include = True

        if filters.destination:
            if flight["arrival_airport"] != filters.destination:
                to_include = False

        if filters.origin:
            if flight["departure_airport"] != filters.origin:
                to_include = False

        # Save time if we can
        if not to_include:
            return to_include

        start_filter = None
        end_filter = None

        try:
            start_filter = (
                datetime.fromisoformat(filters.start.replace("Z", "+00:00"))
                if filters.start
                else None
            )
        except:
            pass

        try:
            end_filter = (
                datetime.fromisoformat(filters.end.replace("Z", "+00:00"))
                if filters.end
                else None
            )
        except:
            pass

        flight_departure = None
        try:
            flight_departure = datetime.fromtimestamp(
                flight["departure_time"], tz=timezone.utc
            )
        except:
            pass

        if not flight_departure:
            to_include = False

        else:
            # Three cases

            # 1. Only start filter is active
            if start_filter and not end_filter:
                if flight_departure < start_filter:
                    to_include = False

            # 2. Only end filter is active
            elif end_filter and not start_filter:
                if flight_departure > end_filter:
                    to_include = False

            # 3. Both filters are active
            elif end_filter and start_filter:
                if not (
                    flight_departure >= start_filter and flight_departure <= end_filter
                ):
                    to_include = False

        return to_include

    @classmethod
    def get_flight_by_acid(cls, acid: str) -> Flight:
        return cls._flight_data.get(acid, {})

    @classmethod
    def get_all_airports_details(cls) -> dict[str, Airport]:
        return cls._airport_data

    @classmethod
    def get_airport_details(cls, iata_code: str) -> Airport | dict:
        return cls._airport_data.get(iata_code, {})

    @classmethod
    def get_all_flights(cls) -> dict[int, Flight]:
        return cls._flight_data

    @classmethod
    def clear_flights(cls):
        cls._flight_data = {}

