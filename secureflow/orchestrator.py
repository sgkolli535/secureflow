import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from secureflow.config import Settings
from secureflow.devin_client import DevinClient
from secureflow.github_client import GitHubCodeQLClient
from secureflow.models import Finding, FindingStatus, PipelineRun
from secureflow.notifications import NotificationService
from secureflow.prompts import build_fix_prompt
from secureflow.triage import (
    batch_related_findings,
    compute_priority_score,
    determine_escalation,
)

logger = logging.getLogger("secureflow")


class SecureFlowOrchestrator:
    def __init__(self, settings: Settings, db: Session):
        self.settings = settings
        self.db = db
        self.github = GitHubCodeQLClient(
            settings.github_token, settings.github_owner, settings.github_repo
        )
        self.devin = DevinClient(settings.devin_api_key, settings.devin_base_url)
        self.notifications = NotificationService(db)

    async def run_pipeline(self) -> PipelineRun:
        run = PipelineRun()
        self.db.add(run)
        self.db.commit()

        try:
            # 1. Fetch & sync alerts
            new_findings = await self._fetch_and_sync_alerts()
            run.alerts_fetched = len(new_findings)
            logger.info("Fetched %d new alerts", len(new_findings))

            # 2. Triage
            triaged = self._triage_findings(new_findings)
            auto_fix = [f for f in triaged if f.escalation_level == "auto_fix"]
            assist = [f for f in triaged if f.escalation_level == "assist"]
            escalated = [f for f in triaged if f.escalation_level == "escalate"]

            logger.info(
                "Triage: %d auto_fix, %d assist, %d escalate",
                len(auto_fix), len(assist), len(escalated),
            )

            # 3. Dispatch to Devin
            fixable = auto_fix + assist
            batches = batch_related_findings([f.to_alert_dict() for f in fixable])

            sessions_created = 0
            for batch in batches:
                if sessions_created >= self.settings.max_concurrent_sessions:
                    break
                await self._dispatch_batch(batch)
                sessions_created += 1

            run.sessions_created = sessions_created

            # 4. Mark escalated findings
            for f in escalated:
                f.status = FindingStatus.ESCALATED.value
                self.notifications.send_escalation(f)
            run.escalated = len(escalated)

            # 5. Poll active sessions
            prs = await self._poll_active_sessions()
            run.prs_created = prs

            # 6. Daily digest
            self.notifications.send_daily_digest()

            run.status = "completed"
            run.completed_at = datetime.now(timezone.utc)

        except Exception:
            run.status = "failed"
            logger.exception("Pipeline run failed")

        self.db.commit()
        return run

    async def poll_sessions(self) -> int:
        """Standalone poll — called by background task."""
        return await self._poll_active_sessions()

    # ── Internal ────────────────────────────────────────────────

    async def _fetch_and_sync_alerts(self) -> list[Finding]:
        raw = await self.github.get_open_alerts()
        new_findings: list[Finding] = []

        for alert in raw:
            norm = self.github.normalize_alert(alert)
            exists = (
                self.db.query(Finding)
                .filter_by(github_alert_number=norm["github_alert_number"])
                .first()
            )
            if not exists:
                finding = Finding(**norm)
                self.db.add(finding)
                new_findings.append(finding)

        self.db.commit()
        return new_findings

    def _triage_findings(self, findings: list[Finding]) -> list[Finding]:
        for f in findings:
            d = f.to_alert_dict()
            f.priority_score = compute_priority_score(d)
            f.escalation_level = determine_escalation(d)
            f.status = FindingStatus.QUEUED.value
        self.db.commit()
        return sorted(findings, key=lambda f: f.priority_score or 0, reverse=True)

    async def _dispatch_batch(self, batch: list[dict]):
        repo_url = f"https://github.com/{self.settings.github_owner}/{self.settings.github_repo}"
        prompt = build_fix_prompt(batch[0], repo_url, batch if len(batch) > 1 else None)

        # Rich tags for organization and filtering in Devin dashboard
        tags = ["secureflow", batch[0].get("severity", "medium")]
        if batch[0].get("cwe"):
            tags.append(batch[0]["cwe"])
        if batch[0].get("file_path"):
            tags.append(f"file:{batch[0]['file_path']}")

        result = await self.devin.create_session(
            prompt=prompt,
            tags=tags,
            playbook_id=self.settings.devin_playbook_id or None,
        )
        session_id = result.get("session_id", "")
        session_url = result.get("url", "")

        for item in batch:
            finding = (
                self.db.query(Finding)
                .filter_by(github_alert_number=item["github_alert_number"])
                .first()
            )
            if finding:
                finding.devin_session_id = session_id
                finding.devin_session_url = session_url
                finding.status = FindingStatus.IN_PROGRESS.value
                finding.devin_started_at = datetime.now(timezone.utc)

        self.db.commit()
        logger.info("Dispatched Devin session %s for %d findings", session_id, len(batch))

    async def _poll_active_sessions(self) -> int:
        active = self.db.query(Finding).filter_by(status=FindingStatus.IN_PROGRESS.value).all()
        prs_created = 0
        seen: set[str] = set()

        for finding in active:
            sid = finding.devin_session_id
            if not sid or sid in seen:
                continue
            seen.add(sid)

            try:
                session = await self.devin.get_session(sid)
            except Exception:
                logger.warning("Failed to poll session %s", sid)
                continue

            status_key = session.get("status_enum", session.get("status", ""))

            # Timeout check
            if finding.devin_started_at:
                started = finding.devin_started_at
                if started.tzinfo is None:
                    started = started.replace(tzinfo=timezone.utc)
                elapsed = datetime.now(timezone.utc) - started
                if elapsed > timedelta(minutes=self.settings.session_timeout_minutes):
                    self._escalate_session(sid, "Devin session timed out")
                    continue

            if status_key in ("finished", "stopped"):
                pr_info = session.get("pull_request") or {}
                pr_url = pr_info.get("url", pr_info.get("html_url", ""))
                linked = self.db.query(Finding).filter_by(devin_session_id=sid).all()

                confidence = await self._compute_confidence(sid, session)

                for f in linked:
                    if pr_url:
                        f.status = FindingStatus.PR_CREATED.value
                        f.pr_url = pr_url
                        f.confidence_score = confidence
                        f.devin_completed_at = datetime.now(timezone.utc)
                        prs_created += 1
                        self.notifications.send_pr_created(f)
                    else:
                        f.status = FindingStatus.ESCALATED.value
                        self.notifications.send_escalation(f, "Devin finished without creating a PR")

            elif status_key in ("failed", "errored"):
                self._escalate_session(sid, f"Devin session {status_key}")

        self.db.commit()
        return prs_created

    async def _compute_confidence(self, session_id: str, session_data: dict) -> float:
        """Score 0.0–1.0 based on session outcome signals."""
        score = 0.0

        # Session completed successfully (0.3)
        status = session_data.get("status_enum", session_data.get("status", ""))
        if status == "finished":
            score += 0.3

        # PR was created (0.3)
        pr_info = session_data.get("pull_request") or {}
        if pr_info.get("url") or pr_info.get("html_url"):
            score += 0.3

        # Session insights — check for errors/test signals (0.25)
        try:
            insights = await self.devin.get_session_insights(session_id)
            analysis = insights.get("analysis", "")
            if "error" not in analysis.lower() and "fail" not in analysis.lower():
                score += 0.25
            elif "test" in analysis.lower() and "pass" in analysis.lower():
                score += 0.15
            else:
                score += 0.10
        except Exception:
            score += 0.10  # neutral when insights unavailable

        # First attempt bonus (0.15)
        score += 0.15

        return round(min(score, 1.0), 2)

    async def redispatch_with_feedback(self, finding: Finding, rejection_reason: str):
        """Create a new Devin session with original context plus rejection feedback."""
        repo_url = f"https://github.com/{self.settings.github_owner}/{self.settings.github_repo}"
        alert_dict = finding.to_alert_dict()
        original_prompt = build_fix_prompt(alert_dict, repo_url)

        feedback_prompt = f"""{original_prompt}

## IMPORTANT: Previous Attempt Was Rejected
The previous fix attempt was rejected by a reviewer. Address the following feedback:

**Rejection Reason**: {rejection_reason}

Previous Devin session: {finding.devin_session_url or 'N/A'}
Previous PR: {finding.pr_url or 'N/A'}

Create an improved fix that addresses this feedback. Use a NEW branch and PR.
"""
        tags = [
            "secureflow",
            finding.severity or "medium",
            "retry",
            f"attempt-{finding.retry_count}",
        ]
        if finding.cwe:
            tags.append(finding.cwe)

        result = await self.devin.create_session(
            prompt=feedback_prompt,
            tags=tags,
            playbook_id=self.settings.devin_playbook_id or None,
        )

        finding.devin_session_id = result.get("session_id", "")
        finding.devin_session_url = result.get("url", "")
        finding.status = FindingStatus.IN_PROGRESS.value
        finding.devin_started_at = datetime.now(timezone.utc)
        finding.pr_url = None
        finding.pr_number = None
        finding.confidence_score = None
        self.db.commit()

        self.notifications.send_escalation(
            finding,
            f"Re-dispatched to Devin (attempt {finding.retry_count}): {rejection_reason}",
        )

    def _escalate_session(self, session_id: str, reason: str):
        linked = self.db.query(Finding).filter_by(devin_session_id=session_id).all()
        for f in linked:
            f.status = FindingStatus.ESCALATED.value
            self.notifications.send_escalation(f, reason)

