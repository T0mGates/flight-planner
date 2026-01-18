import { AnimatePresence, motion } from "framer-motion";
import { type Flight, type FlightFilters, type FlightDiff } from "../../helpers/Types";
import FlightFiltersCard from "./FlightFiltersCard";
import {
  Card,
  CardContent,
  CardHeader,
} from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { PlaneTakeoff, PlaneLanding, Hash } from "lucide-react";

interface FlightInfoCardProps {
  flights: Flight[];
  selectedId?: string;
  onSelect: (acid: string) => void;
  filters: FlightFilters;
  setFilters: (filters: FlightFilters) => void;
  isFetching: boolean;
  flightDiffs: Record<string, FlightDiff> | undefined;
}

export default function FlightInfoCard({ flights, selectedId, onSelect, filters, setFilters, isFetching, flightDiffs }: FlightInfoCardProps) {
  return (
    <Card className="w-full shadow-2xl border-zinc-800 bg-zinc-950/40 backdrop-blur-md text-zinc-50 rounded-xl">

      {/* Upper title portion of the card */}
      <CardHeader className="pb-3 border-b border-zinc-900">
        <FlightFiltersCard filters={filters} setFilters={setFilters} isFetching={isFetching} />
      </CardHeader>

      <CardContent className="pt-4 bg-transparent">
        <ScrollArea className="h-125 pr-4">
          <div className="flex flex-col gap-4">
            {flights.map((flight) => {
              const diff      = flightDiffs?.[flight.ACID];
              const hasDiffs  = diff?.has_differences;
              const isDelayed = diff?.was_delayed;

              return (
                <div
                  key={`fic:${flight.ACID}`}
                  onClick={() => onSelect(flight.ACID)}
                  className={`flex flex-col rounded-xl border transition-all cursor-pointer overflow-hidden relative ${
                    selectedId === flight.ACID
                      ? "border-blue-500 bg-blue-500/10 shadow-[0_0_15px_rgba(59,130,246,0.1)]"
                      : "border-zinc-800 bg-zinc-900/20 hover:border-zinc-500"
                  }`}
                >
                  {/* 1. TOP RIGHT INDICATOR (Differences Found) */}
                  {hasDiffs && (
                    <div className="absolute top-1 right-2 flex items-center gap-1.5 z-20">
                      <span className="text-[8px] font-bold text-emerald-400 uppercase tracking-tighter bg-emerald-500/10 px-1.5 py-0.5 rounded border border-emerald-500/20">
                        Optimized
                      </span>
                      <div className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse shadow-[0_0_8px_rgba(16,185,129,0.6)]" />
                    </div>
                  )}

                  {/* ID BAR AT THE TOP */}
                  <div className="bg-zinc-900/80 px-3 py-1.5 border-b border-zinc-800 flex items-center gap-2">
                    <Hash size={10} className="text-blue-500" />
                    <span className="text-[10px] font-mono font-bold tracking-widest text-zinc-400">
                      ACID:
                      <span className="text-blue-400">{` ${flight.ACID}`}</span>
                    </span>
                  </div>

                  {/* Flight Card Contents */}
                  <div className="p-4 flex items-center justify-between gap-2">
                    {/* Left: Departure */}
                    <div className="flex flex-col flex-1 items-start">
                      <span className="text-[10px] text-zinc-500 uppercase font-bold tracking-tighter mb-1 flex items-center gap-1">
                        <PlaneTakeoff size={12} /> From
                      </span>
                      <span className="text-lg font-semibold text-zinc-100 leading-tight">
                        {flight.departure_airport}
                      </span>
                    </div>

                    {/* Middle: Arrow and Detailed Departure Info */}
                    <div className="flex flex-col items-center justify-center min-w-30 relative">
                      
                      {/* 2. DELAYED TAG (Above Arrow) */}
                      <AnimatePresence>
                        {isDelayed && (
                          <motion.div 
                            initial={{ opacity: 0, y: 5 }}
                            animate={{ opacity: 1, y: 0 }}
                            className="absolute -top-3 flex items-center gap-1 bg-red-500/10 px-2 py-0.5 rounded-full border border-red-500/30"
                          >
                            <span className="text-[7px] font-black text-red-500 uppercase tracking-widest">Delayed</span>
                          </motion.div>
                        )}
                      </AnimatePresence>

                      <span className={`mt-2 text-xl font-light leading-none ${isDelayed ? 'text-red-900/80' : 'text-zinc-700'}`}>→</span>

                      <div className="mt-2 flex flex-col items-center gap-0.5">
                        <span className="text-[9px] text-zinc-600 uppercase font-bold tracking-widest">Departure</span>
                        <div className={`flex flex-col items-center border rounded px-2 py-1 transition-colors ${
                          isDelayed ? 'bg-red-500/5 border-red-500/20' : 'bg-blue-500/5 border-blue-500/10'
                        }`}>
                          <span className={`text-[11px] font-mono font-bold leading-none ${isDelayed ? 'text-red-400' : 'text-blue-400'}`}>
                            {typeof flight.departure_time === 'number'
                              ? new Date(flight.departure_time * 1000).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: true })
                              : '00:00'}
                          </span>
                          <span className="text-[9px] font-mono text-zinc-500 mt-0.5 leading-none">
                            {typeof flight.departure_time === 'number'
                              ? new Date(flight.departure_time * 1000).toLocaleDateString([], { month: 'short', day: 'numeric', year: 'numeric'})
                              : '---'}
                          </span>
                        </div>
                      </div>
                    </div>

                    {/* Right: Arrival */}
                    <div className="flex flex-col flex-1 items-end">
                      <span className="text-[10px] text-zinc-500 uppercase font-bold tracking-tighter mb-1 flex items-center justify-end gap-1">
                        To <PlaneLanding size={12} />
                      </span>
                      <span className="text-lg font-semibold text-zinc-100 leading-tight">
                        {flight.arrival_airport}
                      </span>
                    </div>
                  </div>
                </div>
              );
            })}

          </div>

        </ScrollArea>
      </CardContent>
    </Card>
  );
}
