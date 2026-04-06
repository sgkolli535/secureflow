from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from secureflow.database import get_db
from secureflow.models import Finding, Notification, PipelineRun

router = APIRouter()


@router.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    by_severity: dict[str, int] = {}
    for sev in ("critical", "high", "medium", "low"):
        by_severity[sev] = db.query(Finding).filter(Finding.severity == sev).count()

    by_status: dict[str, int] = {}
    for st in ("new", "queued", "in_progress", "pr_created", "merged", "escalated", "dismissed", "rejected"):
        by_status[st] = db.query(Finding).filter(Finding.status == st).count()

    total = db.query(Finding).count()
    fixed = by_status.get("merged", 0) + by_status.get("pr_created", 0)
    auto_fix_rate = round(fixed / total, 2) if total > 0 else 0.0

    # Mean time to fix (for completed findings)
    completed = (
        db.query(Finding)
        .filter(
            Finding.devin_started_at.isnot(None),
            Finding.devin_completed_at.isnot(None),
        )
        .all()
    )
    if completed:
        total_hours = sum(
            (f.devin_completed_at - f.devin_started_at).total_seconds() / 3600
            for f in completed
        )
        mttf_hours = round(total_hours / len(completed), 1)
    else:
        mttf_hours = None

    by_escalation: dict[str, int] = {}
    for lvl in ("auto_fix", "assist", "escalate"):
        by_escalation[lvl] = db.query(Finding).filter(Finding.escalation_level == lvl).count()

    return {
        "total": total,
        "by_severity": by_severity,
        "by_status": by_status,
        "by_escalation": by_escalation,
        "auto_fix_rate": auto_fix_rate,
        "mean_time_to_fix_hours": mttf_hours,
    }


@router.get("/compliance")
def get_compliance(db: Session = Depends(get_db)):
    """Compliance & audit reporting — the data you show your auditor."""
    now = datetime.now(timezone.utc)
    total = db.query(Finding).count()

    # Mean time to remediate (first_seen → devin_completed_at)
    completed = (
        db.query(Finding)
        .filter(Finding.first_seen.isnot(None), Finding.devin_completed_at.isnot(None))
        .all()
    )
    if completed:
        total_hours = sum(
            (f.devin_completed_at - f.first_seen).total_seconds() / 3600
            for f in completed
        )
        mttr_hours = round(total_hours / len(completed), 1)
    else:
        mttr_hours = None

    # Auto-fixed vs manual
    auto_fixed = db.query(Finding).filter(
        Finding.escalation_level == "auto_fix",
        Finding.status.in_(["pr_created", "merged"]),
    ).count()
    manual = db.query(Finding).filter(Finding.status == "escalated").count()
    auto_fix_pct = round(auto_fixed / total * 100, 1) if total else 0
    manual_pct = round(manual / total * 100, 1) if total else 0

    # Finding age distribution
    age_buckets = {"< 1 day": 0, "1-7 days": 0, "7-30 days": 0, "> 30 days": 0}
    open_findings = db.query(Finding).filter(
        Finding.status.in_(["new", "queued", "in_progress", "pr_created"])
    ).all()
    for f in open_findings:
        if f.first_seen:
            first = f.first_seen
            if first.tzinfo is None:
                first = first.replace(tzinfo=timezone.utc)
            age = now - first
            if age < timedelta(days=1):
                age_buckets["< 1 day"] += 1
            elif age < timedelta(days=7):
                age_buckets["1-7 days"] += 1
            elif age < timedelta(days=30):
                age_buckets["7-30 days"] += 1
            else:
                age_buckets["> 30 days"] += 1

    # Trend from recent pipeline runs
    recent_runs = db.query(PipelineRun).order_by(PipelineRun.started_at.desc()).limit(10).all()
    trend = [
        {
            "run_id": r.id,
            "date": r.started_at.isoformat() if r.started_at else None,
            "alerts_fetched": r.alerts_fetched,
            "prs_created": r.prs_created,
            "escalated": r.escalated,
        }
        for r in reversed(recent_runs)
    ]

    # Audit trail
    recent_notifs = db.query(Notification).order_by(
        Notification.created_at.desc()
    ).limit(100).all()
    audit_trail = [
        {
            "id": n.id,
            "type": n.notification_type,
            "channel": n.channel,
            "message": n.message,
            "created_at": n.created_at.isoformat() if n.created_at else None,
            "finding_id": n.finding_id,
        }
        for n in recent_notifs
    ]

    # CWE fix rates
    all_findings = db.query(Finding).filter(Finding.cwe.isnot(None), Finding.cwe != "").all()
    cwe_counts: dict[str, dict[str, int]] = {}
    for f in all_findings:
        cwe = f.cwe
        if cwe not in cwe_counts:
            cwe_counts[cwe] = {"total": 0, "fixed": 0}
        cwe_counts[cwe]["total"] += 1
        if f.status in ("pr_created", "merged"):
            cwe_counts[cwe]["fixed"] += 1
    cwe_fix_rates = [
        {
            "cwe": cwe,
            "total": counts["total"],
            "fixed": counts["fixed"],
            "rate": round(counts["fixed"] / counts["total"] * 100) if counts["total"] > 0 else 0,
        }
        for cwe, counts in sorted(cwe_counts.items())
    ]

    # Cumulative remediation timeline
    fixed_findings = (
        db.query(Finding)
        .filter(Finding.devin_completed_at.isnot(None))
        .order_by(Finding.devin_completed_at)
        .all()
    )
    remediation_timeline = []
    cumulative = 0
    for f in fixed_findings:
        cumulative += 1
        remediation_timeline.append({
            "date": f.devin_completed_at.isoformat() if f.devin_completed_at else None,
            "cumulative_fixed": cumulative,
            "cwe": f.cwe,
        })

    return {
        "mean_time_to_remediate_hours": mttr_hours,
        "auto_fix_percentage": auto_fix_pct,
        "manual_percentage": manual_pct,
        "finding_age_distribution": age_buckets,
        "trend": trend,
        "audit_trail": audit_trail,
        "total_findings": total,
        "total_fixed": auto_fixed,
        "total_escalated": manual,
        "cwe_fix_rates": cwe_fix_rates,
        "remediation_timeline": remediation_timeline,
    }
