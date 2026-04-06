import type { DashboardStats } from "../types";

export default function StatsBar({ stats }: { stats: DashboardStats | null }) {
  if (!stats) {
    return (
      <div className="border border-gray-200 rounded-xl mb-6 h-20 animate-pulse" />
    );
  }

  const fixRate = Math.round(stats.auto_fix_rate * 100);

  const cells = [
    { label: "Critical", value: stats.by_severity.critical ?? 0, color: "text-red-600" },
    { label: "High", value: stats.by_severity.high ?? 0, color: "text-orange-600" },
    { label: "Medium", value: stats.by_severity.medium ?? 0, color: "text-amber-600" },
    { label: "Low", value: stats.by_severity.low ?? 0, color: "text-blue-600" },
    { label: "Auto-Fix Rate", value: `${fixRate}%`, color: "text-emerald-600" },
    { label: "Avg Fix Time", value: stats.mean_time_to_fix_hours ? `${stats.mean_time_to_fix_hours}h` : "\u2014", color: "text-blue-700" },
  ];

  return (
    <div className="border border-gray-200 rounded-xl overflow-hidden flex divide-x divide-gray-200">
      {cells.map((cell) => (
        <div key={cell.label} className="flex-1 px-5 py-4 text-center">
          <p className="text-[10px] text-gray-400 font-semibold uppercase tracking-wider mb-1">{cell.label}</p>
          <p className={`text-xl font-bold ${cell.color}`}>{cell.value}</p>
        </div>
      ))}
    </div>
  );
}
