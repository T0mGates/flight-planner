import { Popup, Polyline } from "react-leaflet";
import { LatLng } from 'leaflet';
import type { Flight } from '@/helpers/Types.ts';
import L from 'leaflet';

export default function FlightMapLine({ flight, positions, colour, onSelect }: { flight: Flight, positions: LatLng[], colour: string, onSelect: (id: number) => void }) {
  if (positions.length == 0) {
    return (<></>);
  }
  return (
    <>
      {/* Invisible, thick Polyline for easier clicking */}
      <Polyline
        positions={positions}
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

      {/* Visible, thin Polyline */}
      <Polyline
        positions={positions}
        pathOptions={{
          color: colour,
          weight: 2.5,
          opacity: 0.3,
          dashArray: '10, 10',
          lineCap: 'round',
          lineJoin: 'round',
          interactive: false
        }}
      />
    </>
  );
}

