export interface Flight {
  departure_airport: string,
  arrival_airport: string,
  ACID: string,
  plane_type: string,
  route: string,
  is_cargo: boolean,
  aircraft_speed: number[],
  altitude: number[],
  passengers: number,
  departure_time: number,
  id: number,
};

export interface FlightDiff {
  departure_time_diff: number,
  was_delayed: false,
  average_speed_diff: number,
  average_altitude_diff: number,
  has_differences: boolean
};

export interface Airport {
  latlon: string,
  airport_name: string
};

export type AirportDict = {
  [key: string]: Airport
}

export interface FlightFilters {
  startDateTime: string; // ISO String: "2026-05-03T07:00"
  endDateTime: string;   // ISO String: "2026-05-03T16:00"
  origin: string;
  destination: string;
}

