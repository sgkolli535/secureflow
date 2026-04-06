import { useEffect, useState, useCallback } from "react";
import {
  getFindings,
  getStats,
  getNotifications,
  getPipelineRuns,
  getCompliance,
  rejectFinding,
} from "./api";
import type {
  Finding,
  DashboardStats,
  NotificationItem,
  PipelineRun,
  ComplianceStats,
} from "./types";
import StatsBar from "./components/StatsBar";
import FilterBar from "./components/FilterBar";
import FindingsTable from "./components/FindingsTable";
import NotificationFeed from "./components/NotificationFeed";
import PipelineControls from "./components/PipelineControls";
import CompliancePanel from "./components/CompliancePanel";
import PipelineFlowView from "./components/PipelineFlowView";
import DevinInfoModal from "./components/DevinInfoModal";
import SeverityDonut from "./components/SeverityDonut";

type ViewMode = "table" | "kanban";
type Page = "overview" | "compliance";

export default function App() {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [findings, setFindings] = useState<Finding[]>([]);
  const [notifications, setNotifications] = useState<NotificationItem[]>([]);
  const [lastRun, setLastRun] = useState<PipelineRun | null>(null);
  const [compliance, setCompliance] = useState<ComplianceStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [severity, setSeverity] = useState("");
  const [status, setStatus] = useState("");
  const [viewMode, setViewMode] = useState<ViewMode>("table");
  const [page, setPage] = useState<Page>("overview");

  const refresh = useCallback(async (silent = false) => {
    if (!silent) setLoading(true);
    try {
      const [statsRes, findingsRes, notifRes, runsRes, compRes] =
        await Promise.all([
          getStats(),
          getFindings({
            severity: severity || undefined,
            status: status || undefined,
          }),
          getNotifications(),
          getPipelineRuns(),
          getCompliance(),
        ]);
      setStats(statsRes);
      setFindings(findingsRes.findings);
      setNotifications(notifRes.notifications);
      setLastRun(runsRes.runs[0] || null);
      setCompliance(compRes);
    } catch (err) {
      console.error("Failed to load data:", err);
    } finally {
      if (!silent) setLoading(false);
    }
  }, [severity, status]);

  useEffect(() => {
    refresh();
    const interval = setInterval(() => refresh(true), 30000);
    return () => clearInterval(interval);
  }, [refresh]);

  const handleReject = async (findingId: number, reason: string) => {
    try {
      await rejectFinding(findingId, reason);
      refresh();
    } catch (err) {
      console.error("Failed to reject finding:", err);
    }
  };

  const sidebarW = sidebarOpen ? "w-56" : "w-14";
  const mainMl = sidebarOpen ? "ml-56" : "ml-14";

  return (
    <div className="min-h-screen bg-white flex">
      {/* Sidebar */}
      <aside className={`${sidebarW} bg-white border-r border-gray-200 flex flex-col fixed h-full transition-all duration-200 z-20`}>
        <div className={`py-4 border-b border-gray-200 ${sidebarOpen ? "px-4" : "px-2"}`}>
          <div className="flex items-center gap-2.5">
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="w-8 h-8 bg-blue-700 rounded-lg flex items-center justify-center text-white font-bold text-xs flex-shrink-0 hover:bg-blue-800 transition-colors"
              title={sidebarOpen ? "Collapse" : "Expand"}
            >
              SF
            </button>
            {sidebarOpen && (
              <div>
                <h1 className="text-sm font-bold text-gray-900 leading-tight">SecureFlow</h1>
                <p className="text-[9px] text-gray-400 uppercase tracking-widest">Security Remediation</p>
              </div>
            )}
          </div>
        </div>

        <nav className={`flex-1 py-3 space-y-0.5 ${sidebarOpen ? "px-2" : "px-1"}`}>
          {sidebarOpen && <p className="px-2 pt-1 pb-2 text-[9px] font-bold text-gray-400 uppercase tracking-widest">Dashboard</p>}
          {!sidebarOpen && <div className="pt-1" />}
          <NavBtn active={page === "overview"} open={sidebarOpen} label="Overview" onClick={() => setPage("overview")}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 6A2.25 2.25 0 016 3.75h2.25A2.25 2.25 0 0110.5 6v2.25a2.25 2.25 0 01-2.25 2.25H6a2.25 2.25 0 01-2.25-2.25V6zm10.5 0A2.25 2.25 0 0116.5 3.75h.75a2.25 2.25 0 012.25 2.25v2.25a2.25 2.25 0 01-2.25 2.25h-.75a2.25 2.25 0 01-2.25-2.25V6zM3.75 15.75A2.25 2.25 0 016 13.5h2.25a2.25 2.25 0 012.25 2.25V18a2.25 2.25 0 01-2.25 2.25H6A2.25 2.25 0 013.75 18v-2.25zm10.5 0A2.25 2.25 0 0116.5 13.5h.75a2.25 2.25 0 012.25 2.25V18a2.25 2.25 0 01-2.25 2.25h-.75a2.25 2.25 0 01-2.25-2.25v-2.25z" />
          </NavBtn>
          <NavBtn active={page === "compliance"} open={sidebarOpen} label="Compliance" onClick={() => setPage("compliance")}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75m-3-7.036A11.959 11.959 0 013.598 6 11.99 11.99 0 003 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751A11.959 11.959 0 0012 2.714z" />
          </NavBtn>

          {sidebarOpen && <p className="px-2 pt-4 pb-2 text-[9px] font-bold text-gray-400 uppercase tracking-widest">Views</p>}
          {!sidebarOpen && <div className="pt-3" />}
          <NavBtn active={viewMode === "table" && page === "overview"} open={sidebarOpen} label="Table" onClick={() => { setViewMode("table"); setPage("overview"); }}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M3.375 19.5h17.25m-17.25 0a1.125 1.125 0 01-1.125-1.125M3.375 19.5h7.5c.621 0 1.125-.504 1.125-1.125m-9.75 0V5.625m0 12.75v-1.5c0-.621.504-1.125 1.125-1.125m18.375 2.625V5.625m0 12.75c0 .621-.504 1.125-1.125 1.125m1.125-1.125v-1.5c0-.621-.504-1.125-1.125-1.125m0 3.75h-7.5A1.125 1.125 0 0112 18.375m9.75-12.75c0-.621-.504-1.125-1.125-1.125H3.375c-.621 0-1.125.504-1.125 1.125m19.5 0v1.5c0 .621-.504 1.125-1.125 1.125M2.25 5.625v1.5c0 .621.504 1.125 1.125 1.125m0 0h17.25m-17.25 0h7.5c.621 0 1.125.504 1.125 1.125M3.375 8.25c-.621 0-1.125.504-1.125 1.125v1.5c0 .621.504 1.125 1.125 1.125m17.25-3.75h-7.5c-.621 0-1.125.504-1.125 1.125m8.625-1.125c.621 0 1.125.504 1.125 1.125v1.5c0 .621-.504 1.125-1.125 1.125m-17.25 0h7.5m-7.5 0c-.621 0-1.125.504-1.125 1.125v1.5c0 .621.504 1.125 1.125 1.125M12 10.875v-1.5m0 1.5c0 .621-.504 1.125-1.125 1.125M12 10.875c0 .621.504 1.125 1.125 1.125m-2.25 0c.621 0 1.125.504 1.125 1.125M13.125 12h7.5m-7.5 0c-.621 0-1.125.504-1.125 1.125M20.625 12c.621 0 1.125.504 1.125 1.125v1.5c0 .621-.504 1.125-1.125 1.125m-17.25 0h7.5M12 14.625v-1.5m0 1.5c0 .621-.504 1.125-1.125 1.125M12 14.625c0 .621.504 1.125 1.125 1.125m-2.25 0c.621 0 1.125.504 1.125 1.125m0 0v1.5c0 .621-.504 1.125-1.125 1.125" />
          </NavBtn>
          <NavBtn active={viewMode === "kanban" && page === "overview"} open={sidebarOpen} label="Pipeline" onClick={() => { setViewMode("kanban"); setPage("overview"); }}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M9 4.5v15m6-15v15m-10.875 0h15.75c.621 0 1.125-.504 1.125-1.125V5.625c0-.621-.504-1.125-1.125-1.125H4.125C3.504 4.5 3 5.004 3 5.625v12.75c0 .621.504 1.125 1.125 1.125z" />
          </NavBtn>
        </nav>

        <div className={`py-3 border-t border-gray-200 ${sidebarOpen ? "px-2" : "px-1"}`}>
          {sidebarOpen ? (
            <DevinInfoModal />
          ) : (
            <button onClick={() => setSidebarOpen(true)} title="How It Works" className="w-full flex justify-center py-2 text-gray-400 hover:text-gray-600 rounded-lg">
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}><path strokeLinecap="round" strokeLinejoin="round" d="M11.25 11.25l.041-.02a.75.75 0 011.063.852l-.708 2.836a.75.75 0 001.063.853l.041-.021M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-9-3.75h.008v.008H12V8.25z" /></svg>
            </button>
          )}
        </div>
      </aside>

      {/* Main */}
      <div className={`flex-1 ${mainMl} transition-all duration-200`}>
        <header className="bg-white border-b border-gray-200 sticky top-0 z-10">
          <div className="px-8 py-4 flex items-center justify-between">
            <div>
              <h2 className="text-lg font-bold text-gray-900 tracking-tight">
                {page === "overview" ? "Security Overview" : "Compliance & Audit"}
              </h2>
              <p className="text-xs text-gray-400">
                {stats ? `${stats.total} findings across your repositories` : "Loading..."}
              </p>
            </div>
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-1.5">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                <span className="text-[10px] text-gray-400 font-medium uppercase tracking-wider">Live</span>
              </div>
              <PipelineControls lastRun={lastRun} onRunComplete={refresh} />
            </div>
          </div>
        </header>

        <main className="px-8 py-6">
          {page === "overview" ? (
            <>
              <div className="mb-6"><StatsBar stats={stats} /></div>
              <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
                <div className="xl:col-span-2">
                  {viewMode === "table" ? (
                    <>
                      <FilterBar severity={severity} status={status} onSeverityChange={setSeverity} onStatusChange={setStatus} />
                      <FindingsTable findings={findings} loading={loading} onReject={handleReject} />
                    </>
                  ) : (
                    <PipelineFlowView findings={findings} onReject={handleReject} />
                  )}
                </div>
                <div className="space-y-6">
                  <SeverityDonut stats={stats} />
                  <NotificationFeed notifications={notifications} loading={loading} />
                </div>
              </div>
            </>
          ) : (
            <CompliancePanel compliance={compliance} />
          )}
        </main>
      </div>
    </div>
  );
}

function NavBtn({ active, open, label, onClick, children }: {
  active: boolean; open: boolean; label: string;
  onClick: () => void; children: React.ReactNode;
}) {
  return (
    <button
      onClick={onClick}
      title={label}
      className={`w-full flex items-center gap-2.5 ${open ? "px-2.5" : "justify-center px-0"} py-2 rounded-lg text-[13px] font-medium transition-colors ${
        active ? "bg-blue-50 text-blue-700" : "text-gray-500 hover:text-gray-700 hover:bg-gray-50"
      }`}
    >
      <svg className="w-4 h-4 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>{children}</svg>
      {open && label}
    </button>
  );
}
