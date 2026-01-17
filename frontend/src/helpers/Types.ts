import { LatLng } from 'leaflet';

export interface Flight
{
    departure_airport   : string,
    arrival_airport     : string,
    ACID                : string,
    Plane_type          : string,
    is_cargo            : boolean,
    passengers          : number,
    id                  : number,
    route               : string,
    aircraft_speed      : string
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
    const [latStr, lngStr] = coordinate.split('/');

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

    parsedCoordinates.push(new LatLng(lat, long));
  }
  return parsedCoordinates;
}


