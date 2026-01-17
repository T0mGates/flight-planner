import { LatLng } from 'leaflet';

export interface Flight {
  departure_airport: string,
  arrival_airport: string,
  ACID: string,
  plane_type: string,
  route: string,
  is_cargo: boolean,
  aircraft_speed: number,
  altitude: number,
  passengers: number,
  departure_time: number,
  id: number,
};

export interface Airport {
  latlon: string,
  airport_name: string
};

export type AirportDict = {
  [key: string]: Airport
}

export interface FlightFilters {
  startDateTime       : string; // ISO String: "2026-05-03T07:00"
  endDateTime         : string;   // ISO String: "2026-05-03T16:00"
  origin              : string;
  destination         : string;
}

class RouteParseError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'RouteParseError';
  }
}

// Parse the format for lat/long that we're using on the backend to the format that leaflet can recognize
// Expect a string of coordinates, seperated by spaces and by slashes
export function parseLatLong(route: string) {
  // Expect multiple coordinate pairs
  const coordinates = route.split(' ');
  let parsedCoordinates = [];

  for (const coordinate of coordinates) {
    parsedCoordinates.push(parseSingleLatLong(coordinate));
  }
  return parsedCoordinates;
}

export function parseSingleLatLong(position: string) {
  const [latStr, lngStr] = position.split('/');

  if (!latStr.match(/^[\d.]+[NS]$/i)) {
    throw new RouteParseError(`Invalid latitude format: "${latStr}". Expected format: "50.77N" or "50.77S"`);
  }

  if (!lngStr.match(/^[\d.]+[EW]$/i)) {
    throw new RouteParseError(`Invalid longitude format: "${lngStr}". Expected format: "115.66W" or "115.66E"`);
  }

  const latValue = parseFloat(latStr);
  const lat = latStr.includes('S') ? -latValue : latValue;

  const lngValue = parseFloat(lngStr);
  const long = lngStr.includes('W') ? -lngValue : lngValue;

  return new LatLng(lat, long);
}
