import { LatLng } from 'leaflet';
import { parseLatLong, parseSingleLatLong } from '@/helpers/Types.ts';
import type { Flight, AirportDict } from '@/helpers/Types.ts';
import PlaneMarker from './PlaneMarker';
import FlightMapLine from './FlightMapLine';

// Make neon colours with greater variety
function generateNeonColors(count: number) {
  const colors = [];

  for (let i = 0; i < count; i++) {
    const hue = (i * 360 / count);
    const saturation = 100;
    const lightness = 40;
    colors.push(`hsl(${hue} ${saturation} ${lightness})`);
  }
  return colors;
}

const NEON_COLORS = generateNeonColors(150);

function getFlightColour(flightId: number): string {
  return NEON_COLORS[Math.abs(flightId * 5 + 3) % NEON_COLORS.length];
}

function calculateHeading(from: LatLng, to: LatLng): number {
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

function airportPosition(airport: string, airports: AirportDict) {
  if (airport in airports) {
    return parseSingleLatLong(airports[airport].latlon);
  }
  return new LatLng(0, 0);
}

function calculateFlightPositions(flight: Flight, airports: AirportDict) {
  return [
    airportPosition(flight.departure_airport, airports),
    ...parseLatLong(flight.route),
    airportPosition(flight.arrival_airport, airports),
  ];
}

function calculateCurrentFlightPosition(
  flight: Flight,
  flightPositions: LatLng[],
  currentTime: number
): LatLng {
  if (!flightPositions) {
    // This shouldn't happen
    console.log("No flight positions to calculate plane from");
    return new LatLng(0, 0);
  }
  const elapsedSeconds = currentTime - flight.departure_time;

  if (elapsedSeconds < 0) {
    return flightPositions[0];
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
      // Plane is currently on this segment
      const timeIntoSegment = elapsedSeconds - timeAccumulated;
      const fraction = timeIntoSegment / segmentDuration;

      // Linear interpolation between start and end
      const lat = segmentStart.lat + (segmentEnd.lat - segmentStart.lat) * fraction;
      const lng = segmentStart.lng + (segmentEnd.lng - segmentStart.lng) * fraction;

      return new LatLng(lat, lng);
    }
  }
  // We're at the end of the flight, return the last position
  return flightPositions[flightPositions.length - 1];
}

export default function FlightMapElements({ flight, airports, onSelect }:
  { flight: Flight, airports: AirportDict, onSelect: (id: number) => void }) {
  const positions = calculateFlightPositions(flight, airports);
  const colour = getFlightColour(flight.id);
  const heading = positions.length > 1 ? calculateHeading(positions[0], positions[1]) : 0;

  return (
    <>
      <FlightMapLine flight={flight} positions={positions} colour={colour} onSelect={onSelect} />
      <PlaneMarker position={calculateCurrentFlightPosition(flight, positions, 0)} heading={heading} />
    </>
  );
}

