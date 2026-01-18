import { useQuery } from "@tanstack/react-query";
import { motion, AnimatePresence } from "framer-motion";
import { Activity, CheckCircle2, AlertCircle, BarChart3, ArrowRight } from "lucide-react";

interface StatusData {
  status: string;
  progress: number;
  result: string;
  Message: string;
  "Total Iterations": number;
  "Current Iteration": number;
  "Active Conflicts": number;
  "Total Conflicts": number;
  "Optimization Changes": number;
}

export default function AnalysisStatus({ id }: { id: string }) {
  const { data, error } = useQuery<StatusData>({
    queryKey: ["analysisStatus", id],
    queryFn: async () => {
      const response = await fetch(`http://localhost:8000/job_status/${id}`);
      if (!response.ok) throw new Error("Status check failed");
      return response.json();
    },
    // Poll every 2 seconds while the status is not "completed"
    refetchInterval: (query) => 
      query.state.data?.status === "completed" ? false : 2000,
  });

  if (error) return (
    <div className="p-3 rounded-xl border border-red-500/30 bg-red-500/5 text-red-400 text-[10px] flex items-center gap-2">
      <AlertCircle size={14} /> Failed to track worker #{id}
    </div>
  );

  if (!data) return null;

  const isCompleted       = data.status === "completed";
  const completionPercent = (data["Current Iteration"]/data["Total Iterations"]) * 100;

  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      className={`w-64 p-4 rounded-xl border backdrop-blur-md transition-colors duration-500 ${
        isCompleted ? "border-emerald-500/30 bg-emerald-500/5" : "border-blue-500/30 bg-blue-500/5"
      }`}
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          {isCompleted ? (
            <CheckCircle2 size={14} className="text-emerald-400" />
          ) : (
            <Activity size={14} className="text-blue-400 animate-pulse" />
          )}
          <span className={`text-[10px] font-bold uppercase tracking-widest ${isCompleted ? 'text-emerald-400' : 'text-blue-400'}`}>
            {isCompleted ? "Optimizations Finished" : "Calculating Optimizations"}
          </span>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="h-1 w-full bg-zinc-800 rounded-full overflow-hidden mb-3">
        <motion.div 
          className={`h-full ${isCompleted ? 'bg-emerald-500' : 'bg-blue-500'}`}
          initial={{ width: 0 }}
          animate={{ width: `${isCompleted ? 100 : completionPercent}%` }}
        />
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-2 gap-y-3 gap-x-4 mb-3">
        <div className="flex flex-col">
          <span className="text-[8px] text-zinc-500 uppercase font-bold">Solved | Conflicts</span>
          <span className="text-xs font-mono text-zinc-200">
            {Number.isInteger(data["Total Conflicts"]) && Number.isInteger(data["Active Conflicts"])
            ?
              `${data["Total Conflicts"] - data["Active Conflicts"]} | ${data["Total Conflicts"]}`
            :
              `N/A | N/A`
            }
            
          </span>
        </div>
        <div className="flex flex-col items-end">
          <span className="text-[8px] text-zinc-500 uppercase font-bold">Changes</span>
          <span className="text-xs font-mono text-blue-400">+{Number.isInteger(data["Optimization Changes"]) ? data["Optimization Changes"] : 0}</span>
        </div>
        <div className="flex flex-col">
          <span className="text-[8px] text-zinc-500 uppercase font-bold">Iteration</span>
          <span className="text-xs font-mono text-zinc-200">
            {data["Current Iteration"]} <span className="text-zinc-600 text-[10px]">of {data["Total Iterations"]}</span>
          </span>
        </div>
        <div className="flex flex-col items-end">
          <span className="text-[8px] text-zinc-500 uppercase font-bold">Status</span>
          <span className="text-xs font-mono text-zinc-200 capitalize">{data.status}</span>
        </div>
      </div>

      {/* Footer & Action Area */}
      <div className="pt-4 border-t border-white/5 flex flex-col gap-4">
        
        {/* Status Message Section */}
        <div className="flex items-start gap-2">
          <p className="text-[9px] text-zinc-500 leading-relaxed italic flex-1">
            {data.Message || data.result}
          </p>
        </div>

        {/* Centered Action Button */}
        <AnimatePresence>
          {isCompleted && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 10 }}
              className="flex justify-center w-full"
            >
              <button
                onClick={() => console.log("Finalizing changes...")}
                className="group flex items-center justify-center gap-3 px-8 py-2.5 bg-blue-600 hover:bg-blue-500 text-white rounded-lg shadow-[0_0_20px_rgba(59,130,246,0.3)] transition-all active:scale-95 w-full"
              >
                <span className="text-[10px] font-bold uppercase tracking-[0.2em]">Apply Changes</span>
                <ArrowRight size={14} className="group-hover:translate-x-1 transition-transform" />
              </button>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </motion.div>
  );
}