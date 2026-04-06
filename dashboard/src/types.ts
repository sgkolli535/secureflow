export interface Finding {
  id: number;
  github_alert_number: number;
  rule_id: string | null;
  rule_name: string | null;
  severity: string | null;
  cwe: string | null;
  description: string | null;
  file_path: string | null;
  start_line: number | null;
  end_line: number | null;
  html_url: string | null;
  status: string | null;
  escalation_level: string | null;
  priority_score: number | null;
  devin_session_id: string | null;
  devin_session_url: string | null;
  pr_url: string | null;
  pr_number: number | null;
  confidence_score: number | null;
  rejection_reason: string | null;
  retry_count: number | null;
  first_seen: string | null;
  last_updated: string | null;
  devin_started_at: string | null;
  devin_completed_at: string | null;
  batch_id: string | null;
}

export interface DashboardStats {
  total: number;
  by_severity: Record<string, number>;
  by_status: Record<string, number>;
  by_escalation: Record<string, number>;
  auto_fix_rate: number;
  mean_time_to_fix_hours: number | null;
}

export interface NotificationItem {
  id: number;
  channel: string;
  message: string;
  notification_type: string;
  created_at: string | null;
  finding_id: number | null;
}

export interface PipelineRun {
  id: number;
  started_at: string | null;
  completed_at: string | null;
  alerts_fetched: number;
  sessions_created: number;
  prs_created: number;
  escalated: number;
  status: string;
}

export interface ComplianceStats {
  mean_time_to_remediate_hours: number | null;
  auto_fix_percentage: number;
  manual_percentage: number;
  finding_age_distribution: Record<string, number>;
  trend: Array<{
    run_id: number;
    date: string | null;
    alerts_fetched: number;
    prs_created: number;
    escalated: number;
  }>;
  audit_trail: Array<{
    id: number;
    type: string;
    channel: string;
    message: string;
    created_at: string | null;
    finding_id: number | null;
  }>;
  total_findings: number;
  total_fixed: number;
  total_escalated: number;
  cwe_fix_rates: Array<{
    cwe: string;
    total: number;
    fixed: number;
    rate: number;
  }>;
  remediation_timeline: Array<{
    date: string | null;
    cumulative_fixed: number;
    cwe: string | null;
  }>;
}
