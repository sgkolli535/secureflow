import { useState } from "react";
import { triggerPipeline } from "../api";
import type { PipelineRun } from "../types";

export default function PipelineControls({
  lastRun,
  onRunComplete,
}: {
  lastRun: PipelineRun | null;
  onRunComplete: () => void;
}) {
  const [running, setRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleRun = async () => {
    setRunning(true);
    setError(null);
    try {
      await triggerPipeline();
      onRunComplete();
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Pipeline failed");
    } finally {
      setRunning(false);
    }
  };

  return (
    <div className="flex items-center gap-3">
      <button
        onClick={handleRun}
        disabled={running}
        className="bg-blue-700 hover:bg-blue-800 disabled:bg-blue-400 disabled:cursor-not-allowed text-white px-4 py-1.5 rounded-lg text-xs font-semibold transition-colors"
      >
        {running ? "Running..." : "Run Pipeline"}
      </button>
      {lastRun && (
        <span className="text-[10px] text-gray-400">
          Last: <span className={lastRun.status === "completed" ? "text-emerald-600" : lastRun.status === "failed" ? "text-red-600" : "text-amber-600"}>{lastRun.status}</span>
        </span>
      )}
      {error && <span className="text-red-500 text-[10px]">{error}</span>}
    </div>
  );
}
