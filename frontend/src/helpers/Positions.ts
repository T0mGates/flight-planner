import { LatLng } from 'leaflet';
import type { AirportDict } from '@/helpers/Types.ts';

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

class RouteParseError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'RouteParseError';
  }
}

export function parseSingleLatLong(position: string) {
  const [latStr, lngStr] = position.split('/');

  if (!latStr.match(/^[\d.]+[NS]$/i)) {
    throw new RouteParseError(`Invalid latitude format: "${latStr}"`);
  }

  if (!lngStr.match(/^[\d.]+[EW]$/i)) {
    throw new RouteParseError(`Invalid longitude format: "${lngStr}"`);
  }

  const latValue = parseFloat(latStr);
  const lat = latStr.includes('S') ? -latValue : latValue;

  const lngValue = parseFloat(lngStr);
  const long = lngStr.includes('W') ? -lngValue : lngValue;

  return new LatLng(lat, long);
}

export function airportPosition(airport: string, airports: AirportDict) {
  if (airport in airports) {
    return parseSingleLatLong(airports[airport].latlon);
  }
  return new LatLng(0, 0);
}
