import type { ComplianceStats, DashboardStats, Finding, NotificationItem, PipelineRun } from "./types";

const BASE = "/api";

async function fetchJSON<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE}${path}`);
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

export async function getFindings(params?: {
  severity?: string;
  status?: string;
}): Promise<{ total: number; findings: Finding[] }> {
  const qs = new URLSearchParams();
  if (params?.severity) qs.set("severity", params.severity);
  if (params?.status) qs.set("status", params.status);
  const query = qs.toString();
  return fetchJSON(`/findings${query ? `?${query}` : ""}`);
}

export async function getStats(): Promise<DashboardStats> {
  return fetchJSON("/dashboard/stats");
}

export async function getNotifications(
  channel?: string
): Promise<{ notifications: NotificationItem[] }> {
  const qs = channel ? `?channel=${channel}` : "";
  return fetchJSON(`/notifications${qs}`);
}

export async function triggerPipeline(): Promise<PipelineRun> {
  const res = await fetch(`${BASE}/pipeline/run`, { method: "POST" });
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

export async function getPipelineRuns(): Promise<{ runs: PipelineRun[] }> {
  return fetchJSON("/pipeline/runs");
}

export async function getCompliance(): Promise<ComplianceStats> {
  return fetchJSON("/dashboard/compliance");
}

export async function rejectFinding(
  findingId: number,
  rejectionReason: string
): Promise<Finding> {
  const res = await fetch(`${BASE}/findings/${findingId}/reject`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ rejection_reason: rejectionReason }),
  });
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}
