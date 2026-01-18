import { type Flight } from "../../helpers/Types";
import { Plane, Users, Package, X } from "lucide-react";

interface FlightDetailPanelProps {
    flight: Flight;
    onClose: () => void;
}

export default function FlightDetailPanel({ flight, onClose }: FlightDetailPanelProps) {
    return (
        <div className="relative py-4 px-6 bg-zinc-900/40 backdrop-blur-md border border-blue-500/30 rounded-xl text-white shadow-2xl overflow-hidden">
            {/* Subtle glow effect */}
            <div className="absolute -top-10 -left-10 w-32 h-32 bg-blue-500/10 blur-3xl pointer-events-none" />

            <button
                onClick={onClose}
                className="absolute top-2 right-2 p-1 text-zinc-600 !bg-transparent hover:text-zinc-300 hover:bg-white/5 rounded-full transition-all outline-none cursor-pointer"
            >
                <X size={16} strokeWidth={2} />
            </button>

            <div className="flex items-center gap-2 mb-4 border-b border-zinc-800 pb-2 mr-4">
                <div className="h-1 w-1 rounded-full bg-blue-500 animate-pulse" />
                <h3 className="text-[10px] font-bold uppercase tracking-[0.2em] text-blue-400">Flight Details</h3>
            </div>

            <div className="grid grid-cols-3 gap-6 relative z-10">
                <div className="flex flex-col gap-0.5">
                    <div className="flex items-center gap-1.5">
                        <Plane size={12} className="text-zinc-500 shrink-0 -translate-y-[0.5px]" />
                        <span className="text-[10px] text-zinc-500 uppercase font-bold tracking-widest">Aircraft</span>
                    </div>
                    <span className="text-sm font-semibold leading-tight">{flight.plane_type}</span>
                </div>

                <div className="flex flex-col gap-0.5">
                    <div className="flex items-center gap-1.5">
                        <Users size={12} className={`${flight.passengers <= 170 ? "text-emerald-500" : flight.passengers <= 235 ? "text-orange-500" : "text-red-500"} shrink-0`} />
                        <span className="text-[10px] text-zinc-500 uppercase font-bold tracking-widest">Passengers</span>
                    </div>
                    <span className="text-sm font-semibold">{flight.passengers}</span>
                </div>

                <div className="flex flex-col gap-0.5">
                    <div className="flex items-center gap-1.5">
                        <Package size={12} className={`${flight.is_cargo ? "text-emerald-500" : "text-red-500"} shrink-0`} />
                        <span className="text-[10px] text-zinc-500 uppercase font-bold tracking-widest">Cargo</span>
                    </div>
                    <span className="text-sm font-semibold">{flight.is_cargo ? "Enabled" : "Disabled"}</span>
                </div>
            </div>
        </div>
    );
}