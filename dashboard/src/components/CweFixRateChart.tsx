import { BarChart, Bar, XAxis, YAxis, ResponsiveContainer, Tooltip, Cell } from "recharts";
import type { ComplianceStats } from "../types";

export default function CweFixRateChart({ compliance }: { compliance: ComplianceStats | null }) {
  if (!compliance || compliance.cwe_fix_rates.length === 0) return null;

  const data = compliance.cwe_fix_rates
    .sort((a, b) => b.rate - a.rate)
    .map((d) => ({
      ...d,
      label: d.cwe,
    }));

  return (
    <div className="border border-gray-200 rounded-xl p-6">
      <h3 className="text-xs font-bold text-gray-900 uppercase tracking-wider mb-1">
        Fix Success Rate by CWE
      </h3>
      <p className="text-[11px] text-gray-400 mb-5">Percentage of findings Devin successfully resolved per vulnerability type</p>
      <div style={{ height: data.length * 36 + 20 }}>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} layout="vertical" margin={{ top: 0, right: 12, bottom: 0, left: 0 }}>
            <XAxis type="number" domain={[0, 100]} tickFormatter={(v) => `${v}%`} tick={{ fontSize: 10, fill: "#9ca3af" }} axisLine={false} tickLine={false} />
            <YAxis type="category" dataKey="label" width={72} tick={{ fontSize: 11, fill: "#374151", fontFamily: "monospace", fontWeight: 600 }} axisLine={false} tickLine={false} />
            <Tooltip
              contentStyle={{ background: "#fff", border: "1px solid #e5e7eb", borderRadius: "8px", fontSize: "11px", padding: "6px 10px" }}
              // eslint-disable-next-line @typescript-eslint/no-explicit-any
              formatter={(value: any, _name: any, props: any) => [`${value}% (${props.payload.fixed}/${props.payload.total})`, "Fix Rate"]}
            />
            <Bar dataKey="rate" radius={[0, 4, 4, 0]} barSize={20}>
              {data.map((entry) => (
                <Cell
                  key={entry.cwe}
                  fill={entry.rate >= 80 ? "#059669" : entry.rate >= 50 ? "#d97706" : "#dc2626"}
                  opacity={0.85}
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
