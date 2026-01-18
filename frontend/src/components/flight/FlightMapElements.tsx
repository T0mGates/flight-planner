import type { Flight, AirportDict } from '@/helpers/Types.ts';
import PlaneMarker from './PlaneMarker';
import FlightMapLine from './FlightMapLine';
import { calculateFlightPositions, calculateFlightStatus } from "@/helpers/Flights.ts";

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

export default function FlightMapElements({ flight, airports, selectedFlightId, onSelect, currentTime }:
  { flight: Flight, airports: AirportDict, selectedFlightId: number, onSelect: (id: number) => void, currentTime: number }) {
  const positions = calculateFlightPositions(flight, airports);
  const colour = getFlightColour(flight.id);
  const flightStatus = calculateFlightStatus(flight, positions, currentTime);

  return (
    <>
      <FlightMapLine flight={flight} positions={positions} colour={colour} onSelect={onSelect} selectedFlightId={selectedFlightId} />
      {
        // Don't show the airplane after it lands (to reduce visual clutter)
        !flightStatus.atEnd &&
        <PlaneMarker position={flightStatus.currentPosition} heading={flightStatus.heading} />
      }
    </>
  );
}

