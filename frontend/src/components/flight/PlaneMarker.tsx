import { divIcon, LatLng } from "leaflet";
import { Marker } from "react-leaflet";


function createPlaneIcon(heading: number) {
  return divIcon({
    className: 'plane-icon',
    html: `
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200" version="1.1">
          <polygon style="fill:white;transform-box:fill-box;transform-origin:center;transform:rotate(${heading}deg);opacity:0.9" points="25,200 175,200 100,0 "/>
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
