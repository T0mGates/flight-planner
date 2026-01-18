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

function getFlightColour(flightId: string): string {
  let hash = 0;
  for (let i = 0; i < flightId.length; i++) {
    // charCodeAt returns the numeric value of the character
    // We multiply by a prime (31) to ensure "AB" and "BA" get different colors
    hash = flightId.charCodeAt(i) + ((hash << 5) - hash);
  }

  return NEON_COLORS[Math.abs(hash * 5 + 3) % NEON_COLORS.length];
}

export default function FlightMapElements({ flight, airports, selectedFlightId, onSelect, currentTime }:
  { flight: Flight, airports: AirportDict, selectedFlightId: string | null, onSelect: (acid: string) => void, currentTime: number }) {
  const positions = calculateFlightPositions(flight, airports);
  const colour = getFlightColour(flight.ACID);
  const flightStatus = calculateFlightStatus(flight, positions, currentTime);
  const selected = flight.ACID == selectedFlightId;

  // Don't render anything for the flight if it isn't in flight at the current moment
  if (flightStatus.atStart || flightStatus.atEnd) {
    return (<></>)
  }

  return (
    <>
      <FlightMapLine flight={flight} positions={positions} colour={colour} onSelect={onSelect} selected={selected} />
      <PlaneMarker position={flightStatus.currentPosition} heading={flightStatus.heading} colour={colour} selected={selected} />
    </>
  );
}

