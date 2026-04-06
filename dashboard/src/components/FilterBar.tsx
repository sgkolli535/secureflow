interface FilterBarProps {
  severity: string;
  status: string;
  onSeverityChange: (v: string) => void;
  onStatusChange: (v: string) => void;
}

const SEVERITIES = ["", "critical", "high", "medium", "low"];
const STATUSES = ["", "new", "queued", "in_progress", "pr_created", "merged", "escalated", "dismissed", "rejected"];

function Select({ value, onChange, options, label }: {
  value: string; onChange: (v: string) => void; options: string[]; label: string;
}) {
  return (
    <select
      value={value}
      onChange={(e) => onChange(e.target.value)}
      className="bg-white text-gray-700 border border-gray-200 rounded-lg px-3 py-1.5 text-xs font-medium focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
    >
      <option value="">All {label}</option>
      {options.filter((o) => o !== "").map((o) => (
        <option key={o} value={o}>{o.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase())}</option>
      ))}
    </select>
  );
}

export default function FilterBar({ severity, status, onSeverityChange, onStatusChange }: FilterBarProps) {
  return (
    <div className="flex gap-2 mb-4">
      <Select value={severity} onChange={onSeverityChange} options={SEVERITIES} label="Severities" />
      <Select value={status} onChange={onStatusChange} options={STATUSES} label="Statuses" />
    </div>
  );
}
