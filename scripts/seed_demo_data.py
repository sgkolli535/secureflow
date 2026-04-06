#!/usr/bin/env python3
"""Seed the database with demo findings in various states for the demo video."""

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from secureflow.database import SessionLocal, init_db
from secureflow.models import Finding, Notification, PipelineRun

NOW = datetime.now(timezone.utc)

DEMO_FINDINGS = [
    # ── Merged (completed) ──────────────────────────────────────
    {
        "github_alert_number": 1,
        "rule_id": "py/sql-injection",
        "rule_name": "SQL Injection",
        "severity": "high",
        "cwe": "CWE-89",
        "description": "User-controlled data is used in a SQL query without proper sanitization.",
        "file_path": "app.py",
        "start_line": 42,
        "end_line": 44,
        "html_url": "https://github.com/demo/secureflow-demo-app/security/code-scanning/1",
        "status": "merged",
        "escalation_level": "auto_fix",
        "priority_score": 0.86,
        "confidence_score": 0.95,
        "devin_session_id": "ses_demo_001",
        "devin_session_url": "https://app.devin.ai/sessions/ses_demo_001",
        "pr_url": "https://github.com/demo/secureflow-demo-app/pull/1",
        "pr_number": 1,
        "first_seen": NOW - timedelta(days=2),
        "devin_started_at": NOW - timedelta(days=1, hours=20),
        "devin_completed_at": NOW - timedelta(days=1, hours=19),
    },
    {
        "github_alert_number": 2,
        "rule_id": "py/sql-injection",
        "rule_name": "SQL Injection",
        "severity": "high",
        "cwe": "CWE-89",
        "description": "String concatenation in SQL query allows injection attacks.",
        "file_path": "app.py",
        "start_line": 52,
        "end_line": 54,
        "html_url": "https://github.com/demo/secureflow-demo-app/security/code-scanning/2",
        "status": "merged",
        "escalation_level": "auto_fix",
        "priority_score": 0.86,
        "confidence_score": 0.95,
        "devin_session_id": "ses_demo_001",
        "devin_session_url": "https://app.devin.ai/sessions/ses_demo_001",
        "pr_url": "https://github.com/demo/secureflow-demo-app/pull/1",
        "pr_number": 1,
        "first_seen": NOW - timedelta(days=2),
        "devin_started_at": NOW - timedelta(days=1, hours=18),
        "devin_completed_at": NOW - timedelta(days=1, hours=17),
    },
    # ── PR Created (awaiting review) ────────────────────────────
    {
        "github_alert_number": 3,
        "rule_id": "py/reflective-xss",
        "rule_name": "Reflected Cross-Site Scripting",
        "severity": "high",
        "cwe": "CWE-79",
        "description": "User input is rendered in HTML response without proper escaping.",
        "file_path": "app.py",
        "start_line": 59,
        "end_line": 60,
        "html_url": "https://github.com/demo/secureflow-demo-app/security/code-scanning/3",
        "status": "pr_created",
        "escalation_level": "auto_fix",
        "priority_score": 0.86,
        "confidence_score": 0.85,
        "devin_session_id": "ses_demo_002",
        "devin_session_url": "https://app.devin.ai/sessions/ses_demo_002",
        "pr_url": "https://github.com/demo/secureflow-demo-app/pull/2",
        "pr_number": 2,
        "first_seen": NOW - timedelta(days=1),
        "devin_started_at": NOW - timedelta(hours=10),
        "devin_completed_at": NOW - timedelta(hours=9),
    },
    {
        "github_alert_number": 4,
        "rule_id": "py/reflective-xss",
        "rule_name": "Reflected Cross-Site Scripting",
        "severity": "medium",
        "cwe": "CWE-79",
        "description": "User input embedded directly in HTML output via f-string.",
        "file_path": "app.py",
        "start_line": 64,
        "end_line": 65,
        "html_url": "https://github.com/demo/secureflow-demo-app/security/code-scanning/4",
        "status": "pr_created",
        "escalation_level": "auto_fix",
        "priority_score": 0.575,
        "confidence_score": 0.78,
        "devin_session_id": "ses_demo_002",
        "devin_session_url": "https://app.devin.ai/sessions/ses_demo_002",
        "pr_url": "https://github.com/demo/secureflow-demo-app/pull/2",
        "pr_number": 2,
        "first_seen": NOW - timedelta(days=1),
        "devin_started_at": NOW - timedelta(hours=6),
        "devin_completed_at": NOW - timedelta(hours=5),
    },
    # ── In Progress (Devin working) ─────────────────────────────
    {
        "github_alert_number": 5,
        "rule_id": "py/command-line-injection",
        "rule_name": "Command Injection",
        "severity": "critical",
        "cwe": "CWE-78",
        "description": "User-controlled data passed to os.popen() allows arbitrary command execution.",
        "file_path": "app.py",
        "start_line": 76,
        "end_line": 77,
        "html_url": "https://github.com/demo/secureflow-demo-app/security/code-scanning/5",
        "status": "in_progress",
        "escalation_level": "assist",
        "priority_score": 1.0,
        "devin_session_id": "ses_demo_003",
        "devin_session_url": "https://app.devin.ai/sessions/ses_demo_003",
        "devin_started_at": NOW - timedelta(minutes=15),
    },
    {
        "github_alert_number": 6,
        "rule_id": "py/command-line-injection",
        "rule_name": "Command Injection",
        "severity": "high",
        "cwe": "CWE-78",
        "description": "String concatenation in shell command allows injection.",
        "file_path": "app.py",
        "start_line": 82,
        "end_line": 83,
        "html_url": "https://github.com/demo/secureflow-demo-app/security/code-scanning/6",
        "status": "in_progress",
        "escalation_level": "auto_fix",
        "priority_score": 0.86,
        "devin_session_id": "ses_demo_003",
        "devin_session_url": "https://app.devin.ai/sessions/ses_demo_003",
        "devin_started_at": NOW - timedelta(minutes=15),
    },
    # ── Queued (triaged, waiting) ───────────────────────────────
    {
        "github_alert_number": 7,
        "rule_id": "py/path-injection",
        "rule_name": "Path Traversal",
        "severity": "high",
        "cwe": "CWE-22",
        "description": "Unsanitized user input in file path allows directory traversal.",
        "file_path": "app.py",
        "start_line": 69,
        "end_line": 70,
        "html_url": "https://github.com/demo/secureflow-demo-app/security/code-scanning/7",
        "status": "queued",
        "escalation_level": "auto_fix",
        "priority_score": 0.86,
    },
    {
        "github_alert_number": 8,
        "rule_id": "py/path-injection",
        "rule_name": "Path Traversal",
        "severity": "medium",
        "cwe": "CWE-22",
        "description": "User-supplied filename passed to send_file without validation.",
        "file_path": "app.py",
        "start_line": 74,
        "end_line": 75,
        "html_url": "https://github.com/demo/secureflow-demo-app/security/code-scanning/8",
        "status": "queued",
        "escalation_level": "auto_fix",
        "priority_score": 0.575,
    },
    # ── Escalated (needs human) ─────────────────────────────────
    {
        "github_alert_number": 9,
        "rule_id": "py/hardcoded-credentials",
        "rule_name": "Hardcoded Credentials",
        "severity": "critical",
        "cwe": "CWE-798",
        "description": "Credentials are hardcoded in source code.",
        "file_path": "app.py",
        "start_line": 14,
        "end_line": 16,
        "html_url": "https://github.com/demo/secureflow-demo-app/security/code-scanning/9",
        "status": "escalated",
        "escalation_level": "assist",
        "priority_score": 1.0,
    },
    # ── Rejected (feedback loop demo) ────────────────────────────
    {
        "github_alert_number": 12,
        "rule_id": "py/hardcoded-credentials",
        "rule_name": "Hardcoded Credentials",
        "severity": "high",
        "cwe": "CWE-798",
        "description": "API key hardcoded in source code.",
        "file_path": "app.py",
        "start_line": 15,
        "end_line": 15,
        "html_url": "https://github.com/demo/secureflow-demo-app/security/code-scanning/12",
        "status": "in_progress",
        "escalation_level": "auto_fix",
        "priority_score": 0.86,
        "confidence_score": None,
        "rejection_reason": "Fix moved secret to .env but didn't add .env to .gitignore",
        "retry_count": 1,
        "devin_session_id": "ses_demo_005",
        "devin_session_url": "https://app.devin.ai/sessions/ses_demo_005",
        "devin_started_at": NOW - timedelta(minutes=5),
    },
    # ── New (just discovered) ───────────────────────────────────
    {
        "github_alert_number": 10,
        "rule_id": "py/missing-input-validation",
        "rule_name": "Missing Input Validation",
        "severity": "medium",
        "cwe": "CWE-20",
        "description": "No validation on financial transfer amount or account fields.",
        "file_path": "app.py",
        "start_line": 88,
        "end_line": 96,
        "html_url": "https://github.com/demo/secureflow-demo-app/security/code-scanning/10",
        "status": "new",
        "escalation_level": None,
        "priority_score": None,
    },
    {
        "github_alert_number": 11,
        "rule_id": "py/sql-injection",
        "rule_name": "SQL Injection in set_role",
        "severity": "high",
        "cwe": "CWE-89",
        "description": "f-string used to construct SQL UPDATE query with user input.",
        "file_path": "app.py",
        "start_line": 101,
        "end_line": 103,
        "html_url": "https://github.com/demo/secureflow-demo-app/security/code-scanning/11",
        "status": "new",
        "escalation_level": None,
        "priority_score": None,
    },
]

