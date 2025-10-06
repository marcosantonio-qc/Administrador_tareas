from __future__ import annotations
from sqlalchemy.orm import Session
from app.models.models import AuditLog


def log_audit(db: Session, user_id: int | None, action: str, entity: str, entity_id: str, detail: str | None = None) -> None:
    log = AuditLog(user_id=user_id, action=action, entity=entity, entity_id=str(entity_id), detail=detail)
    db.add(log)
    db.flush()
