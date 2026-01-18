import { MapContainer, TileLayer, } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import type { AirportDict, Airport, Flight } from '@/helpers/Types.ts';
import FlightMapElements from "./FlightMapElements.tsx"
import AirportMapElements from './AirportMapElements.tsx';


export default function Map({
  flights,
  airports,
  selectedFlightId,
  onSelectFlight,
  currentTime
}: {
  flights: Flight[],
  airports: AirportDict,
  selectedFlightId: number,
  onSelectFlight: (id: number) => void,
  currentTime: number
}) {
  return (
    <MapContainer center={[56.1304, -106.3468]} zoom={4} scrollWheelZoom={true} className="w-full h-full">
      <TileLayer
        url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
        attribution='&copy; OpenStreetMap contributors &copy; CARTO'
      />
      {flights.map(
        (flight) => (
          <FlightMapElements
            key={flight.id}
            flight={flight}
            airports={airports}
            selectedFlightId={selectedFlightId}
            onSelect={onSelectFlight}
            currentTime={currentTime}
          />
        )
      )}
      {Object.entries(airports).map(
        ([code, airport]) => <AirportMapElements key={code} code={code} airport={airport}></AirportMapElements>
      )}
    </MapContainer >
  );
}

