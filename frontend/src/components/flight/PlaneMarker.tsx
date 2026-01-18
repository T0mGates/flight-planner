import { divIcon, LatLng } from "leaflet";
import { Marker } from "react-leaflet";
import type { Flight } from "@/helpers/Types";

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

export default function PlaneMarker({ position, heading }: { position: LatLng, heading: number }) {
  return (
    <Marker position={position} icon={createPlaneIcon(heading)} interactive={false} />
  );
}
