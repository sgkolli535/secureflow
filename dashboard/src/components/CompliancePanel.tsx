import { useState } from "react";
import type { ComplianceStats } from "../types";
import CweFixRateChart from "./CweFixRateChart";
import RemediationTimeline from "./RemediationTimeline";

export default function CompliancePanel({ compliance }: { compliance: ComplianceStats | null }) {
  const [showAudit, setShowAudit] = useState(false);

  if (!compliance) {
    return <div className="border border-gray-200 rounded-xl p-8 text-center text-gray-400 text-sm">Loading compliance data...</div>;
  }

  const ageDist = compliance.finding_age_distribution;
  const ageTotal = Object.values(ageDist).reduce((a, b) => a + b, 0);
  const ageColors: Record<string, string> = {
    "< 1 day": "bg-emerald-500",
    "1-7 days": "bg-amber-400",
    "7-30 days": "bg-orange-500",
    "> 30 days": "bg-red-500",
  };

  const typeColors: Record<string, string> = {
    escalation: "bg-red-50 text-red-700 border-red-200",
    pr_created: "bg-emerald-50 text-emerald-700 border-emerald-200",
    digest: "bg-blue-50 text-blue-700 border-blue-200",
  };

  return (
    <div className="space-y-6">
      {/* KPI row */}
      <div className="border border-gray-200 rounded-xl overflow-hidden flex divide-x divide-gray-200">
        <div className="flex-1 px-6 py-5 text-center">
          <p className="text-[10px] text-gray-400 font-semibold uppercase tracking-wider mb-1">Avg Time to Remediate</p>
          <p className="text-2xl font-bold text-gray-900">{compliance.mean_time_to_remediate_hours != null ? `${compliance.mean_time_to_remediate_hours}h` : "\u2014"}</p>
        </div>
        <div className="flex-1 px-6 py-5 text-center">
          <p className="text-[10px] text-gray-400 font-semibold uppercase tracking-wider mb-1">Auto-Fix Rate</p>
          <p className="text-2xl font-bold text-blue-700">{compliance.auto_fix_percentage}%</p>
        </div>
        <div className="flex-1 px-6 py-5 text-center">
          <p className="text-[10px] text-gray-400 font-semibold uppercase tracking-wider mb-1">Total Remediated</p>
          <p className="text-2xl font-bold text-gray-900">{compliance.total_fixed}<span className="text-sm font-normal text-gray-400"> / {compliance.total_findings}</span></p>
        </div>
        <div className="flex-1 px-6 py-5 text-center">
          <p className="text-[10px] text-gray-400 font-semibold uppercase tracking-wider mb-1">Manually Escalated</p>
          <p className="text-2xl font-bold text-gray-900">{compliance.total_escalated}<span className="text-sm font-normal text-gray-400"> ({compliance.manual_percentage}%)</span></p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Age Distribution */}
        <div className="border border-gray-200 rounded-xl p-6 flex flex-col">
          <h3 className="text-xs font-bold text-gray-900 uppercase tracking-wider mb-6">Open Finding Age Distribution</h3>
          <div className="flex-1 flex flex-col justify-center">
            {ageTotal > 0 ? (
              <div className="flex rounded h-4 overflow-hidden bg-gray-100">
                {Object.entries(ageDist).map(([label, count]) =>
                  count > 0 ? <div key={label} className={`${ageColors[label] || "bg-gray-400"}`} style={{ width: `${(count / ageTotal) * 100}%` }} title={`${label}: ${count}`} /> : null
                )}
              </div>
            ) : (
              <div className="flex rounded h-4 overflow-hidden bg-gray-100" />
            )}
            <div className="flex gap-4 mt-4 flex-wrap">
              {Object.entries(ageDist).map(([label, count]) => (
                <span key={label} className="flex items-center gap-1.5 text-[11px] text-gray-500">
                  <span className={`w-2 h-2 rounded-full ${ageColors[label] || "bg-gray-400"}`} />
                  {label}: <span className="font-semibold text-gray-700">{count}</span>
                </span>
              ))}
            </div>
          </div>
        </div>

        {/* Trend */}
        {compliance.trend.length > 0 && (
          <div className="border border-gray-200 rounded-xl p-6">
            <h3 className="text-xs font-bold text-gray-900 uppercase tracking-wider mb-6">Pipeline Run Trend</h3>
            <div className="flex items-end gap-2 h-20">
              {compliance.trend.map((run) => {
                const max = Math.max(...compliance.trend.map(r => r.alerts_fetched || 1));
                const height = ((run.alerts_fetched || 1) / max) * 80;
                return (
                  <div key={run.run_id} className="flex-1 flex flex-col items-center" title={`Run #${run.run_id}: ${run.alerts_fetched} fetched, ${run.prs_created} PRs, ${run.escalated} escalated`}>
                    <div className="w-full bg-blue-100 rounded-t" style={{ height: `${height}px` }}>
                      <div className="bg-blue-600 rounded-t w-full" style={{ height: `${(run.prs_created / (run.alerts_fetched || 1)) * 100}%` }} />
                    </div>
                    <span className="text-[9px] text-gray-400 mt-1">#{run.run_id}</span>
                  </div>
                );
              })}
            </div>
            <div className="flex gap-4 mt-3">
              <span className="flex items-center gap-1.5 text-[11px] text-gray-500"><span className="w-2 h-2 rounded-full bg-blue-600" />PRs Created</span>
              <span className="flex items-center gap-1.5 text-[11px] text-gray-500"><span className="w-2 h-2 rounded-full bg-blue-100" />Fetched</span>
            </div>
          </div>
        )}
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <CweFixRateChart compliance={compliance} />
        <RemediationTimeline compliance={compliance} />
      </div>

      {/* Audit Trail */}
      <div className="border border-gray-200 rounded-xl overflow-hidden">
        <button onClick={() => setShowAudit(!showAudit)} className="w-full px-6 py-4 flex items-center justify-between hover:bg-gray-50/50 transition-colors">
          <h3 className="text-xs font-bold text-gray-900 uppercase tracking-wider">Audit Trail</h3>
          <span className="text-[11px] text-blue-600 font-medium">{showAudit ? "Hide" : "Show"} ({compliance.audit_trail.length})</span>
        </button>
        {showAudit && (
          <div className="border-t border-gray-200 max-h-64 overflow-y-auto">
            <table className="w-full text-left">
              <thead>
                <tr className="border-b border-gray-200 text-[9px] text-gray-400 uppercase tracking-wider">
                  <th className="px-6 py-2 font-semibold">Time</th>
                  <th className="px-6 py-2 font-semibold">Channel</th>
                  <th className="px-6 py-2 font-semibold">Type</th>
                  <th className="px-6 py-2 font-semibold">Message</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {compliance.audit_trail.map((entry) => (
                  <tr key={entry.id} className="hover:bg-gray-50/50">
                    <td className="px-6 py-2 text-[11px] text-gray-500 whitespace-nowrap">{entry.created_at ? new Date(entry.created_at).toLocaleString() : "\u2014"}</td>
                    <td className="px-6 py-2 text-[11px] text-gray-500">#{entry.channel}</td>
                    <td className="px-6 py-2">
                      <span className={`text-[9px] px-1.5 py-0.5 rounded border font-semibold whitespace-nowrap ${typeColors[entry.type] || "bg-gray-50 text-gray-600 border-gray-200"}`}>
                        {entry.type.replace(/_/g, " ")}
                      </span>
                    </td>
                    <td className="px-6 py-2 text-[11px] text-gray-500 truncate max-w-md">{entry.message.replace(/:\w+:/g, "").replace(/\*([^*]+)\*/g, "$1").trim().slice(0, 120)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