DEMO_NOTIFICATIONS = [
    {
        "channel": "security-team",
        "message": (
            ":bar_chart: *SecureFlow Daily Digest* — 2026-03-30\n"
            "New: 2 | Queued: 2 | In Progress: 2 | PRs Open: 2 | Merged: 2 | Escalated: 1\n"
            "Total open findings: 6"
        ),
        "notification_type": "digest",
        "created_at": NOW - timedelta(hours=1),
    },
    {
        "channel": "engineering",
        "message": (
            ":white_check_mark: *SecureFlow Auto-Fix*\n"
            "PR created for CWE-89 (SQL Injection) in `app.py`\n"
            "Severity: HIGH | PR: https://github.com/demo/secureflow-demo-app/pull/1\n"
            "Please review and merge."
        ),
        "notification_type": "pr_created",
        "finding_id": 1,
        "created_at": NOW - timedelta(hours=3, minutes=20),
    },
    {
        "channel": "engineering",
        "message": (
            ":white_check_mark: *SecureFlow Auto-Fix*\n"
            "PR created for CWE-79 (Reflected Cross-Site Scripting) in `app.py`\n"
            "Severity: HIGH | PR: https://github.com/demo/secureflow-demo-app/pull/2\n"
            "Please review and merge."
        ),
        "notification_type": "pr_created",
        "finding_id": 3,
        "created_at": NOW - timedelta(hours=1, minutes=30),
    },
    {
        "channel": "security-team",
        "message": (
            ":rotating_light: *SecureFlow Escalation*\n"
            "CWE-798 (Hardcoded Credentials) in `app.py` requires manual attention.\n"
            "Severity: CRITICAL\n"
            "Reason: Automated fix not possible — requires human judgment\n"
            "Alert: https://github.com/demo/secureflow-demo-app/security/code-scanning/9"
        ),
        "notification_type": "escalation",
        "finding_id": 9,
        "created_at": NOW - timedelta(hours=2),
    },
    {
        "channel": "security-team",
        "message": (
            ":rotating_light: *SecureFlow Escalation*\n"
            "CWE-798 (Hardcoded Credentials) in `app.py` requires manual attention.\n"
            "Severity: HIGH\n"
            "Reason: Re-dispatched to Devin (attempt 1): Fix moved secret to .env but didn't add .env to .gitignore\n"
            "Alert: https://github.com/demo/secureflow-demo-app/security/code-scanning/12"
        ),
        "notification_type": "escalation",
        "finding_id": 12,
        "created_at": NOW - timedelta(minutes=10),
    },
]

