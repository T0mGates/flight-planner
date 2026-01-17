import './App.css'
import { useQuery } from '@tanstack/react-query';
import Map from './components/flight/Map.tsx'
import FlightInfoCard from './components/flight/FlightInfoCard.tsx'

const fetchFlights = async () => {
  const response = await fetch('http://127.0.0.1:8000/flights');
  if (!response.ok) throw new Error('Network response was not ok');
  return response.json();
};

const fetchAirports = async () => {
  const response = await fetch('http://127.0.0.1:8000/airports');
  if (!response.ok) throw new Error('Network response was not ok');
  return response.json();
}

function App() {
  const { data: flightData, isLoading: flightsLoading, error: flightError } = useQuery({
    queryKey: ['flights'],
    queryFn: fetchFlights,
    refetchInterval: 10000, // 10 seconds in milliseconds
  });

  const { data: airportData, isLoading: airportsLoading, error: airportError } = useQuery({
    queryKey: ['airports'],
    queryFn: fetchAirports,
    refetchInterval: 100000, // 100 seconds in milliseconds
  });


  return (
    <div className="relative w-screen h-screen">
      <Map flights={Object.values(flightData ?? {})} airports={airportData ?? {}} />
      <div className="absolute top-4 right-4 w-96 max-h-[calc(100vh-2rem)] z-[1000]">
        <FlightInfoCard flights={Object.values(flightData ?? {})} />
      </div>
    </div>
  )
}

export default App
