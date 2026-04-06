import { useState } from "react";
import type { Finding } from "../types";
import ConfidenceBadge from "./ConfidenceBadge";

const COLUMNS = [
  { key: "new", label: "New", statuses: ["new"] },
  { key: "triaged", label: "Triaged", statuses: ["queued"] },
  { key: "working", label: "Devin Working", statuses: ["in_progress"] },
  { key: "pr", label: "PR Created", statuses: ["pr_created"] },
  { key: "done", label: "Done / Escalated", statuses: ["merged", "escalated", "dismissed", "rejected"] },
];

const SEV_BORDER: Record<string, string> = {
  critical: "border-l-red-500",
  high: "border-l-orange-400",
  medium: "border-l-amber-400",
  low: "border-l-blue-400",
};

const SEV_BADGE: Record<string, string> = {
  critical: "bg-red-50 text-red-700 border-red-200",
  high: "bg-orange-50 text-orange-700 border-orange-200",
  medium: "bg-amber-50 text-amber-700 border-amber-200",
  low: "bg-blue-50 text-blue-700 border-blue-200",
};

interface Props {
  findings: Finding[];
  onReject?: (findingId: number, reason: string) => void;
}

function FindingCard({ finding, onReject }: { finding: Finding; onReject?: (id: number, reason: string) => void }) {
  const [showReject, setShowReject] = useState(false);
  const [reason, setReason] = useState("");
  const sev = finding.severity || "medium";

  return (
    <div className={`border border-gray-200 border-l-[3px] ${SEV_BORDER[sev] || "border-l-gray-300"} rounded-lg p-3`}>
      <div className="flex items-center justify-between mb-1.5">
        <span className="text-[11px] font-mono font-bold text-blue-700">{finding.cwe}</span>
        <span className={`text-[9px] font-semibold uppercase px-1.5 py-0.5 rounded border leading-none ${SEV_BADGE[sev] || "bg-gray-50 text-gray-600 border-gray-200"}`}>{sev}</span>
      </div>
      <p className="text-[13px] text-gray-900 font-semibold leading-snug mb-0.5">{finding.rule_name}</p>
      <p className="text-[10px] text-gray-400 font-mono mb-2">{finding.file_path}{finding.start_line ? `:${finding.start_line}` : ""}</p>
      <div className="flex items-center justify-between">
        <ConfidenceBadge score={finding.confidence_score} />
        <div className="flex gap-2">
          {finding.pr_url && <a href={finding.pr_url} target="_blank" rel="noopener noreferrer" className="text-[10px] text-blue-600 hover:text-blue-800 font-medium">PR</a>}
          {finding.devin_session_url && <a href={finding.devin_session_url} target="_blank" rel="noopener noreferrer" className="text-[10px] text-blue-600 hover:text-blue-800 font-medium">Devin</a>}
        </div>
      </div>
      {finding.status === "pr_created" && onReject && (
        <div className="mt-2">
          {!showReject ? (
            <button onClick={() => setShowReject(true)} className="text-[10px] text-red-500 hover:text-red-700 font-medium">Reject & Re-dispatch</button>
          ) : (
            <div className="flex gap-1 items-center">
              <input type="text" value={reason} onChange={(e) => setReason(e.target.value)} placeholder="Reason..." className="flex-1 text-[10px] border border-gray-200 rounded px-1.5 py-0.5 text-gray-700 outline-none focus:ring-1 focus:ring-blue-500" />
              <button onClick={() => { if (reason.trim()) { onReject(finding.id, reason.trim()); setShowReject(false); setReason(""); } }} className="text-[10px] bg-red-500 text-white px-1.5 py-0.5 rounded">Send</button>
              <button onClick={() => { setShowReject(false); setReason(""); }} className="text-[10px] text-gray-400">&times;</button>
            </div>
          )}
        </div>
      )}
      {finding.status === "rejected" && finding.rejection_reason && (
        <p className="text-[10px] text-red-500 mt-1.5">Rejected: {finding.rejection_reason}</p>
      )}
    </div>
  );
}

export default function PipelineFlowView({ findings, onReject }: Props) {
  return (
    <div className="grid grid-cols-5 gap-4">
      {COLUMNS.map((col) => {
        const items = findings.filter((f) => col.statuses.includes(f.status || "new"));
        return (
          <div key={col.key}>
            <div className="flex items-center justify-between mb-3 pb-2 border-b border-gray-200">
              <span className="text-[10px] font-bold text-gray-900 uppercase tracking-wider">{col.label}</span>
              <span className="text-[10px] text-gray-400 font-medium">{items.length}</span>
            </div>
            <div className="space-y-2 min-h-[200px] max-h-[60vh] overflow-y-auto">
              {items.length === 0 && <p className="text-[10px] text-gray-300 text-center pt-8">No findings</p>}
              {items.map((f) => <FindingCard key={f.id} finding={f} onReject={onReject} />)}
            </div>
          </div>
        );
      })}
    </div>
  );
}
