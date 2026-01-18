import './App.css';

import { Play, Loader2 } from "lucide-react";
import * as Sentry from "@sentry/react";
import { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from "framer-motion";
import { useQuery, useQueryClient } from '@tanstack/react-query';
import Map from './components/flight/Map.tsx';
import FlightInfoCard from './components/flight/FlightInfoCard.tsx';
import FlightDetailPanel from './components/flight/FlightDetailPanel.tsx';
import { type Flight, type FlightDiff } from "./helpers/Types";
import TimeControls from './components/flight/TimeControls.tsx';
import { getFirstFlight, getLastFlight } from './helpers/Flights.ts';
import AnalysisStatus from './components/flight/AnalysisStatus.tsx';
import SchedulerChat from './components/chatbot/SchedulerChat.tsx';

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

  const toFetch = seeNewChanges && workerId != null
    ?
    `http://localhost:8000/job_status/${workerId}/flight_results?${params.toString()}`
    :
    `http://localhost:8000/flights?${params.toString()}`
  const response = await fetch(toFetch);

  if (!response.ok) throw new Error('Failed to fetch flight data');
  return response.json();
};

const fetchFlightDiffs = async ({ queryKey }: any): Promise<Record<string, FlightDiff>> => {
  const [_key, filters, seeNewChanges, workerId] = queryKey;

  if (!seeNewChanges || null == workerId) {
    return {};
  }

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

  const response = await fetch(`http://localhost:8000/compare_flights/${workerId}?${params.toString()}`);

  if (!response.ok) throw new Error('Failed to fetch flight diffs');
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

  const queryClient = useQueryClient();

  const [seeNewChanges, setSeeNewChanges] = useState(false);

  const [selectedId, setSelectedId] = useState<string | null>(null);

  const [isApplying, setIsApplying] = useState(false);

  const {
    data: analysisData,
    error: analysisStartError,
    isFetching: isAnalyzing,
    refetch: triggerAnalysis,
    isSuccess: analysisStarted
  } = useQuery({
    queryKey: ['startWorker'],
    queryFn: startAnalysis,
    enabled: false, // Prevents automatic execution on mount
    retry: false,
  });

  // Put into useEffect to avoid double call in strict mode
  useEffect(() => {
    if (flightError) {
      Sentry.captureException(analysisStartError);
    }
  }, [analysisStartError]);

  let workerId = null;
  if (analysisStarted) {
    workerId = analysisData["job_id"];
  }

  const resetAnalysis = async () => {
    setSeeNewChanges(false);
    // Clean up the analysis query so it's as if we haven't started one
    queryClient.removeQueries({ queryKey: ['startWorker'] });
  }

  const applyOptimizations = async () => {
    setIsApplying(true); // Start loading UI
    try {
      const response = await fetch(`http://localhost:8000/apply_optimization/${workerId}`);
      if (!response.ok) throw new Error("Failed to apply changes");

      // Add extra delay to let the animation look nice
      await new Promise(resolve => setTimeout(resolve, 1500));

      resetAnalysis();
    } catch (error) {
      Sentry.captureException(error);
    } finally {
      setIsApplying(false);
    }
  };

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') setSelectedId(null);
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  const { data: flightData, error: flightError } = useQuery({
    queryKey: ['flights', filters, seeNewChanges, workerId],
    queryFn: fetchFlights,
    refetchInterval: 10000,
  });

  // Linked to fetchFlights
  const { data: flightDiffs, error: diffsError, isFetching: _ } = useQuery({
    queryKey: ['diffs', filters, seeNewChanges, workerId],
    queryFn: fetchFlightDiffs,
    refetchInterval: 10000,
  });

  // Put into useEffect to avoid double call in strict mode
  useEffect(() => {
    if (diffsError) {
      Sentry.captureException(diffsError);
    }
  }, [diffsError]);

  // Put into useEffect to avoid double call in strict mode
  useEffect(() => {
    if (flightError) {
      Sentry.captureException(flightError);
    }
  }, [flightError]);

  const { data: airportData, error: airportError } = useQuery({
    queryKey: ['airports'],
    queryFn: fetchAirports,
    refetchInterval: 100000, // 100 seconds in milliseconds
  });

  // Put into useEffect to avoid double call in strict mode
  useEffect(() => {
    if (airportError) {
      Sentry.captureException(airportError);
    }
  }, [airportError]);

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
      <div className="absolute bottom-4 left-4 z-1000 flex flex-col gap-4 items-start pointer-events-none">
        {/* The Chat is now physically above the controls in the DOM */}
        <div className="w-80 pointer-events-auto">
          <SchedulerChat uuid={workerId} />
        </div>

        {/* The Time Controls stay at the bottom */}
        <div className="pointer-events-auto">
          <TimeControls
            startTimeSeconds={earliestFlightTime}
            endTimeSeconds={latestFlightTime}
            currentTimeSeconds={currentDisplayTime}
            setCurrentTimeSeconds={setCurrentDisplayTime}
            timestep={60}
            intervalTimeout={50}
          />
        </div>
      </div>
      <Map
        flights={Object.values(flightData ?? {})}
        airports={airportData ?? {}}
        selectedFlightId={selectedId ?? null}
        onSelectFlight={handleSelect}
        currentTime={currentDisplayTime}
      />

      {/* Right Sidebar: Details and Info Cards */}
      <div className="absolute top-4 right-4 w-96 h-[calc(100vh-2rem)] z-1000 flex flex-col gap-4">
        <AnimatePresence mode="popLayout">
          {selectedFlight && (
            <motion.div
              key="detail-panel"
              initial={{ opacity: 0, y: -20, scale: 0.95 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: -20, scale: 0.95 }}
              transition={{ duration: 0.3, ease: "easeOut" }}
            >
              <FlightDetailPanel
                flight={selectedFlight}
                onClose={() => setSelectedId(null)}
                diffs={flightDiffs ? flightDiffs[selectedFlight.ACID] : null}
              />
            </motion.div>
          )}
        </AnimatePresence>

        <motion.div
          layout
          transition={{ duration: 0.4, type: "spring", bounce: 0.2 }}
          className="flex-1 min-h-0 overflow-hidden pointer-events-auto rounded-xl"
        >
          <FlightInfoCard
            flights={Object.values(flightData ?? {})}
            filters={filters}
            setFilters={handleFilterChange}
            selectedId={selectedId ?? undefined}
            onSelect={handleSelect}
            flightDiffs={flightDiffs}
          />
        </motion.div>
      </div>

      {/* Top Left Analysis Button, or if a worker is active, separate component */}
      <div className="absolute top-4 left-4 z-1000">
        {isApplying
          ?
          (
            <motion.div
              key="applying-loader"
              initial={{ opacity: 0, scale: 0.9, x: -20 }}
              animate={{ opacity: 1, scale: 1, x: 0 }}
              exit={{ opacity: 0, scale: 0.9, x: 20 }}
              className="relative flex items-center gap-4 px-5 py-3 rounded-xl border border-emerald-500/40 bg-zinc-950/90 backdrop-blur-md shadow-[0_0_30px_rgba(16,185,129,0.15)] overflow-hidden"
            >
              {/* Animated background pulse */}
              <div className="absolute inset-0 bg-emerald-500/5 animate-pulse" />

              <div className="relative">
                <Loader2 size={20} className="text-emerald-400 animate-spin" />
                {/* Outer Glow Ring */}
                <div className="absolute inset-0 text-emerald-400/30 blur-sm animate-pulse">
                  <Loader2 size={20} />
                </div>
              </div>

              <div className="flex flex-col items-start relative z-10">
                <div className="flex items-center gap-2">
                  <span className="text-[10px] font-black text-emerald-400 uppercase tracking-[0.25em] leading-none">
                    Applying
                  </span>
                  <span className="flex gap-0.5">
                    <motion.span
                      animate={{ opacity: [0, 1, 0] }}
                      transition={{ duration: 1.5, repeat: Infinity, times: [0, 0.2, 1] }}
                      className="w-1 h-1 rounded-full bg-emerald-400"
                    />
                    <motion.span
                      animate={{ opacity: [0, 1, 0] }}
                      transition={{ duration: 1.5, repeat: Infinity, times: [0.2, 0.4, 1] }}
                      className="w-1 h-1 rounded-full bg-emerald-400"
                    />
                    <motion.span
                      animate={{ opacity: [0, 1, 0] }}
                      transition={{ duration: 1.5, repeat: Infinity, times: [0.4, 0.6, 1] }}
                      className="w-1 h-1 rounded-full bg-emerald-400"
                    />
                  </span>
                </div>
                <span className="text-[9px] text-zinc-500 font-mono font-medium mt-1 uppercase tracking-tighter">
                  Synchronizing New Flight Schedule...
                </span>
              </div>
            </motion.div>
          )
          :
          workerId ? (
            <AnalysisStatus id={workerId} seeNewChanges={seeNewChanges} setSeeNewChanges={setSeeNewChanges} applyOptimizations={applyOptimizations} />
          ) : (
            <motion.button
              onClick={() => triggerAnalysis()}
              disabled={isAnalyzing || analysisStarted}
              animate={!(isAnalyzing || analysisStarted) ? {
                boxShadow: [
                  "0 0 0px rgba(59, 130, 246, 0)",
                  "0 0 20px rgba(59, 130, 246, 0.4)",
                  "0 0 0px rgba(59, 130, 246, 0)"
                ],
                borderColor: [
                  "rgba(39, 39, 42, 1)",
                  "rgba(59, 130, 246, 0.8)",
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
          )
        }
      </div>
    </div>
  );
}

export default Sentry.withProfiler(App);
