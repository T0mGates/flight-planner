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

  const { data: flightsData, isLoading, error } = useQuery<Record<string, Flight>, Error>({
    queryKey: ['flights'],
    queryFn: fetchFlights,
    refetchInterval: 10000,
  });

  const { data: selectedFlight } = useQuery<Flight | null, Error>({
    queryKey: ['flight', selectedId],
    queryFn: () => fetchFlightById(selectedId),
    enabled: !!selectedId,
  });

  if (isLoading) return <div className="bg-zinc-950 text-white p-10">Loading flights...</div>;
  if (error) return <div className="bg-zinc-950 text-white p-10">Error loading flight data!</div>;

  const flightsArray = flightsData ? Object.values(flightsData) : [];

  return (
    <div className="relative w-screen h-screen bg-zinc-950 overflow-hidden">
      <Map flights={flightsArray} />

      <div className="absolute top-4 right-4 w-96 max-h-[calc(100vh-2rem)] z-[1000] flex flex-col gap-4 transition-all duration-500 ease-in-out">
        {selectedFlight && (
          <FlightDetailPanel
            flight={selectedFlight}
            onClose={() => setSelectedId(null)}
          />
        )}

        <FlightInfoCard
          flights={flightsArray}
          selectedId={selectedId ?? undefined}
          onSelect={(id) => setSelectedId(id)}
        />
      </div>
    </div>
  )
}

export default App