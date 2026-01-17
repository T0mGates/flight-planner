import { Fragment } from 'react'
import { MapContainer, TileLayer, Popup, Marker, Polyline } from 'react-leaflet'
import { LatLng } from 'leaflet'
import 'leaflet/dist/leaflet.css'
import type { Flight } from './Types.ts'
import { parseLatLong } from './Types.ts'


export default function Map({ flights }: { flights: Flight[] }) {
  return (
    <MapContainer center={[56.1304, -106.3468]} zoom={4} scrollWheelZoom={false} className="w-full h-full">
      <TileLayer
        url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
        attribution='&copy; OpenStreetMap contributors &copy; CARTO'
      />
      {flights.map(
        (flight) => <FlightMapElements key={flight.ACID} flight={flight} colour="blue"></FlightMapElements>
      )}
    </MapContainer>
  );
}

// Create all required details on the map related to a particular flight
function FlightMapElements({ flight, colour }: { flight: Flight, colour: string }) {
  const positions: LatLng[] = parseLatLong(flight["route"]);

  for (const pos of positions) {
    if (pos.lat == undefined || pos.lng == undefined) {
      console.log("Position for flight ", flight.ACID, " is fucked.", flight);
    }
  }

  return (
    <Fragment>
      {positions.length > 0 &&
        <>
          <Polyline positions={positions} pathOptions={{ color: colour, weight: 5, opacity: 0.7, dashArray: '10, 5', lineCap: 'round', lineJoin: 'round' }}>
            <Popup>
              <div>
                <strong>Flight {flight.ACID}</strong><br />
                Aircraft: {flight.Plane_type}<br />
                Altitude: 0 ft<br />
                Speed: 0 knots<br />
                Passengers: {flight.passengers}<br />
                Route: {flight.route}
              </div>
            </Popup>
          </Polyline>
          <Marker position={positions[0]}>
            <Popup>
              Flight {flight["ACID"]} departure
            </Popup>
          </Marker>
          <Marker position={positions[positions.length - 1]}>
            <Popup>
              Flight {flight["ACID"]} arrival
            </Popup>
          </Marker>
        </>
      }
    </Fragment  >
  );
}

