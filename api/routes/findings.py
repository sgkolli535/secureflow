from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from secureflow.config import settings
from secureflow.database import get_db
from secureflow.models import Finding, FindingStatus
from secureflow.orchestrator import SecureFlowOrchestrator

router = APIRouter()


class FindingOut(BaseModel):
    id: int
    github_alert_number: int
    rule_id: str | None
    rule_name: str | None
    severity: str | None
    cwe: str | None
    description: str | None
    file_path: str | None
    start_line: int | None
    end_line: int | None
    html_url: str | None
    status: str | None
    escalation_level: str | None
    priority_score: float | None
    devin_session_id: str | None
    devin_session_url: str | None
    pr_url: str | None
    pr_number: int | None
    confidence_score: float | None
    rejection_reason: str | None
    retry_count: int | None
    first_seen: str | None
    last_updated: str | None
    devin_started_at: str | None
    devin_completed_at: str | None
    batch_id: str | None

    class Config:
        from_attributes = True


class FindingUpdate(BaseModel):
    status: Optional[str] = None
    escalation_level: Optional[str] = None


class RejectRequest(BaseModel):
    rejection_reason: str


def _to_out(f: Finding) -> dict:
    d = {c.name: getattr(f, c.name) for c in f.__table__.columns}
    for k in ("first_seen", "last_updated", "devin_started_at", "devin_completed_at"):
        if d.get(k):
            d[k] = d[k].isoformat()
    return d


@router.get("")
def list_findings(
    severity: Optional[str] = None,
    status: Optional[str] = None,
    escalation_level: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    q = db.query(Finding)
    if severity:
        q = q.filter(Finding.severity == severity)
    if status:
        q = q.filter(Finding.status == status)
    if escalation_level:
        q = q.filter(Finding.escalation_level == escalation_level)

    total = q.count()
    findings = q.order_by(Finding.priority_score.desc().nullslast()).offset(offset).limit(limit).all()

    return {"total": total, "findings": [_to_out(f) for f in findings]}


@router.get("/{finding_id}")
def get_finding(finding_id: int, db: Session = Depends(get_db)):
    f = db.query(Finding).filter_by(id=finding_id).first()
    if not f:
        raise HTTPException(404, "Finding not found")
    return _to_out(f)


@router.patch("/{finding_id}")
def update_finding(finding_id: int, body: FindingUpdate, db: Session = Depends(get_db)):
    f = db.query(Finding).filter_by(id=finding_id).first()
    if not f:
        raise HTTPException(404, "Finding not found")
    if body.status is not None:
        f.status = body.status
    if body.escalation_level is not None:
        f.escalation_level = body.escalation_level
    db.commit()
    return _to_out(f)


@router.post("/{finding_id}/reject")
async def reject_finding(
    finding_id: int,
    body: RejectRequest,
    db: Session = Depends(get_db),
):
    """Reject a PR fix and re-dispatch to Devin with feedback."""
    f = db.query(Finding).filter_by(id=finding_id).first()
    if not f:
        raise HTTPException(404, "Finding not found")
    if f.status != FindingStatus.PR_CREATED.value:
        raise HTTPException(400, "Can only reject findings with status pr_created")

    f.status = FindingStatus.REJECTED.value
    f.rejection_reason = body.rejection_reason
    f.retry_count = (f.retry_count or 0) + 1
    db.commit()

    orch = SecureFlowOrchestrator(settings, db)
    await orch.redispatch_with_feedback(f, body.rejection_reason)

    return _to_out(f)
