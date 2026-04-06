import { AreaChart, Area, XAxis, YAxis, ResponsiveContainer, Tooltip, CartesianGrid } from "recharts";
import type { ComplianceStats } from "../types";

export default function RemediationTimeline({ compliance }: { compliance: ComplianceStats | null }) {
  if (!compliance || compliance.remediation_timeline.length === 0) return null;

  const data = compliance.remediation_timeline.map((d) => ({
    ...d,
    time: d.date ? new Date(d.date).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }) : "",
    dateLabel: d.date ? new Date(d.date).toLocaleDateString([], { month: "short", day: "numeric" }) : "",
  }));

  return (
    <div className="border border-gray-200 rounded-xl p-6">
      <h3 className="text-xs font-bold text-gray-900 uppercase tracking-wider mb-1">
        Remediation Timeline
      </h3>
      <p className="text-[11px] text-gray-400 mb-5">Cumulative findings resolved over time</p>
      <div className="h-48">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data} margin={{ top: 4, right: 12, bottom: 0, left: -20 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f3f4f6" vertical={false} />
            <XAxis
              dataKey="dateLabel"
              tick={{ fontSize: 10, fill: "#9ca3af" }}
              axisLine={false}
              tickLine={false}
            />
            <YAxis
              tick={{ fontSize: 10, fill: "#9ca3af" }}
              axisLine={false}
              tickLine={false}
              allowDecimals={false}
            />
            <Tooltip
              contentStyle={{
                background: "#fff",
                border: "1px solid #e5e7eb",
                borderRadius: "8px",
                fontSize: "11px",
                padding: "6px 10px",
              }}
              formatter={(value) => [`${value} findings`, "Resolved"]}
              labelFormatter={(_, payload) => {
                if (payload && payload[0]?.payload?.date) {
                  return new Date(payload[0].payload.date).toLocaleString();
                }
                return "";
              }}
            />
            <defs>
              <linearGradient id="blueGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#2563eb" stopOpacity={0.2} />
                <stop offset="100%" stopColor="#2563eb" stopOpacity={0.02} />
              </linearGradient>
            </defs>
            <Area
              type="stepAfter"
              dataKey="cumulative_fixed"
              stroke="#2563eb"
              strokeWidth={2}
              fill="url(#blueGrad)"
              dot={{ r: 3, fill: "#2563eb", strokeWidth: 0 }}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
