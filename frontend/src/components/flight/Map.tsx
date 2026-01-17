import { MapContainer, TileLayer, } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import type { Flight } from '../../helpers/Types.ts';
import FlightMapElements from "./FlightMapElements.tsx"

export default function Map({ flights }: { flights: Flight[] }) {
  return (
    <MapContainer center={[56.1304, -106.3468]} zoom={4} scrollWheelZoom={true} className="w-full h-full">
      <TileLayer
        url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
        attribution='&copy; OpenStreetMap contributors &copy; CARTO'
      />
      {flights.map(
        (flight) => <FlightMapElements key={flight.id} flight={flight}></FlightMapElements>
      )}
    </MapContainer>
  );
}

