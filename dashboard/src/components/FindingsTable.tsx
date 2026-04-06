import type { Finding } from "../types";
import FindingRow from "./FindingRow";

export default function FindingsTable({
  findings,
  loading,
  onReject,
}: {
  findings: Finding[];
  loading: boolean;
  onReject?: (findingId: number, reason: string) => void;
}) {
  if (loading) {
    return (
      <div className="border border-gray-200 rounded-xl p-8 text-center text-gray-400 text-sm">
        Loading findings...
      </div>
    );
  }

  if (findings.length === 0) {
    return (
      <div className="border border-gray-200 rounded-xl p-8 text-center text-gray-400 text-sm">
        No findings match the current filters.
      </div>
    );
  }

  return (
    <div className="border border-gray-200 rounded-xl overflow-x-auto">
      <table className="w-full text-left min-w-[800px]">
        <thead>
          <tr className="border-b border-gray-200 text-[10px] text-gray-400 uppercase tracking-wider font-semibold">
            <th className="px-4 py-3 w-24">Severity</th>
            <th className="px-4 py-3 w-20">CWE</th>
            <th className="px-4 py-3">Finding</th>
            <th className="px-4 py-3 w-28">Status</th>
            <th className="px-4 py-3 w-24">Confidence</th>
            <th className="px-4 py-3 w-24">Escalation</th>
            <th className="px-4 py-3 w-52">Links</th>
          </tr>
        </thead>
        <tbody>
          {findings.map((f) => (
            <FindingRow key={f.id} finding={f} onReject={onReject} />
          ))}
        </tbody>
      </table>
    </div>
  );
}
