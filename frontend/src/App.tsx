import { useState, useEffect } from 'react'
import './App.css'
import { useQuery } from '@tanstack/react-query';
import Map from './components/flight/Map.tsx'
import FlightInfoCard from './components/flight/FlightInfoCard.tsx'
import FlightDetailPanel from './components/flight/FlightDetailPanel.tsx'
import { type Flight } from "./helpers/Types";

const fetchFlights = async (): Promise<Record<string, Flight>> => {
  const response = await fetch('http://127.0.0.1:8000/flights');
  if (!response.ok) throw new Error('Network response was not ok');
  return response.json();
};

const fetchAirports = async () => {
  const response = await fetch('http://127.0.0.1:8000/airports');
  if (!response.ok) throw new Error('Network response was not ok');
  return response.json();
}

const fetchFlightById = async (id: number | null): Promise<Flight | null> => {
  if (id === null) return null;
  const response = await fetch(`http://127.0.0.1:8000/flights/${id}`);
  if (!response.ok) throw new Error('Flight not found');
  const data = await response.json();
  return data.flight;
};

function App() {
  const [selectedId, setSelectedId] = useState<number | null>(null);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') setSelectedId(null);
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  const { data: flightData, isLoading: flightsLoading, error: flightError } = useQuery({
    queryKey: ['flights'],
    queryFn: fetchFlights,
    refetchInterval: 10000,
  });

  const { data: airportData, isLoading: airportsLoading, error: airportError } = useQuery({
    queryKey: ['airports'],
    queryFn: fetchAirports,
    refetchInterval: 100000, // 100 seconds in milliseconds
  });

  const { data: selectedFlight } = useQuery<Flight | null, Error>({
    queryKey: ['flight', selectedId],
    queryFn: () => fetchFlightById(selectedId),
    enabled: !!selectedId,
  });

  return (
    <div className="relative w-screen h-screen">
      <Map flights={Object.values(flightData ?? {})} airports={airportData ?? {}} />
      <div className="absolute top-4 right-4 w-96 max-h-[calc(100vh-2rem)] z-[1000] flex flex-col gap-4 transition-all duration-500 ease-in-out">
        {selectedFlight && (
          <FlightDetailPanel
            flight={selectedFlight}
            onClose={() => setSelectedId(null)}
          />
        )}
        <FlightInfoCard
          flights={Object.values(flightData ?? {})}
          selectedId={selectedId ?? undefined}
          onSelect={(id: number) => setSelectedId(id)}
        />
      </div>
    </div>
  )
}

export default App
