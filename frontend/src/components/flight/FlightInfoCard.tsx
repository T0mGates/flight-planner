import { type Flight } from "@/helpers/Types";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription
} from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { PlaneTakeoff, PlaneLanding, Hash } from "lucide-react";

interface FlightInfoCardProps {
    flights: Flight[];
    selectedId?: number;
    onSelect: (id: number) => void;
}

export default function FlightInfoCard({ flights, selectedId, onSelect }: FlightInfoCardProps) {
    return (
        <Card className="w-full shadow-2xl border-zinc-800 bg-zinc-950/90 backdrop-blur text-zinc-50">

      {/* Upper title portion of the card */}
      <CardHeader className="pb-3 border-b border-zinc-900">
        <div className="flex justify-between items-center">
          <CardTitle className="text-xl font-bold tracking-tight text-white">
            Live Monitor
          </CardTitle>
          {/* Blinking Indicator thingy */}
          <div className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse" title="Live" />
        </div>
        <CardDescription className="text-zinc-500">Real-time flight updates</CardDescription>
      </CardHeader>

            <CardContent className="pt-4 bg-transparent">
                <ScrollArea className="h-[500px] pr-4">
                    <div className="flex flex-col gap-4">
                        {flights.map((flight) => (
                            <div
                                key={flight.id}
                                onClick={() => onSelect(flight.id)}
                                className={`flex flex-col rounded-xl border transition-all cursor-pointer overflow-hidden ${selectedId === flight.id
                                        ? "border-blue-500 bg-blue-500/10 shadow-[0_0_15px_rgba(59,130,246,0.1)]"
                                        : "border-zinc-800 bg-zinc-900/20 hover:border-zinc-500"
                                    }`}
                            >
                        {/* ID BAR AT THE TOP */}
                        <div className="bg-zinc-900/80 px-3 py-1.5 border-b border-zinc-800 flex items-center gap-2">
                            <Hash size={10} className="text-blue-500" />
                            <span className="text-[10px] font-mono font-bold tracking-widest text-zinc-400">
                                ACID: 
                                <span className="text-blue-400">
                                    {flight.ACID}
                                </span>
                                    </span>
                                </div>

                {/* CONTENT BELOW */}
                <div className="p-4 flex items-center justify-between">
                  <div className="flex flex-col">
                    <span className="text-[10px] text-zinc-500 uppercase font-bold tracking-tighter mb-1 flex items-center gap-1">
                      <PlaneTakeoff size={12} /> From
                    </span>
                    <span className="text-lg font-semibold text-zinc-100 leading-tight">
                      {flight.departure_airport}
                    </span>
                  </div>

                  <div className="flex flex-col items-center px-4">
                    <span className="text-zinc-600 text-xl font-light">
                      →
                    </span>
                  </div>

                  <div className="flex flex-col text-right">
                    <span className="text-[10px] text-zinc-500 uppercase font-bold tracking-tighter mb-1 flex items-center justify-end gap-1">
                      To <PlaneLanding size={12} />
                    </span>
                    <span className="text-lg font-semibold text-zinc-100 leading-tight">
                      {flight.arrival_airport}
                    </span>
                  </div>
                </div>
              </div>
            ))}

          </div>

        </ScrollArea>
      </CardContent>
    </Card>
  );
}
