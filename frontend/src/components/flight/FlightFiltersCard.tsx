import { useState } from "react";
import {
  Filter,
  Calendar,
  MapPin,
  Loader2,
  ChevronDown,
  ChevronUp,
  RotateCcw
} from "lucide-react";

import { type FlightFilters } from "@/helpers/Types";

interface FlightFiltersCardProps {
  filters: FlightFilters;
  setFilters: (filters: FlightFilters) => void;
  isFetching: boolean;
}

export default function FlightFiltersCard({ filters, setFilters, isFetching }: FlightFiltersCardProps) {
  const [localFilters, setLocalFilters] = useState(filters);

  const [openSections, setOpenSections] = useState({
    dates: false,
    location: false
  });

  // Helper to count active filters in a section
  const dateCount = [localFilters.startDateTime, localFilters.endDateTime].filter(Boolean).length;
  const locCount = [localFilters.origin, localFilters.destination].filter(Boolean).length;
  const totalCount = dateCount + locCount;

  const toggleSection = (key: "dates" | "location") => {
    setOpenSections(prev => ({ ...prev, [key]: !prev[key] }));
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setLocalFilters({ ...localFilters, [e.target.name]: e.target.value });
  };

  const handleReset = () => {
    const reset = { startDateTime: "", endDateTime: "", origin: "", destination: "" };
    setLocalFilters(reset);
    setFilters(reset);
  };

  return (
    <div className="mt-2 flex flex-col gap-3 overflow-visible">

      {/* 1. Departure Window Dropdown */}
      <div
        className={`rounded-xl border transition-all duration-300 bg-zinc-900/40 
          ${openSections.dates
            ? "border-blue-500/50 shadow-[0_0_15px_rgba(59,130,246,0.25)] ring-1 ring-blue-500/20"
            : "border-zinc-800 hover:border-zinc-700 shadow-none"
          }`}
      >
        <button
          onClick={() => toggleSection("dates")}
          className="w-full flex items-center justify-between px-4 py-3 rounded-xl outline-none cursor-pointer"
        >
          <div className="flex items-center gap-2">
            <Calendar size={14} className={dateCount > 0 ? "text-blue-400" : "text-zinc-500"} />
            <span className="text-[10px] uppercase font-bold text-zinc-400 tracking-widest">Departure Window</span>
            {dateCount > 0 && (
              <span className="ml-1 px-1.5 py-0.5 rounded-full bg-blue-500/20 text-blue-400 text-[9px] font-mono">
                {dateCount}
              </span>
            )}
          </div>
          {openSections.dates ? <ChevronUp size={14} className="text-zinc-600" /> : <ChevronDown size={14} className="text-zinc-600" />}
        </button>

        {openSections.dates && (
          <div className="px-4 pb-4 pt-2 flex flex-col gap-3 animate-in fade-in slide-in-from-top-1 duration-200">
            <div className="flex flex-col gap-1.5">
              <span className="text-[9px] text-zinc-600 font-bold ml-1 uppercase">From</span>
              <input
                type="datetime-local"
                name="startDateTime"
                value={localFilters.startDateTime}
                onChange={handleChange}
                className="w-full bg-zinc-950 border border-zinc-800 rounded-lg px-3 py-2 text-xs text-zinc-200 scheme-dark outline-none focus:border-blue-500/50 transition-colors"
              />
            </div>
            <div className="flex flex-col gap-1.5">
              <span className="text-[9px] text-zinc-600 font-bold ml-1 uppercase">To</span>
              <input
                type="datetime-local"
                name="endDateTime"
                value={localFilters.endDateTime}
                onChange={handleChange}
                className="w-full bg-zinc-950 border border-zinc-800 rounded-lg px-3 py-2 text-xs text-zinc-200 scheme-dark outline-none focus:border-blue-500/50 transition-colors"
              />
            </div>
          </div>
        )}
      </div>

      {/* 2. Location Dropdown */}
      <div
        className={`rounded-xl border transition-all duration-300 bg-zinc-900/40 
          ${openSections.location
            ? "border-blue-500/50 shadow-[0_0_15px_rgba(59,130,246,0.25)] ring-1 ring-blue-500/20"
            : "border-zinc-800 hover:border-zinc-700 shadow-none"
          }`}
      >
        <button
          onClick={() => toggleSection("location")}
          className="w-full flex items-center justify-between px-4 py-3 rounded-xl outline-none cursor-pointer"
        >
          <div className="flex items-center gap-2">
            <MapPin size={14} className={locCount > 0 ? "text-blue-400" : "text-zinc-500"} />
            <span className="text-[10px] uppercase font-bold text-zinc-400 tracking-widest">Location Filters</span>
            {locCount > 0 && (
              <span className="ml-1 px-1.5 py-0.5 rounded-full bg-blue-500/20 text-blue-400 text-[9px] font-mono">
                {locCount}
              </span>
            )}
          </div>
          {openSections.location ? <ChevronUp size={14} className="text-zinc-600" /> : <ChevronDown size={14} className="text-zinc-600" />}
        </button>

        {openSections.location && (
          <div className="px-4 pb-4 pt-2 grid grid-cols-2 gap-3 animate-in fade-in slide-in-from-top-1 duration-200">
            <div className="flex flex-col gap-1.5 col-span-1">
              <span className="text-[8px] text-zinc-600 font-bold ml-1">ORIGIN</span>
              <input
                type="text"
                name="origin"
                placeholder="CYYZ"
                value={localFilters.origin}
                onChange={handleChange}
                className="bg-zinc-950 border border-zinc-800 rounded-lg px-3 py-2 text-xs text-zinc-200 uppercase placeholder:text-zinc-800 outline-none focus:border-blue-500/50 transition-colors"
              />
            </div>
            <div className="flex flex-col gap-1.5 col-span-1">
              <span className="text-[8px] text-zinc-600 font-bold ml-1">DESTINATION</span>
              <input
                type="text"
                name="destination"
                placeholder="CYVR"
                value={localFilters.destination}
                onChange={handleChange}
                className="bg-zinc-950 border border-zinc-800 rounded-lg px-3 py-2 text-xs text-zinc-200 uppercase placeholder:text-zinc-800 outline-none focus:border-blue-500/50 transition-colors"
              />
            </div>
          </div>
        )}
      </div>

      {/* 3. Action Buttons Row */}
      <div className="flex gap-2 mt-2">
        {totalCount > 0 && (
          <button
            onClick={handleReset}
            className="px-3 rounded-lg border border-zinc-800 bg-zinc-900/50 hover:bg-zinc-800 text-zinc-400 hover:text-zinc-200 transition-all"
            title="Reset Filters"
          >
            <RotateCcw size={14} />
          </button>
        )}
        <button
          onClick={() => setFilters(localFilters)}
          className="flex-1 flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-500 disabled:bg-blue-900/30 disabled:text-zinc-600 text-white text-[10px] font-bold uppercase tracking-widest py-2.5 rounded-lg transition-all active:scale-[0.95]"
        >
          Apply Filters
        </button>
      </div>
    </div>
  );
}