DEMO_PIPELINE_RUNS = [
    {
        "started_at": NOW - timedelta(days=3),
        "completed_at": NOW - timedelta(days=3) + timedelta(minutes=8),
        "alerts_fetched": 6,
        "sessions_created": 2,
        "prs_created": 1,
        "escalated": 0,
        "status": "completed",
    },
    {
        "started_at": NOW - timedelta(days=2),
        "completed_at": NOW - timedelta(days=2) + timedelta(minutes=12),
        "alerts_fetched": 8,
        "sessions_created": 3,
        "prs_created": 2,
        "escalated": 1,
        "status": "completed",
    },
    {
        "started_at": NOW - timedelta(days=1),
        "completed_at": NOW - timedelta(days=1) + timedelta(minutes=10),
        "alerts_fetched": 5,
        "sessions_created": 2,
        "prs_created": 2,
        "escalated": 0,
        "status": "completed",
    },
    {
        "started_at": NOW - timedelta(hours=4, minutes=10),
        "completed_at": NOW - timedelta(hours=4),
        "alerts_fetched": 12,
        "sessions_created": 4,
        "prs_created": 2,
        "escalated": 1,
        "status": "completed",
    },
]


def main():
    init_db()
    db = SessionLocal()

    # Clear existing data
    db.query(Finding).delete()
    db.query(Notification).delete()
    db.query(PipelineRun).delete()
    db.commit()

    # Seed findings
    for data in DEMO_FINDINGS:
        db.add(Finding(**data))
    db.commit()

    # Seed notifications
    for data in DEMO_NOTIFICATIONS:
        db.add(Notification(**data))
    db.commit()

    # Seed pipeline runs
    for run_data in DEMO_PIPELINE_RUNS:
        db.add(PipelineRun(**run_data))
    db.commit()

    print(f"Seeded {len(DEMO_FINDINGS)} findings, {len(DEMO_NOTIFICATIONS)} notifications, {len(DEMO_PIPELINE_RUNS)} pipeline runs")
    db.close()


if __name__ == "__main__":
    main()
