import logging
from datetime import datetime, timezone

import httpx
from sqlalchemy.orm import Session

from secureflow.config import settings
from secureflow.models import Finding, Notification

logger = logging.getLogger("secureflow")


class NotificationService:
    def __init__(self, db: Session):
        self.db = db

    def send_pr_created(self, finding: Finding):
        msg = (
            f":white_check_mark: *SecureFlow Auto-Fix*\n"
            f"PR created for {finding.cwe} ({finding.rule_name}) in `{finding.file_path}`\n"
            f"Severity: {finding.severity.upper()} | PR: {finding.pr_url}\n"
            f"Please review and merge."
        )
        self._create("engineering", msg, "pr_created", finding.id)

    def send_escalation(self, finding: Finding, reason: str = ""):
        msg = (
            f":rotating_light: *SecureFlow Escalation*\n"
            f"{finding.cwe} ({finding.rule_name}) in `{finding.file_path}` requires manual attention.\n"
            f"Severity: {finding.severity.upper()}\n"
            f"Reason: {reason or 'Automated fix not possible — requires human judgment'}\n"
            f"Alert: {finding.html_url}"
        )
        self._create("security-team", msg, "escalation", finding.id)

    def send_daily_digest(self):
        counts: dict[str, int] = {}
        for status in ["new", "queued", "in_progress", "pr_created", "merged", "escalated"]:
            counts[status] = self.db.query(Finding).filter_by(status=status).count()

        total_open = counts.get("new", 0) + counts.get("queued", 0) + counts.get("in_progress", 0)
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        msg = (
            f":bar_chart: *SecureFlow Daily Digest* — {now}\n"
            f"New: {counts.get('new', 0)} | Queued: {counts.get('queued', 0)} | "
            f"In Progress: {counts.get('in_progress', 0)} | PRs Open: {counts.get('pr_created', 0)} | "
            f"Merged: {counts.get('merged', 0)} | Escalated: {counts.get('escalated', 0)}\n"
            f"Total open findings: {total_open}"
        )
        self._create("security-team", msg, "digest")

    def _create(self, channel: str, message: str, ntype: str, finding_id: int | None = None):
        notif = Notification(
            channel=channel,
            message=message,
            notification_type=ntype,
            finding_id=finding_id,
        )
        self.db.add(notif)
        self.db.commit()

        # Deliver to Slack
        self._send_to_slack(channel, message)

    def _send_to_slack(self, channel: str, message: str):
        if not settings.slack_enabled or not settings.slack_webhook_url:
            logger.info("[Slack Mock] #%s: %s", channel, message[:120])
            return
        try:
            payload = {"text": message, "channel": f"#{channel}"}
            with httpx.Client(timeout=10.0) as client:
                resp = client.post(settings.slack_webhook_url, json=payload)
                resp.raise_for_status()
            logger.info("Slack notification sent to #%s", channel)
        except Exception:
            logger.exception("Failed to send Slack notification to #%s", channel)
