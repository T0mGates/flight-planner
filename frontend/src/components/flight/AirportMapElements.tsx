import type { Airport } from '@/helpers/Types.ts';
import { Marker, Popup } from 'react-leaflet';
import { parseSingleLatLong } from '@/helpers/Positions.ts';
import { divIcon } from "leaflet";

const planeIcon = divIcon({
  className: 'airport-icon',
  html: `
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <path d="M2 22h20"></path>
      <path d="M6.36 17.4 4 17l-2-4 1.1-.55a2 2 0 0 1 1.8 0l.17.1a2 2 0 0 0 1.8 0L8 12 5 6l.9-.45a2 2 0 0 1 2.09.2l4.02 3a2 2 0 0 0 2.1.2l4.19-2.06a2.41 2.41 0 0 1 1.73-.17L21 7a1.4 1.4 0 0 1 .87 1.99l-.38.76c-.23.46-.6.84-1.07 1.08L7.58 17.2a2 2 0 0 1-1.22.18Z"></path>
    </svg>
  `,
  iconSize: [30, 30],
  iconAnchor: [15, 15], // Center the icon on the point
});

export default function AirportMapElements({ code, airport, }: { code: string, airport: Airport }) {
  const position = parseSingleLatLong(airport.latlon);

  return (
    <>
      <Marker position={position} icon={planeIcon}>
        <Popup>
          <div className="flex justify-between items-center mb-2 z-500">
            <div className="text-lg font-bold tracking-tight text-white">
              {code}
            </div>
          </div>
          <div className="text-sm text-zinc-500">{airport.airport_name}</div>
        </Popup>
      </Marker>
    </>
  );
}
