from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from secureflow.config import settings
from secureflow.database import get_db
from secureflow.models import PipelineRun
from secureflow.orchestrator import SecureFlowOrchestrator

router = APIRouter()


@router.post("/run")
async def trigger_pipeline(db: Session = Depends(get_db)):
    orch = SecureFlowOrchestrator(settings, db)
    run = await orch.run_pipeline()
    return {
        "id": run.id,
        "status": run.status,
        "alerts_fetched": run.alerts_fetched,
        "sessions_created": run.sessions_created,
        "prs_created": run.prs_created,
        "escalated": run.escalated,
    }


@router.get("/runs")
def list_runs(limit: int = 20, db: Session = Depends(get_db)):
    runs = db.query(PipelineRun).order_by(PipelineRun.started_at.desc()).limit(limit).all()
    return {
        "runs": [
            {
                "id": r.id,
                "started_at": r.started_at.isoformat() if r.started_at else None,
                "completed_at": r.completed_at.isoformat() if r.completed_at else None,
                "alerts_fetched": r.alerts_fetched,
                "sessions_created": r.sessions_created,
                "prs_created": r.prs_created,
                "escalated": r.escalated,
                "status": r.status,
            }
            for r in runs
        ]
    }
