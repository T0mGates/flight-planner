import { useState }             from "react";
import { 
        Filter, 
        Calendar, 
        MapPin, 
        Loader2 // This is the standard spinner icon
       }                        from "lucide-react";

import { type FlightFilters }   from "@/helpers/Types";

interface FlightFiltersCardProps {
  filters: FlightFilters;
  setFilters: (filters: FlightFilters) => void;
  isFetching: boolean;
}

export default function FlightFiltersCard({ filters, setFilters, isFetching }: FlightFiltersCardProps) {
  // 1. Local state for "unsaved" changes
  const [localFilters, setLocalFilters] = useState(filters);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setLocalFilters({ ...localFilters, [e.target.name]: e.target.value });
  };

  const applyFilters = () => {
    setFilters(localFilters);
  }

  return (
    <div className="mt-4 p-4 rounded-xl border border-zinc-800 bg-zinc-900/40 flex flex-col gap-6">
      
      {/* 1. Departure Window - Full Width Stack */}
      <div className="flex flex-col gap-3">
        <label className="text-[10px] uppercase font-bold text-zinc-500 tracking-widest flex items-center gap-2">
          <Calendar size={12} className="text-blue-500" /> 
          Departure Window
        </label>
        
        <div className="flex flex-col gap-3">
          <div className="flex flex-col gap-1.5">
            <span className="text-[9px] text-zinc-600 font-bold ml-1">FROM</span>
            <input 
              type="datetime-local" 
              name="startDateTime"
              value={localFilters.startDateTime}
              onChange={handleChange}
              className="w-full bg-zinc-950 border border-zinc-800 rounded-lg px-4 py-2.5 text-sm text-zinc-200 [color-scheme:dark] focus:ring-1 focus:ring-blue-500 outline-none transition-all"
            />
          </div>

          <div className="flex flex-col gap-1.5">
            <span className="text-[9px] text-zinc-600 font-bold ml-1">TO</span>
            <input 
              type="datetime-local" 
              name="endDateTime"
              value={localFilters.endDateTime}
              onChange={handleChange}
              className="w-full bg-zinc-950 border border-zinc-800 rounded-lg px-4 py-2.5 text-sm text-zinc-200 [color-scheme:dark] focus:ring-1 focus:ring-blue-500 outline-none transition-all"
            />
          </div>
        </div>
      </div>

      {/* 2. Location - Full Width Stack */}
      <div className="flex flex-col gap-3">
        <label className="text-[10px] uppercase font-bold text-zinc-500 tracking-widest flex items-center gap-2">
          <MapPin size={12} className="text-blue-500" /> 
          Location Filters
        </label>
        <div className="grid grid-cols-2 gap-3">
          <input 
            type="text" 
            name="origin" 
            placeholder="Origin (CYYZ)"
            value={localFilters.origin}
            onChange={handleChange}
            className="bg-zinc-950 border border-zinc-800 rounded-lg px-4 py-2.5 text-sm text-zinc-200 uppercase placeholder:text-zinc-700 focus:border-zinc-600 outline-none"
          />
          <input 
            type="text" 
            name="destination" 
            placeholder="Dest (CYVR)"
            value={localFilters.destination}
            onChange={handleChange}
            className="bg-zinc-950 border border-zinc-800 rounded-lg px-4 py-2.5 text-sm text-zinc-200 uppercase placeholder:text-zinc-700 focus:border-zinc-600 outline-none"
          />
        </div>
      </div>

      {/* 3. Action Button */}
      <button 
        onClick={() => applyFilters()}
        disabled={isFetching}
        className="w-full flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-500 disabled:bg-blue-900/30 disabled:text-zinc-600 text-white text-xs font-bold uppercase tracking-widest py-3 rounded-lg transition-all active:scale-[0.98] cursor-pointer"
      >
        {isFetching ? (
          <>
            <Loader2 size={16} className="animate-spin" />
            Updating Monitor...
          </>
        ) : (
          <>
            <Filter size={16} />
            Apply Filters
          </>
        )}
      </button>
    </div>
  );
}