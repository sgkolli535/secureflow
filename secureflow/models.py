import enum
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Severity(str, enum.Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class FindingStatus(str, enum.Enum):
    NEW = "new"
    QUEUED = "queued"
    IN_PROGRESS = "in_progress"
    PR_CREATED = "pr_created"
    MERGED = "merged"
    ESCALATED = "escalated"
    DISMISSED = "dismissed"
    REJECTED = "rejected"


class EscalationLevel(str, enum.Enum):
    AUTO_FIX = "auto_fix"
    ASSIST = "assist"
    ESCALATE = "escalate"


def _utcnow():
    return datetime.now(timezone.utc)


class Finding(Base):
    __tablename__ = "findings"

    id = Column(Integer, primary_key=True)
    github_alert_number = Column(Integer, unique=True, index=True)
    rule_id = Column(String)
    rule_name = Column(String)
    severity = Column(String)
    cwe = Column(String)
    description = Column(Text)
    file_path = Column(String)
    start_line = Column(Integer)
    end_line = Column(Integer)
    html_url = Column(String)

    # Pipeline state
    status = Column(String, default=FindingStatus.NEW.value)
    escalation_level = Column(String, nullable=True)
    priority_score = Column(Float, nullable=True)

    # Devin tracking
    devin_session_id = Column(String, nullable=True)
    devin_session_url = Column(String, nullable=True)

    # PR tracking
    pr_url = Column(String, nullable=True)
    pr_number = Column(Integer, nullable=True)

    # Timestamps
    first_seen = Column(DateTime, default=_utcnow)
    last_updated = Column(DateTime, default=_utcnow, onupdate=_utcnow)
    devin_started_at = Column(DateTime, nullable=True)
    devin_completed_at = Column(DateTime, nullable=True)

    # Confidence scoring
    confidence_score = Column(Float, nullable=True)

    # Feedback loop
    rejection_reason = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)

    # Batch tracking
    batch_id = Column(String, nullable=True)

    def to_alert_dict(self) -> dict:
        """Subset of fields used for triage and prompt building."""
        return {
            "github_alert_number": self.github_alert_number,
            "rule_id": self.rule_id,
            "rule_name": self.rule_name,
            "severity": self.severity,
            "cwe": self.cwe,
            "description": self.description,
            "file_path": self.file_path,
            "start_line": self.start_line,
            "end_line": self.end_line,
            "html_url": self.html_url,
        }


class PipelineRun(Base):
    __tablename__ = "pipeline_runs"

    id = Column(Integer, primary_key=True)
    started_at = Column(DateTime, default=_utcnow)
    completed_at = Column(DateTime, nullable=True)
    alerts_fetched = Column(Integer, default=0)
    sessions_created = Column(Integer, default=0)
    prs_created = Column(Integer, default=0)
    escalated = Column(Integer, default=0)
    status = Column(String, default="running")


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True)
    channel = Column(String)
    message = Column(Text)
    notification_type = Column(String)
    created_at = Column(DateTime, default=_utcnow)
    finding_id = Column(Integer, nullable=True)
