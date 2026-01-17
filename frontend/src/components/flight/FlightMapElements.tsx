import { LatLng } from 'leaflet';
import { parseLatLong, parseSingleLatLong } from '@/helpers/Types.ts';
import type { Flight, AirportDict } from '@/helpers/Types.ts';
import { Popup, Polyline } from "react-leaflet";
import PlaneMarker from './PlaneMarker';
import L from 'leaflet';

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
  return parseSingleLatLong(airports[airport].latlon);
}

export default function FlightMapElements({ flight, airports, onSelect }:
  { flight: Flight, airports: AirportDict, onSelect: (id: number) => void }) {

  const positions: LatLng[] = parseLatLong(flight.route);
  const lineElements: LatLng[] = [
    airportPosition(flight.departure_airport, airports),
    ...positions,
    airportPosition(flight.arrival_airport, airports)
  ];
  const colour = getFlightColour(flight.id);
  const heading = positions.length > 1 ? calculateHeading(positions[0], positions[1]) : 0;

  return (
    <>
      {positions.length > 0 &&
        <>
          {/* Invisible, thick Polyline for easier clicking */}
          <Polyline
            positions={lineElements}
            pathOptions={{
              color: 'transparent',
              weight: 20,
            }}
            eventHandlers={{
              click: (e) => {
                onSelect(flight.id);
                L.DomEvent.stopPropagation(e);
              },
            }}
          >
            <Popup>
              <div className="flex justify-between items-center mb-2">
                <div className="text-lg font-bold tracking-tight text-white">
                  Flight {flight.ACID}
                </div>
              </div>
              <div className="text-sm text-zinc-500">
                From: {flight.departure_airport}<br />
                To: {flight.arrival_airport}<br />
              </div>
            </Popup>
          </Polyline>

          {/* 2. THE VISUAL LINE: The thin, elegant dashed line */}
          <Polyline
            positions={lineElements}
            pathOptions={{
              color: colour,
              weight: 2.5,
              opacity: 0.3,
              dashArray: '10, 10',
              lineCap: 'round',
              lineJoin: 'round',
              interactive: false // Clicks pass through to the 'Hit Area' below
            }}
          />

          <PlaneMarker position={positions[0]} heading={heading}
          />
        </>
      }
    </>
  );
}

