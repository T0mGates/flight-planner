import { type Flight } from "../../helpers/Types";
import { Plane, Users, Package, Info, X } from "lucide-react";

interface FlightDetailPanelProps {
    flight: Flight;
    onClose: () => void;
}

export default function FlightDetailPanel({ flight, onClose }: FlightDetailPanelProps) {
    return (
        <div className="relative py-3 px-6 bg-zinc-900 border border-blue-500/50 rounded-xl text-white shadow-xl 
                        animate-in fade-in zoom-in-95 slide-in-from-top-2 duration-300 ease-out">

            <button
                onClick={onClose}
                className="absolute top-1 right-1 p-0 m-0 !bg-transparent border-none shadow-none appearance-none cursor-pointer text-zinc-600 transition-colors flex items-center justify-center outline-none "
            >
                <X size={14} strokeWidth={1.5} />
            </button>

            <div className="flex items-center gap-2 mb-3 border-b border-zinc-800 pb-2 mr-4">
                <Info size={14} className="text-blue-400" />
                <h3 className="text-xs font-bold uppercase tracking-wider text-blue-400">Flight Details</h3>
            </div>

            <div className="grid grid-cols-3 gap-6">
                <div className="flex flex-col gap-0.5">
                    <div className="flex items-center gap-1.5">
                        <Plane size={12} className="text-zinc-500 shrink-0 -translate-y-[0.5px]" />
                        <span className="text-[10px] text-zinc-500 uppercase font-bold tracking-widest">Aircraft</span>
                    </div>
                    <span className="text-sm font-semibold leading-tight">{flight.plane_type}</span>
                </div>

                <div className="flex flex-col gap-0.5">
                    <div className="flex items-center gap-1.5">
                        <Users size={12} className="text-zinc-500 shrink-0" />
                        <span className="text-[10px] text-zinc-500 uppercase font-bold tracking-widest">Passengers</span>
                    </div>
                    <span className="text-sm font-semibold">{flight.passengers}</span>
                </div>

                <div className="flex flex-col gap-0.5">
                    <div className="flex items-center gap-1.5">
                        <Package size={12} className={`${flight.is_cargo ? "text-emerald-500" : "text-zinc-500"} shrink-0`} />
                        <span className="text-[10px] text-zinc-500 uppercase font-bold tracking-widest">Cargo</span>
                    </div>
                    <span className="text-sm font-semibold">{flight.is_cargo ? "Enabled" : "Disabled"}</span>
                </div>
            </div>
        </div>
    );
}