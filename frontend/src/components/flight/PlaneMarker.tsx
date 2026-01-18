import { divIcon, LatLng } from "leaflet";
import { Marker } from "react-leaflet";
import type { Flight } from "@/helpers/Types";

function createPlaneIcon(heading: number, colour: string) {
  return divIcon({
    className: 'plane-icon',
    html: `
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" style="transform-box:fill-box;transform-origin:center;transform:rotate(${heading - 90}deg);">
        <path d="M407.72,224c-3.4,0-14.79.1-18,.3l-64.9,1.7a1.83,1.83,0,0,1-1.69-.9L193.55,67.56A9,9,0,0,0,186.89,64H160l73,161a2.35,2.35,0,0,1-2.26,3.35l-121.69,1.8a8.06,8.06,0,0,1-6.6-3.1l-37-45c-3-3.9-8.62-6-13.51-6H33.08c-1.29,0-1.1,1.21-.75,2.43L52.17,249.9a16.3,16.3,0,0,1,0,11.9L32.31,333c-.59,1.95-.52,3,1.77,3H52c8.14,0,9.25-1.06,13.41-6.3l37.7-45.7a8.19,8.19,0,0,1,6.6-3.1l120.68,2.7a2.7,2.7,0,0,1,2.43,3.74L160,448h26.64a9,9,0,0,0,6.65-3.55L323.14,287c.39-.6,2-.9,2.69-.9l63.9,1.7c3.3.2,14.59.3,18,.3C452,288.1,480,275.93,480,256S452.12,224,407.72,224Z" style="fill:none;stroke:${colour};stroke-linecap:round;stroke-linejoin:round;stroke-width:32px"/>
      </svg>
    `,
    // If you want to make the triangle smaller, need to change size and anchor together
    iconSize: [20, 20],
    iconAnchor: [10, 10]
  });
}

function calculateCurrentFlightPosition(
  flight: Flight,
  flightPositions: LatLng[],
  currentTime: number
): LatLng {
  if (!flightPositions) {
    // This shouldn't happen
    console.log("No flight positions to calculate plane from");
    return new LatLng(0, 0);
  }
  const elapsedSeconds = currentTime - flight.departure_time;

  if (elapsedSeconds < 0) {
    return flightPositions[0];
  }


  // Keep track of how long the plane would have been in the air for
  let timeAccumulated = 0;
  for (let i = 0; i < flightPositions.length - 1; i++) {
    const segmentStart = flightPositions[i];
    const segmentEnd = flightPositions[i + 1];

    // Convert speed from knots to km/h
    const speedKmh = flight.aircraft_speed * 1.852;

    // Calculate distance for this segment, in meters (convert to km)
    const segmentDistance = segmentStart.distanceTo(segmentEnd) / 1000;

    // Calculate time to fly this segment (in seconds)
    const segmentDuration = (segmentDistance / speedKmh) * 3600;

    // Check if plane is on this segment
    if (elapsedSeconds <= timeAccumulated + segmentDuration) {
      // Plane is currently on this segment
      const timeIntoSegment = elapsedSeconds - timeAccumulated;
      const fraction = timeIntoSegment / segmentDuration;

      // Linear interpolation between start and end
      const lat = segmentStart.lat + (segmentEnd.lat - segmentStart.lat) * fraction;
      const lng = segmentStart.lng + (segmentEnd.lng - segmentStart.lng) * fraction;

      return new LatLng(lat, lng);
    }
  }
  // We're at the end of the flight, return the last position
  return flightPositions[flightPositions.length - 1];
}

export default function PlaneMarker({ position, heading, colour }: { position: LatLng, heading: number, colour: string }) {
  return (
    <Marker position={position} icon={createPlaneIcon(heading, colour)} interactive={false} />
  );
}
