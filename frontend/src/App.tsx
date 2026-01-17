import './App.css';

import { useState, useEffect, useCallback }       from 'react';
import { motion, AnimatePresence }                from "framer-motion";
import { useQuery }                               from '@tanstack/react-query';
import Map                                        from './components/flight/Map.tsx';
import FlightInfoCard                             from './components/flight/FlightInfoCard.tsx';
import FlightDetailPanel                          from './components/flight/FlightDetailPanel.tsx';
import { type Flight }                            from "./helpers/Types";
import logo                                       from './assets/plane_logo.png';

// Fetch with filters
const fetchFlights = async ({ queryKey }: any): Promise<Record<string, Flight>> => {
  const [_key, filters] = queryKey;
  
  const params = new URLSearchParams();

  // Only append if the value actually exists
  if (filters.startDateTime) params.append("start",       `${filters.startDateTime}:00Z`);
  if (filters.endDateTime)   params.append("end",         `${filters.endDateTime}:00Z`);
  if (filters.origin)        params.append("origin",      filters.origin.toUpperCase());
  if (filters.destination)   params.append("destination", filters.destination.toUpperCase());

  const response = await fetch(`http://localhost:8000/flights?${params.toString()}`);
  
  if (!response.ok) throw new Error('Failed to fetch flight data');
  return response.json();
};

const fetchAirports = async () => {
  const response = await fetch('http://127.0.0.1:8000/airports');
  if (!response.ok) throw new Error('Network response was not ok');
  return response.json();
}

const fetchFlightById = async (id: number | null): Promise<Flight | null> => {
  if (id === null) return null;
  const response = await fetch(`http://localhost:8000/flights/${id}`);
  if (!response.ok) throw new Error('Flight not found');
  const data = await response.json();
  return data.flight;
};

function App() {
  // DEFAULT FILTERS
  const [filters, setFilters] = useState({
    startDateTime : "",
    endDateTime   : "",
    origin        : "",
    destination   : ""
  });

  const [selectedId, setSelectedId] = useState<number | null>(null);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') setSelectedId(null);
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  const { data: flightData, isLoading: flightsLoading, error: flightError, isFetching: isFetchingFlights } = useQuery({
    queryKey: ['flights', filters],
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
  
  const handleSelect = useCallback((id: number) => {
    setSelectedId(id);
  }, []);

  return (
    <div className="relative w-screen h-screen">
      <div className="absolute bottom-3 left-0 z-[1000] pointer-events-none select-none">
        <img
          src={logo}
          alt="Flight Planner Logo"
          className="h-30 w-auto opacity-80 grayscale contrast-125"
        />
      </div>
      <Map flights={Object.values(flightData ?? {})} airports={airportData ?? {}} onSelectFlight={handleSelect} />
      <div className="absolute top-4 right-4 w-96 max-h-[calc(100vh-2rem)] z-1000 flex flex-col gap-4">
        <AnimatePresence mode="popLayout">
          {selectedFlight && (
            <motion.div
              key="detail-panel" // Key is required for AnimatePresence
              initial={{ opacity: 0, y: -20, scale: 0.95 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: -20, scale: 0.95 }}
              transition={{ duration: 0.3, ease: "easeOut" }}
            >
              <FlightDetailPanel
                flight={selectedFlight}
                onClose={() => setSelectedId(null)}
              />
            </motion.div>
          )}
        </AnimatePresence>
        {/* We also wrap the card so it slides up/down smoothly when the panel above it changes */}
        <motion.div layout transition={{ duration: 0.4, type: "spring", bounce: 0.2 }}>
          <FlightInfoCard
            flights={Object.values(flightData ?? {})}
            filters={filters}
            isFetching={isFetchingFlights}
            setFilters={setFilters}
            selectedId={selectedId ?? undefined}
            onSelect={(id: number) => setSelectedId(id)}
          />
        </motion.div>
      </div>
    </div>
  )
}

export default App
