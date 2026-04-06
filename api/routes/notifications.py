from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from secureflow.database import get_db
from secureflow.models import Notification

router = APIRouter()


@router.get("")
def list_notifications(
    channel: Optional[str] = None,
    notification_type: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    q = db.query(Notification)
    if channel:
        q = q.filter(Notification.channel == channel)
    if notification_type:
        q = q.filter(Notification.notification_type == notification_type)

    notifications = q.order_by(Notification.created_at.desc()).limit(limit).all()

    return {
        "notifications": [
            {
                "id": n.id,
                "channel": n.channel,
                "message": n.message,
                "notification_type": n.notification_type,
                "created_at": n.created_at.isoformat() if n.created_at else None,
                "finding_id": n.finding_id,
            }
            for n in notifications
        ]
    }
