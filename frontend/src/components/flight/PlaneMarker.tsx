import { divIcon, LatLng } from "leaflet";
import { Marker } from "react-leaflet";


function createPlaneIcon(heading: number) {
  return divIcon({
    className: 'plane-icon',
    html: `
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200" version="1.1">
          <polygon style="fill:white;transform-box:fill-box;transform-origin:center;transform:rotate(${heading}deg);opacity:0.7" points="183.138438763306,172 16.8615612366939,172 100,28"/>
      </svg>
    `,
    // If you want to make the triangle smaller, need to change size and anchor together
    iconSize: [20, 20],
    iconAnchor: [10, 10]
  });
}

export default function PlaneMarker({ position, heading }: { position: LatLng, heading: number }) {
  return (
    <Marker position={position} icon={createPlaneIcon(heading)} interactive={false} />
  );
}
