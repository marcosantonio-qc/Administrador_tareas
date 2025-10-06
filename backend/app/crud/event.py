from __future__ import annotations
from datetime import time
from sqlalchemy.orm import Session
from sqlalchemy import and_, text
from fastapi import HTTPException, status
from app.models.models import Event, EventStatusEnum
from app.services.audit import log_audit
from app.core.emailer import send_email
from app.schemas.schemas import EventCreate, EventUpdate


def _times_overlap(start_a: time, end_a: time, start_b: time, end_b: time) -> bool:
    return start_a < end_b and start_b < end_a


def check_room_availability(db: Session, room_id: int, date, start_time: time, end_time: time, exclude_event_id: int | None = None) -> bool:
    q = db.query(Event).filter(Event.room_id == room_id, Event.date == date)
    if exclude_event_id:
        q = q.filter(Event.id != exclude_event_id)
    events = q.all()
    for ev in events:
        if ev.status != EventStatusEnum.cancelled and _times_overlap(start_time, end_time, ev.start_time, ev.end_time):
            return False
    return True


def create_event(db: Session, data: EventCreate, user_id: int | None) -> Event:
    if data.start_time >= data.end_time:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="start_time must be before end_time")

    # Use sp_getapplock to serialize creation per room per date
    lock_name = f"room:{data.room_id}:date:{data.date.isoformat()}"
    db.execute(text("EXEC sp_getapplock @Resource=:res, @LockMode='Exclusive', @LockTimeout=5000"), {"res": lock_name})
    try:
        if not check_room_availability(db, data.room_id, data.date, data.start_time, data.end_time):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Room not available for the selected time range")

        ev = Event(
            name=data.name,
            type=data.type,
            organizer=data.organizer,
            attendees=data.attendees,
            room_id=data.room_id,
            date=data.date,
            start_time=data.start_time,
            end_time=data.end_time,
            description=data.description,
            contact=data.contact,
            status=data.status,
            created_by_id=user_id,
            updated_by_id=user_id,
        )
        db.add(ev)
        db.flush()  # get ID
        log_audit(db, user_id, "create", "event", str(ev.id), detail=f"Created event {ev.name} on {ev.date}")
        if ev.contact:
            try:
                send_email(
                    subject=f"Reserva creada: {ev.name}",
                    body=f"Su reserva fue creada para {ev.date} {ev.start_time}-{ev.end_time}.",
                    to_address=ev.contact,
                )
            except Exception:
                pass
        return ev
    finally:
        db.execute(text("EXEC sp_releaseapplock @Resource=:res"), {"res": lock_name})


def update_event(db: Session, event_id: int, data: EventUpdate, user_id: int | None) -> Event:
    ev = db.query(Event).filter(Event.id == event_id).first()
    if not ev:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")

    # compute new values
    new_room_id = data.room_id or ev.room_id
    new_date = data.date or ev.date
    new_start = data.start_time or ev.start_time
    new_end = data.end_time or ev.end_time

    if new_start >= new_end:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="start_time must be before end_time")

    lock_name = f"room:{new_room_id}:date:{new_date.isoformat()}"
    db.execute(text("EXEC sp_getapplock @Resource=:res, @LockMode='Exclusive', @LockTimeout=5000"), {"res": lock_name})
    try:
        if not check_room_availability(db, new_room_id, new_date, new_start, new_end, exclude_event_id=ev.id):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Room not available for the selected time range")
        # apply updates
        for field, value in data.dict(exclude_unset=True).items():
            setattr(ev, field, value)
        ev.updated_by_id = user_id
        db.flush()
        log_audit(db, user_id, "update", "event", str(ev.id), detail=f"Updated event {ev.name}")
        if ev.contact:
            try:
                send_email(
                    subject=f"Reserva actualizada: {ev.name}",
                    body=f"Su reserva fue actualizada para {ev.date} {ev.start_time}-{ev.end_time}.",
                    to_address=ev.contact,
                )
            except Exception:
                pass
        return ev
    finally:
        db.execute(text("EXEC sp_releaseapplock @Resource=:res"), {"res": lock_name})


def delete_event(db: Session, event_id: int):
    ev = db.query(Event).filter(Event.id == event_id).first()
    if not ev:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    log_audit(db, None, "delete", "event", str(ev.id), detail=f"Deleted event {ev.name}")
    db.delete(ev)
