import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from "recharts";
import type { DashboardStats } from "../types";

const COLORS: Record<string, string> = {
  critical: "#dc2626",
  high: "#ea580c",
  medium: "#d97706",
  low: "#2563eb",
};

export default function SeverityDonut({ stats }: { stats: DashboardStats | null }) {
  if (!stats) return null;

  const data = Object.entries(stats.by_severity)
    .filter(([, v]) => v > 0)
    .map(([name, value]) => ({ name, value }));

  if (data.length === 0) return null;

  return (
    <div className="border border-gray-200 rounded-xl p-5">
      <h3 className="text-[10px] font-bold text-gray-900 uppercase tracking-wider mb-4">
        Severity Distribution
      </h3>
      <div className="flex items-center gap-6">
        <div className="w-32 h-32 flex-shrink-0">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={data}
                cx="50%"
                cy="50%"
                innerRadius={30}
                outerRadius={55}
                paddingAngle={2}
                dataKey="value"
                strokeWidth={0}
              >
                {data.map((entry) => (
                  <Cell key={entry.name} fill={COLORS[entry.name] || "#94a3b8"} />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{
                  background: "#fff",
                  border: "1px solid #e5e7eb",
                  borderRadius: "8px",
                  fontSize: "11px",
                  padding: "6px 10px",
                }}
                formatter={(value, name) => [String(value), String(name).charAt(0).toUpperCase() + String(name).slice(1)]}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>
        <div className="space-y-2">
          {data.map((d) => (
            <div key={d.name} className="flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full flex-shrink-0" style={{ background: COLORS[d.name] }} />
              <span className="text-[11px] text-gray-500 capitalize w-14">{d.name}</span>
              <span className="text-[12px] font-bold text-gray-900">{d.value}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
