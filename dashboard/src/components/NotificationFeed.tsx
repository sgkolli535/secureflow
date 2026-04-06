import type { NotificationItem } from "../types";

const CHANNEL_COLORS: Record<string, string> = {
  "security-team": "text-red-600 bg-red-50 border-red-200",
  engineering: "text-blue-600 bg-blue-50 border-blue-200",
  escalations: "text-amber-600 bg-amber-50 border-amber-200",
};

const TYPE_ICONS: Record<string, string> = {
  digest: "\u{1F4CA}",
  pr_created: "\u{2705}",
  escalation: "\u{1F6A8}",
};

function formatTime(iso: string | null): string {
  if (!iso) return "";
  const d = new Date(iso);
  const now = new Date();
  const diffMs = now.getTime() - d.getTime();
  const diffMin = Math.floor(diffMs / 60000);
  if (diffMin < 60) return `${diffMin}m ago`;
  const diffH = Math.floor(diffMin / 60);
  if (diffH < 24) return `${diffH}h ago`;
  return d.toLocaleDateString();
}

export default function NotificationFeed({
  notifications,
  loading,
}: {
  notifications: NotificationItem[];
  loading: boolean;
}) {
  return (
    <div className="border border-gray-200 rounded-xl overflow-hidden">
      <div className="px-4 py-3 border-b border-gray-200">
        <h3 className="text-xs font-bold text-gray-900 uppercase tracking-wider">Notification Feed</h3>
      </div>
      <div className="max-h-96 overflow-y-auto divide-y divide-gray-100">
        {loading && <div className="p-4 text-gray-400 text-xs">Loading...</div>}
        {!loading && notifications.length === 0 && <div className="p-4 text-gray-400 text-xs">No notifications yet.</div>}
        {notifications.map((n) => (
          <div key={n.id} className="px-4 py-3 hover:bg-gray-50/50 transition-colors">
            <div className="flex items-center gap-2 mb-1.5">
              <span className="text-sm">{TYPE_ICONS[n.notification_type] || "\u{1F514}"}</span>
              <span className={`text-[9px] px-1.5 py-0.5 rounded border font-semibold uppercase tracking-wider ${CHANNEL_COLORS[n.channel] || "text-gray-500 bg-gray-50 border-gray-200"}`}>
                #{n.channel}
              </span>
              <span className="text-[10px] text-gray-400 ml-auto">{formatTime(n.created_at)}</span>
            </div>
            <div className="text-xs text-gray-600 leading-relaxed mt-1">
              {(() => {
                const cleaned = n.message.replace(/:\w+:/g, "").replace(/\*([^*]+)\*/g, "$1").trim();
                const lines = cleaned.split("\n").filter(Boolean);
                const title = lines[0] || "";
                const body = lines.slice(1);
                return (
                  <>
                    <p className="font-semibold text-gray-800 text-[12px] mb-1">{title}</p>
                    {body.length > 0 && (
                      <ul className="space-y-0.5">
                        {body.map((line, i) => {
                          const parts = line.split(/:\s*/);
                          const hasLabel = parts.length >= 2 && parts[0].length < 30;
                          return (
                            <li key={i} className="flex gap-1.5 text-[11px] text-gray-500 leading-snug">
                              <span className="text-gray-300 mt-px">&#8226;</span>
                              {hasLabel ? (
                                <span><span className="font-semibold text-gray-600">{parts[0]}:</span> {parts.slice(1).join(": ")}</span>
                              ) : (
                                <span>{line}</span>
                              )}
                            </li>
                          );
                        })}
                      </ul>
                    )}
                  </>
                );
              })()}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
