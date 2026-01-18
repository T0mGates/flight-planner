import { type Flight, type FlightDiff } from "../../helpers/Types";
import { Plane, Users, Package, X, Clock, Zap, Mountain, AlertTriangle } from "lucide-react";

interface FlightDetailPanelProps {
    flight: Flight;
    onClose: () => void;
    diffs: FlightDiff | null
}

export default function FlightDetailPanel({ flight, onClose, diffs }: FlightDetailPanelProps) {
    const hasDiffData = diffs && diffs.has_differences;

    return (
        <div className={`
            relative py-4 px-6 bg-zinc-950/90 backdrop-blur-xl border border-blue-500/30 rounded-xl text-white shadow-2xl 
            transition-all duration-500 ease-out
            ${hasDiffData ? 'w-[560px] -translate-x-[176px]' : 'w-full'}
        `}>
            {/* 1. Use translate-x instead of -ml for smoother hardware-accelerated movement */}
            
            <div className="absolute -top-10 -left-10 w-32 h-32 bg-blue-500/10 blur-3xl pointer-events-none" />

            <button
                onClick={onClose}
                className="absolute top-2 right-2 p-1 text-zinc-600 !bg-transparent hover:text-zinc-300 hover:bg-white/5 rounded-full transition-all outline-none cursor-pointer z-50"
            >
                <X size={16} strokeWidth={2} />
            </button>

            <div className={`grid ${hasDiffData ? 'grid-cols-2 gap-8' : 'grid-cols-1'} relative z-10`}>
                
                {/* LEFT SECTION */}
                <div className="flex flex-col min-w-0">
                    <div className="flex items-center gap-2 mb-4 border-b border-zinc-800 pb-2">
                        <div className="h-1 w-1 rounded-full bg-blue-500 animate-pulse" />
                        <h3 className="text-[9px] font-bold uppercase tracking-[0.2em] text-blue-400">Flight Details</h3>
                    </div>

                    <div className="grid grid-cols-3 gap-4 justify-items-center">
                        <DetailItem icon={<Plane size={12} />} label="Aircraft" value={flight.plane_type} />
                        
                        {/* 2. Explicitly wrapping the Users icon logic to ensure render */}
                        <DetailItem 
                            icon={<Users size={12} className={flight.passengers <= 170 ? "text-emerald-500" : flight.passengers <= 250 ? "text-orange-500" : "text-red-500"} />} 
                            label="Passengers" 
                            value={flight.passengers} 
                        />
                        
                        <DetailItem 
                            icon={<Package size={12} className={flight.is_cargo ? "text-emerald-500" : "text-red-500"} />} 
                            label="Cargo" 
                            value={flight.is_cargo ? "YES" : "NO"} 
                        />
                    </div>
                </div>

                {/* RIGHT SECTION */}
                {hasDiffData && (
                    <div className="flex flex-col border-l border-zinc-800 pl-8 min-w-0">
                        <div className="flex items-center justify-between mb-4 border-b border-zinc-800 pb-2">
                            <div className="flex items-center gap-2">
                                <div className="h-1 w-1 rounded-full bg-orange-500" />
                                <h3 className="text-[9px] font-bold uppercase tracking-[0.2em] text-orange-400">Flight Diffs</h3>
                            </div>
                        </div>

                        <div className="grid grid-cols-3 gap-4 justify-items-center">
                            <DetailItem 
                                icon={<Clock size={12} className="text-zinc-500" />} 
                                label="Time" 
                                value={`${diffs.departure_time_diff == 0 ? "N/A" : (diffs.departure_time_diff > 0 ? '+' : diffs.departure_time_diff < 0 ? '-' : '') + Math.abs(Math.floor(diffs.departure_time_diff/60)) + "m"}`}
                            />
                            <DetailItem 
                                icon={<Zap size={12} className="text-yellow-500" />} 
                                label="Speed" 
                                value={`${diffs.average_speed_diff == 0 ? "N/A" : (diffs.average_speed_diff > 0 ? '+' : '') + diffs.average_speed_diff + "NM"}`}
                            />
                            <DetailItem 
                                icon={<Mountain size={12} className="text-blue-500" />} 
                                label="Alt." 
                                value={`${diffs.average_altitude_diff == 0 ? "N/A" : (diffs.average_altitude_diff > 0 ? '+' : '') + diffs.average_altitude_diff + "ft"}`}
                            />
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}

function DetailItem({ icon, label, value, valueClassName = "text-zinc-100" }: { icon: React.ReactNode, label: string, value: string | number, valueClassName?: string }) {
    return (
        <div className="flex flex-col gap-1 min-w-0 items-center"> {/* Added items-center here */}
            <div className="flex items-center gap-1.5 text-zinc-500">
                <div className="shrink-0 flex items-center justify-center w-3 h-3">
                    {icon}
                </div>
                <span className="text-[8px] uppercase font-bold tracking-widest truncate">{label}</span>
            </div>
            <span className={`text-xs font-semibold leading-tight font-mono truncate ${valueClassName}`}>{value}</span>
        </div>
    );
}