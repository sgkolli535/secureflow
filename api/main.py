import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from secureflow.config import settings
from secureflow.database import SessionLocal, init_db
from secureflow.orchestrator import SecureFlowOrchestrator

from api.routes import dashboard, findings, notifications, pipeline, webhooks

logger = logging.getLogger("secureflow")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(levelname)s: %(message)s")

_poll_task: asyncio.Task | None = None


async def _background_poller():
    """Continuously poll active Devin sessions."""
    while True:
        db = SessionLocal()
        try:
            orch = SecureFlowOrchestrator(settings, db)
            prs = await orch.poll_sessions()
            if prs:
                logger.info("Background poll: %d PRs detected", prs)
        except Exception:
            logger.exception("Background poll error")
        finally:
            db.close()
        await asyncio.sleep(settings.poll_interval_seconds)


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _poll_task
    init_db()
    logger.info("Database initialized")
    _poll_task = asyncio.create_task(_background_poller())
    yield
    if _poll_task:
        _poll_task.cancel()


app = FastAPI(title="SecureFlow API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(findings.router, prefix="/api/findings", tags=["findings"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["dashboard"])
app.include_router(notifications.router, prefix="/api/notifications", tags=["notifications"])
app.include_router(pipeline.router, prefix="/api/pipeline", tags=["pipeline"])
app.include_router(webhooks.router, prefix="/api/webhooks", tags=["webhooks"])
