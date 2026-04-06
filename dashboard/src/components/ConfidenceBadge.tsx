export default function ConfidenceBadge({ score }: { score: number | null }) {
  if (score === null || score === undefined) return null;
  const pct = Math.round(score * 100);
  const color =
    pct >= 80
      ? "bg-emerald-50 text-emerald-700 border-emerald-200"
      : pct >= 50
        ? "bg-amber-50 text-amber-700 border-amber-200"
        : "bg-red-50 text-red-700 border-red-200";
  return (
    <span className={`inline-block text-[10px] font-semibold px-2 py-0.5 rounded border leading-none ${color}`}>
      {pct}%
    </span>
  );
}
