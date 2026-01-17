import { Fragment } from 'react';
import { LatLng } from 'leaflet';
import { parseLatLong } from '@/helpers/Types.ts';
import type { Flight, AirportDict, Airport } from '@/helpers/Types.ts';
import { Popup, Marker, Polyline } from "react-leaflet";
import PlaneMarker from './PlaneMarker';

const NEON_COLORS = [
  '#00FF41', // Matrix green
  '#FF006E', // Hot pink
  '#00F5FF', // Cyan
  '#FFEA00', // Electric yellow
  '#FF3131', // Neon red
  '#9D00FF', // Purple
  '#FF9500', // Orange
  '#39FF14', // Lime green
  '#FF10F0', // Magenta
  '#00FFD1', // Turquoise
  '#FE4EDA', // Hot pink 2
  '#DFFF00', // Chartreuse
] as const;

function getFlightColour(flightId: number): string {
  return NEON_COLORS[Math.abs(flightId) % NEON_COLORS.length];
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

// Create all required details on the map related to a particular flight
export default function FlightMapElements({ flight, airports }: { flight: Flight, airports: AirportDict }) {
  const positions: LatLng[] = parseLatLong(flight["route"]);
  const colour = getFlightColour(flight.id);
  const heading = positions.length > 1 ? calculateHeading(positions[0], positions[1]) : 0;

  return (
    <>
      {positions.length > 0 &&
        <>
          <Polyline positions={positions} pathOptions={{ color: colour, weight: 3, opacity: 0.7, dashArray: '10, 5', lineCap: 'round', lineJoin: 'round' }}>
            <Popup>
              <div>
                <strong>Flight {flight.ACID}</strong><br />
                Aircraft: {flight.plane_type}<br />
                Altitude: {flight.aircraft_speed} ft<br />
                Speed: {flight.altitude} knots<br />
                Passengers: {flight.passengers}<br />
                Route: {flight.route}
              </div>
            </Popup>
          </Polyline>
          <PlaneMarker position={positions[0]} heading={heading} />
        </>
      }
    </>
  );
}

