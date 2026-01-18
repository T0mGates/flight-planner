import './App.css';

import { Play, Loader2 } from "lucide-react";
import { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from "framer-motion";
import { useQuery } from '@tanstack/react-query';
import Map from './components/flight/Map.tsx';
import FlightInfoCard from './components/flight/FlightInfoCard.tsx';
import FlightDetailPanel from './components/flight/FlightDetailPanel.tsx';
import { type Flight } from "./helpers/Types";
import TimeControls from './components/flight/TimeControls.tsx';
import { getFirstFlight, getLastFlight } from './helpers/Flights.ts';
import AnalysisStatus from './components/flight/AnalysisStatus.tsx';
import logo from './assets/plane_logo.png';

// Fetch with filters
const fetchFlights = async ({ queryKey }: any): Promise<Record<string, Flight>> => {
  const [_key, filters, seeNewChanges, workerId] = queryKey;

  const params = new URLSearchParams();

  const toUTC = (dateStr: string) => {
    if (!dateStr) {
      return null;
    }
    // Converts "2026-05-03T07:00" (Local) -> "2026-05-03T11:00:00.000Z" (UTC)
    return new Date(dateStr).toISOString();
  };

  const startUTC = toUTC(filters.startDateTime);
  const endUTC = toUTC(filters.endDateTime);

  // Only append if the value actually exists
  if (startUTC) params.append("start", startUTC);
  if (endUTC) params.append("end", endUTC);
  if (filters.origin) params.append("origin", filters.origin.toUpperCase());
  if (filters.destination) params.append("destination", filters.destination.toUpperCase());

  const toFetch  = seeNewChanges && workerId != null
  ? 
    `http://localhost:8000/job_status/${workerId}/flight_results?${params.toString()}`
  :
    `http://localhost:8000/flights?${params.toString()}`
  const response = await fetch(toFetch);

  if (!response.ok) throw new Error('Failed to fetch flight data');
  return response.json();
};

const fetchAirports = async () => {
  const response = await fetch('http://localhost:8000/airports');
  if (!response.ok) throw new Error('Network response was not ok');
  return response.json();
}

const fetchFlightById = async (acid: string | null): Promise<Flight | null> => {
  if (acid === null) return null;
  const response = await fetch(`http://localhost:8000/flights/${acid}`);
  if (!response.ok) throw new Error('Flight not found');
  const data = await response.json();
  return data.flight;
};

const startAnalysis = async () => {
  const response = await fetch('http://localhost:8000/start_worker');
  if (!response.ok) throw new Error('Network response was not ok');
  return response.json();
}

function App() {
  // DEFAULT FILTERS
  const [filters, setFilters] = useState({
    startDateTime: "",
    endDateTime: "",
    origin: "",
    destination: ""
  });

  const [seeNewChanges, setSeeNewChanges] = useState(false);

  const [selectedId, setSelectedId] = useState<string | null>(null);

  const {
    data: analysisData,
    isFetching: isAnalyzing,
    refetch: triggerAnalysis,
    isSuccess: analysisStarted
  } = useQuery({
    queryKey: ['startWorker'],
    queryFn: startAnalysis,
    enabled: false, // Prevents automatic execution on mount
    retry: false,
  });

  let workerId = null;
  if (analysisStarted) {
    workerId = analysisData["job_id"];
  }

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') setSelectedId(null);
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  // TODO: handle errors
  const { data: flightData, isLoading: flightsLoading, error: flightError, isFetching: isFetchingFlights } = useQuery({
    queryKey: ['flights', filters, seeNewChanges, workerId],
    queryFn: fetchFlights,
    refetchInterval: 10000,
  });

  // TODO: handle errors
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

  // If select the "old" id, DESELECT it
  const handleSelect = useCallback((acid: string) => {
    setSelectedId(prevId => (prevId === acid ? null : acid));
  }, []);

  // Need start and end times for all flights, for all flights that are loaded
  const [currentDisplayTime, setCurrentDisplayTime] = useState(0);
  // When we load data, provide a sensible current time that's not the Unix epoch
  useEffect(() => {
    if (flightData) {
      setCurrentDisplayTime(getFirstFlight(Object.values(flightData)));
    }
  }, [flightData]);
  const earliestFlightTime = getFirstFlight(Object.values(flightData ?? {}));
  const latestFlightTime = getLastFlight(Object.values(flightData ?? {}), airportData ?? {});

  // Unselect the clicked ID if "apply filters" is clicked
  const handleFilterChange = useCallback((newFilters: any) => {
    setFilters(newFilters);
    setSelectedId(null); // Deselects the flight
  }, []);

  return (
    <div className="relative w-screen h-screen">
      <div className="absolute bottom-4 left-4 z-1000 flex flex-col items-start gap-2">
        <img
          src={logo}
          alt="Logo"
          className="h-30 w-auto object-contain mb-28 opacity-50"
        />
        <TimeControls
          startTimeSeconds={earliestFlightTime}
          endTimeSeconds={latestFlightTime}
          currentTimeSeconds={currentDisplayTime}
          setCurrentTimeSeconds={setCurrentDisplayTime}
          timestep={60}
          intervalTimeout={50}
        />
      </div>
      <Map flights={Object.values(flightData ?? {})} airports={airportData ?? {}} selectedFlightId={selectedId ?? null} onSelectFlight={handleSelect} currentTime={currentDisplayTime} />
      <div className="absolute top-4 right-4 w-96 h-[calc(100vh-2rem)] z-1000 flex flex-col gap-4">
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
        <motion.div
          layout
          transition={{ duration: 0.4, type: "spring", bounce: 0.2 }}
          className="flex-1 min-h-0 overflow-hidden pointer-events-auto rounded-xl"
        >
          <FlightInfoCard
            flights={Object.values(flightData ?? {})}
            filters={filters}
            isFetching={isFetchingFlights}
            setFilters={handleFilterChange}
            selectedId={selectedId ?? undefined}
            onSelect={handleSelect}
          />
        </motion.div>
      </div>

      {/* Top Left Analysis Button, or if a worker is active, separate component */}
      <div className="absolute top-4 left-4 z-1000">
        {workerId ? (
          <AnalysisStatus id={workerId} seeNewChanges={seeNewChanges} setSeeNewChanges={setSeeNewChanges} />
        ) : (
          <motion.button
            onClick={() => triggerAnalysis()}
            disabled={isAnalyzing || analysisStarted}
            // Pulse animation logic
            animate={!(isAnalyzing || analysisStarted) ? {
              boxShadow: [
                "0 0 0px rgba(59, 130, 246, 0)",
                "0 0 20px rgba(59, 130, 246, 0.4)",
                "0 0 0px rgba(59, 130, 246, 0)"
              ],
              borderColor: [
                "rgba(39, 39, 42, 1)",      // border-zinc-800
                "rgba(59, 130, 246, 0.8)",  // blue-500
                "rgba(39, 39, 42, 1)"
              ]
            } : {}}
            transition={{
              duration: 2,
              repeat: Infinity,
              ease: "easeInOut"
            }}
            className={`
        group relative flex items-center gap-3 px-4 py-2.5 rounded-xl border transition-all duration-300
        backdrop-blur-md font-bold uppercase text-[10px] tracking-widest outline-none
        ${isAnalyzing || analysisStarted
                ? "bg-blue-500/10 border-blue-500/50 text-blue-400 cursor-wait"
                : "bg-zinc-950/90 text-white hover:text-blue-400"
              }
      `}
          >
            {/* Icon Logic */}
            <div className="relative flex items-center justify-center">
              {isAnalyzing || analysisStarted ? (
                <Loader2 size={16} className="animate-spin" />
              ) : (
                <Play
                  size={16}
                  className="group-hover:scale-110 transition-transform"
                />
              )}
            </div>

            <div className="flex flex-col items-start leading-none">
              <span className="mb-0.5">
                {isAnalyzing || analysisStarted ? "Analyzing schedule..." : "Start Analysis"}
              </span>
            </div>
          </motion.button>
        )}
      </div>

    </div>
  )
}

export default App
