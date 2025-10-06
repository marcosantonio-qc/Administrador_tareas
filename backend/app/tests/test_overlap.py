import pytest
from datetime import date, time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.models.models import Room, Event, EventTypeEnum
from app.crud.event import check_room_availability


def setup_inmemory_db():
    # Use SQLite in-memory just for logic unit tests
    engine = create_engine("sqlite+pysqlite:///:memory:", echo=False)
    TestingSessionLocal = sessionmaker(bind=engine)
    Base.metadata.create_all(bind=engine)
    return engine, TestingSessionLocal


def test_time_overlap_logic():
    engine, SessionLocal = setup_inmemory_db()
    db = SessionLocal()

    room = Room(name="Salon A", location=None, capacity=100, area=None)
    db.add(room)
    db.flush()

    ev1 = Event(
        name="Evento 1",
        type=EventTypeEnum.internal,
        room_id=room.id,
        date=date(2025, 1, 1),
        start_time=time(10, 0),
        end_time=time(12, 0),
    )
    db.add(ev1)
    db.flush()

    assert check_room_availability(db, room.id, date(2025, 1, 1), time(8, 0), time(9, 0)) is True
    assert check_room_availability(db, room.id, date(2025, 1, 1), time(9, 0), time(10, 0)) is True
    assert check_room_availability(db, room.id, date(2025, 1, 1), time(10, 0), time(11, 0)) is False
    assert check_room_availability(db, room.id, date(2025, 1, 1), time(11, 0), time(12, 0)) is False
    assert check_room_availability(db, room.id, date(2025, 1, 1), time(12, 0), time(13, 0)) is True

    db.close()
