import hashlib
import hmac
import logging

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from sqlalchemy.orm import Session

from secureflow.config import settings
from secureflow.database import get_db
from secureflow.orchestrator import SecureFlowOrchestrator

logger = logging.getLogger("secureflow")
router = APIRouter()


def _verify_signature(payload: bytes, signature: str, secret: str) -> bool:
    if not secret or not signature:
        return False
    expected = "sha256=" + hmac.new(
        secret.encode(), payload, hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature)


@router.post("/github")
async def github_webhook(
    request: Request,
    db: Session = Depends(get_db),
    x_hub_signature_256: str = Header(default=""),
    x_github_event: str = Header(default=""),
):
    body = await request.body()

    # Verify signature if a webhook secret is configured
    if settings.github_webhook_secret:
        if not _verify_signature(body, x_hub_signature_256, settings.github_webhook_secret):
            raise HTTPException(401, "Invalid webhook signature")

    # Only act on code_scanning_alert events
    if x_github_event != "code_scanning_alert":
        return {"status": "ignored", "event": x_github_event}

    payload = await request.json()
    action = payload.get("action", "")
    if action not in ("created", "reopened", "appeared_in_branch"):
        return {"status": "ignored", "action": action}

    logger.info("GitHub webhook: code_scanning_alert %s", action)

    orch = SecureFlowOrchestrator(settings, db)
    run = await orch.run_pipeline()

    return {
        "status": "pipeline_triggered",
        "run_id": run.id,
        "alerts_fetched": run.alerts_fetched,
        "sessions_created": run.sessions_created,
    }
