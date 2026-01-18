import type { AirportDict, Flight } from '@/helpers/Types.ts';
import { LatLng } from 'leaflet';
import { parseLatLong, airportPosition } from './Positions';

export function calculateHeading(from: LatLng, to: LatLng): number {
  const lat1 = from.lat * Math.PI / 180;
  const lat2 = to.lat * Math.PI / 180;
  const dLon = (to.lng - from.lng) * Math.PI / 180;

  const y = Math.sin(dLon) * Math.cos(lat2);
  const x = Math.cos(lat1) * Math.sin(lat2) -
    Math.sin(lat1) * Math.cos(lat2) * Math.cos(dLon);

  let heading = Math.atan2(y, x) * 180 / Math.PI;

  // Normalize to 0-360
  heading = (heading + 360) % 360;

  return heading;
}

export function calculateFlightPositions(flight: Flight, airports: AirportDict) {
  return [
    airportPosition(flight.departure_airport, airports),
    ...parseLatLong(flight.route),
    airportPosition(flight.arrival_airport, airports),
  ];
}

interface FlightStatus {
  heading: number
  currentPosition: LatLng
  atEnd: boolean,
}

export function calculateFlightStatus(
  flight: Flight,
  flightPositions: LatLng[],
  currentTime: number
): FlightStatus {
  let status: FlightStatus = { heading: 0, currentPosition: new LatLng(0, 0), atEnd: false };
  if (!flightPositions) {
    // This shouldn't happen
    return status;
  }
  const elapsedSeconds = currentTime - flight.departure_time;

  if (elapsedSeconds < 0) {
    status.currentPosition = flightPositions[0];
    return status
  }


  // Keep track of how long the plane would have been in the air for
  let timeAccumulated = 0;
  for (let i = 0; i < flightPositions.length - 1; i++) {
    const segmentStart = flightPositions[i];
    const segmentEnd = flightPositions[i + 1];

    // Convert speed from knots to km/h
    const speedKmh = flight.aircraft_speed * 1.852;

    // Calculate distance for this segment, in meters (convert to km)
    const segmentDistance = segmentStart.distanceTo(segmentEnd) / 1000;

    // Calculate time to fly this segment (in seconds)
    const segmentDuration = (segmentDistance / speedKmh) * 3600;

    // Check if plane is on this segment
    if (elapsedSeconds <= timeAccumulated + segmentDuration) {
      // Plane is currently on this segment, get remaining time
      const timeIntoSegment = elapsedSeconds - timeAccumulated;
      const fraction = timeIntoSegment / segmentDuration;

      // Linear interpolation between start and end
      const lat = segmentStart.lat + (segmentEnd.lat - segmentStart.lat) * fraction;
      const lng = segmentStart.lng + (segmentEnd.lng - segmentStart.lng) * fraction;

      status.currentPosition = new LatLng(lat, lng);
      status.heading = calculateHeading(segmentStart, segmentEnd);
      return status;
    }
    // Otherwise, increment the accumulated time and continue
    timeAccumulated += segmentDuration;
  }
  // We're at the end of the flight, return the last position
  status.currentPosition = flightPositions[flightPositions.length - 1];
  status.atEnd = true;
  return status;
}


export function getFirstFlight(flights: Flight[]) {
  if (!flights || flights.length == 0) {
    return 0;
  }
  let earliest = flights[0];
  for (const flight of flights) {
    if (flight.departure_time < earliest.departure_time) {
      earliest = flight;
    }
  }
  return earliest.departure_time;
}

export function getLastFlight(flights: Flight[], airports: AirportDict) {
  if (!flights || flights.length == 0) {
    return 0;
  }
  let latestTime = 0;
  for (const flight of flights) {
    const positions = calculateFlightPositions(flight, airports);
    let timeAccumulated = 0;
    for (let i = 0; i < positions.length - 1; i++) {
      const segmentStart = positions[i];
      const segmentEnd = positions[i + 1];

      // Convert speed from knots to km/h
      const speedKmh = flight.aircraft_speed * 1.852;
      const segmentDistance = segmentStart.distanceTo(segmentEnd) / 1000;
      timeAccumulated += (segmentDistance / speedKmh) * 3600;
    }
    const totalTime = timeAccumulated + flight.departure_time;
    if (totalTime > latestTime) {
      latestTime = totalTime;
    }
  }
  return latestTime;
}
