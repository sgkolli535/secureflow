import { useState } from "react";
import type { Finding } from "../types";
import ConfidenceBadge from "./ConfidenceBadge";

const SEV_BADGE: Record<string, string> = {
  critical: "bg-red-50 text-red-700 border border-red-200",
  high: "bg-orange-50 text-orange-700 border border-orange-200",
  medium: "bg-amber-50 text-amber-700 border border-amber-200",
  low: "bg-blue-50 text-blue-700 border border-blue-200",
};

const STATUS_BADGE: Record<string, string> = {
  new: "bg-gray-50 text-gray-600 border border-gray-200",
  queued: "bg-blue-50 text-blue-700 border border-blue-200",
  in_progress: "bg-amber-50 text-amber-700 border border-amber-200",
  pr_created: "bg-green-50 text-green-700 border border-green-200",
  merged: "bg-emerald-50 text-emerald-700 border border-emerald-200",
  escalated: "bg-red-50 text-red-700 border border-red-200",
  dismissed: "bg-gray-50 text-gray-500 border border-gray-200",
  rejected: "bg-red-50 text-red-600 border border-red-200",
};

function Badge({ text, colorClass }: { text: string; colorClass: string }) {
  return (
    <span className={`inline-block px-2 py-0.5 rounded text-[10px] font-semibold leading-none whitespace-nowrap ${colorClass}`}>
      {text.replace(/_/g, " ").toUpperCase()}
    </span>
  );
}

export default function FindingRow({
  finding,
  onReject,
}: {
  finding: Finding;
  onReject?: (findingId: number, reason: string) => void;
}) {
  const [showReject, setShowReject] = useState(false);
  const [reason, setReason] = useState("");
  const sev = finding.severity || "medium";
  const status = finding.status || "new";

  return (
    <tr className="border-b border-gray-100 hover:bg-gray-50/40 transition-colors">
      <td className="px-4 py-3">
        <Badge text={sev} colorClass={SEV_BADGE[sev] || SEV_BADGE.medium} />
      </td>
      <td className="px-4 py-3 font-mono text-xs text-gray-500">{finding.cwe || "\u2014"}</td>
      <td className="px-4 py-3">
        <div className="text-[13px] text-gray-900 font-medium">{finding.rule_name}</div>
        <div className="text-[11px] text-gray-400 font-mono mt-0.5">{finding.file_path}:{finding.start_line}</div>
      </td>
      <td className="px-4 py-3">
        <Badge text={status} colorClass={STATUS_BADGE[status] || STATUS_BADGE.new} />
      </td>
      <td className="px-4 py-3">
        <ConfidenceBadge score={finding.confidence_score} />
      </td>
      <td className="px-4 py-3 text-[11px] text-gray-400">
        {finding.escalation_level ? finding.escalation_level.replace(/_/g, " ") : "\u2014"}
      </td>
      <td className="px-4 py-3">
        <div className="flex items-center gap-1.5 whitespace-nowrap">
          {finding.devin_session_url && <a href={finding.devin_session_url} target="_blank" rel="noopener noreferrer" className="text-[11px] text-blue-600 hover:text-blue-800 font-medium">Devin</a>}
          {finding.pr_url && (
            <>{finding.devin_session_url && <span className="text-gray-300">&#183;</span>}<a href={finding.pr_url} target="_blank" rel="noopener noreferrer" className="text-[11px] text-blue-600 hover:text-blue-800 font-medium">PR #{finding.pr_number || ""}</a></>
          )}
          {finding.html_url && (
            <>{(finding.devin_session_url || finding.pr_url) && <span className="text-gray-300">&#183;</span>}<a href={finding.html_url} target="_blank" rel="noopener noreferrer" className="text-[11px] text-blue-600 hover:text-blue-800 font-medium">Alert</a></>
          )}
          {finding.status === "pr_created" && onReject && (
            <>
              <span className="text-gray-300">&#183;</span>
              {!showReject ? (
                <button onClick={() => setShowReject(true)} className="text-[11px] text-red-500 hover:text-red-700 font-medium">Reject</button>
              ) : (
                <span className="inline-flex items-center gap-1">
                  <input type="text" value={reason} onChange={(e) => setReason(e.target.value)} placeholder="Reason..." className="text-[11px] bg-white border border-gray-200 rounded px-1.5 py-0.5 text-gray-700 w-28 focus:ring-1 focus:ring-blue-500 focus:border-blue-500 outline-none" />
                  <button onClick={() => { if (reason.trim()) { onReject(finding.id, reason.trim()); setShowReject(false); setReason(""); } }} className="text-[11px] bg-red-500 hover:bg-red-600 text-white px-1.5 py-0.5 rounded">Send</button>
                  <button onClick={() => { setShowReject(false); setReason(""); }} className="text-[11px] text-gray-400 hover:text-gray-600">&times;</button>
                </span>
              )}
            </>
          )}
        </div>
        {finding.rejection_reason && (
          <p className="text-[10px] text-red-500 mt-1">Rejected: {finding.rejection_reason}</p>
        )}
      </td>
    </tr>
  );
}
