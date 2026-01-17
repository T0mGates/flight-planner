import { Fragment } from 'react'
import { MapContainer, TileLayer, Popup, Marker, Polyline } from 'react-leaflet'
import { LatLng } from 'leaflet'
import 'leaflet/dist/leaflet.css'
import type { FlightData } from './Types.tsx'
import { parseLatLong } from './Types.tsx'


export default function Map({ flights }: { flights: FlightData[] }) {
  return (
    <MapContainer center={[51.505, -0.09]} zoom={13} scrollWheelZoom={false} style={{ height: "80em", width: "80em" }}>
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      {flights.map(
        (flight) => <FlightMapElements key={flight.ACID} flight={flight} colour="blue"></FlightMapElements>
      )}
    </MapContainer>
  );
}

// Create all required details on the map related to a particular flight
function FlightMapElements({ flight, colour }: { flight: FlightData, colour: string }) {
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
          <Polyline positions={positions} color={colour}>
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
    </Fragment>
  );
}

