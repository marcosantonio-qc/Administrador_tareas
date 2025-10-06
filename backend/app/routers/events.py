from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.schemas.schemas import EventCreate, EventOut, EventUpdate
from app.crud.event import create_event, update_event
from app.models.models import Event, RoleEnum
from app.deps.auth import get_current_user, require_role
from sqlalchemy import and_

router = APIRouter(prefix="/events", tags=["events"])


@router.get("/", response_model=List[EventOut])
def list_events(db: Session = Depends(get_db)):
    return db.query(Event).order_by(Event.date, Event.start_time).all()


@router.post("/", response_model=EventOut, status_code=status.HTTP_201_CREATED)
def create_event_endpoint(payload: EventCreate, db: Session = Depends(get_db), user=Depends(require_role(RoleEnum.admin, RoleEnum.editor))):
    ev = create_event(db, payload, user_id=user.id)
    db.commit()
    db.refresh(ev)
    return ev


@router.put("/{event_id}", response_model=EventOut)
def update_event_endpoint(event_id: int, payload: EventUpdate, db: Session = Depends(get_db), user=Depends(require_role(RoleEnum.admin, RoleEnum.editor))):
    ev = update_event(db, event_id, payload, user_id=user.id)
    db.commit()
    db.refresh(ev)
    return ev


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_event_endpoint(event_id: int, db: Session = Depends(get_db), user=Depends(require_role(RoleEnum.admin))):
    ev = db.query(Event).filter(Event.id == event_id).first()
    if not ev:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    db.delete(ev)
    db.commit()
    return None


@router.get("/by-room/{room_id}", response_model=List[EventOut])
def list_events_by_room(room_id: int, start_date: str | None = None, end_date: str | None = None, db: Session = Depends(get_db)):
    q = db.query(Event).filter(Event.room_id == room_id)
    if start_date:
        q = q.filter(Event.date >= start_date)
    if end_date:
        q = q.filter(Event.date <= end_date)
    return q.order_by(Event.date, Event.start_time).all()
