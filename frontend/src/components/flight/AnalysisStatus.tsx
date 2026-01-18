import * as Sentry from "@sentry/react"
import { useQuery } from "@tanstack/react-query";
import { useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Activity, CheckCircle2, AlertCircle, ArrowRight, ArrowLeft, Save } from "lucide-react";

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

export interface AnalysisStatusProps {
  id: string;
  seeNewChanges: boolean;
  setSeeNewChanges: (seeNewChanges: boolean) => void;
  applyOptimizations: () => void;
}

export default function AnalysisStatus({ id, seeNewChanges, setSeeNewChanges, applyOptimizations }: AnalysisStatusProps) {
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

  useEffect(() => {
    if (error) {
      Sentry.captureException(error);
    }
  }, [error])

  if (error) return (
    <div className="p-3 rounded-xl border border-red-500/30 bg-red-500/5 text-red-400 text-[10px] flex items-center gap-2">
      <AlertCircle size={14} /> Failed to track worker #{id}
    </div>
  );

  if (!data) return null;

  const isCompleted = data.status === "completed";
  const completionPercent = (data["Current Iteration"] / data["Total Iterations"]) * 100;

  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      className={`w-64 p-4 rounded-xl border backdrop-blur-md transition-colors duration-500 ${isCompleted ? "border-emerald-500/30 bg-emerald-500/5" : "border-blue-500/30 bg-blue-500/5"
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
        <div className="flex flex-col text-left">
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
        <div className="flex flex-col text-left">
          <span className="text-[8px] text-zinc-500 uppercase font-bold">Iteration</span>
          <span className="text-xs font-mono text-zinc-200">
            {data["Current Iteration"]} <span className="text-zinc-600 text-[10px]">of {data["Total Iterations"]}</span>
          </span>
        </div>
        <div className="flex flex-col items-end text-right">
          <span className="text-[8px] text-zinc-500 uppercase font-bold">Status</span>
          <span className="text-xs font-mono text-zinc-200 capitalize">{data.status + ((data["Current Iteration"] < data["Total Iterations"]) && data.status == "Completed" ? " Early" : "")}</span>
        </div>
      </div>

      {/* Footer & Action Area */}
      <div className="pt-4 border-t border-white/5 flex flex-col gap-4">

        {/* Status Message Section */}
        <div className="flex items-start gap-2">
          <p className="text-[9px] text-zinc-500 leading-relaxed italic flex-1">
            {isCompleted ? "Finished calculations! Ask your AI assistant for more information." : data.Message || data.result}
          </p>
        </div>

        {/* Centered Action Button */}
        <AnimatePresence>
          {isCompleted && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 10 }}
              className="flex flex-row gap-2 justify-center w-full"
            >
              <button
                onClick={() => applyOptimizations()}
                className="flex-1 group flex items-center justify-center gap-1 px-1 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg shadow-[0_0_15px_rgba(59,130,246,0.2)] transition-all active:scale-95"
              >
                <span className="text-[7px] font-bold uppercase tracking-wider whitespace-nowrap">Apply Changes</span>
                <Save size={12} className="group-hover:translate-x-0.5 transition-transform shrink-0" />
              </button>

              {seeNewChanges
                ?
                <button
                  onClick={() => setSeeNewChanges(false)}
                  className="flex-1 group flex items-center justify-center gap-1 px-1 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg shadow-[0_0_15px_rgba(59,130,246,0.2)] transition-all active:scale-95"
                >
                  <ArrowLeft size={12} className="group-hover:-translate-x-0.5 transition-transform shrink-0" />
                  <span className="text-[7px] font-bold uppercase tracking-wider whitespace-nowrap">See Original</span>
                </button>
                :
                <button
                  onClick={() => setSeeNewChanges(true)}
                  className="flex-1 group flex items-center justify-center gap-1 px-1 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg shadow-[0_0_15px_rgba(59,130,246,0.2)] transition-all active:scale-95"
                >
                  <span className="text-[7px] font-bold uppercase tracking-wider whitespace-nowrap">See Changes</span>
                  <ArrowRight size={12} className="group-hover:translate-x-0.5 transition-transform shrink-0" />
                </button>
              }
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </motion.div>
  );
}
