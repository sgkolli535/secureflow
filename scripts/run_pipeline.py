#!/usr/bin/env python3
"""One-shot pipeline run — fetches CodeQL alerts, triages, dispatches to Devin."""

import asyncio
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from secureflow.config import settings
from secureflow.database import SessionLocal, init_db
from secureflow.models import Finding, FindingStatus
from secureflow.orchestrator import SecureFlowOrchestrator

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(levelname)s: %(message)s")
logger = logging.getLogger("secureflow")


async def main():
    init_db()
    db = SessionLocal()

    try:
        logger.info("Starting SecureFlow pipeline...")
        logger.info("Repo: %s/%s", settings.github_owner, settings.github_repo)
        logger.info("Slack: %s", "enabled" if settings.slack_enabled else "mock mode (set SLACK_ENABLED=true to send real notifications)")
        if settings.devin_playbook_id:
            logger.info("Playbook: %s", settings.devin_playbook_id)

        orch = SecureFlowOrchestrator(settings, db)
        run = await orch.run_pipeline()

        logger.info("Pipeline %s — ID: %d", run.status, run.id)
        logger.info(
            "  Alerts fetched: %d | Sessions created: %d | PRs: %d | Escalated: %d",
            run.alerts_fetched, run.sessions_created, run.prs_created, run.escalated,
        )

        # Summary of current state
        total = db.query(Finding).count()
        by_status = {}
        for st in FindingStatus:
            count = db.query(Finding).filter_by(status=st.value).count()
            if count > 0:
                by_status[st.value] = count

        logger.info("Current findings (%d total): %s", total, by_status)

        # Confidence summary
        with_confidence = (
            db.query(Finding)
            .filter(Finding.confidence_score.isnot(None))
            .all()
        )
        if with_confidence:
            scores = [f.confidence_score for f in with_confidence]
            avg = sum(scores) / len(scores)
            low = [f for f in with_confidence if f.confidence_score < settings.confidence_threshold]
            logger.info(
                "Confidence: avg=%.0f%% | %d findings below %.0f%% threshold",
                avg * 100, len(low), settings.confidence_threshold * 100,
            )
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(main())
