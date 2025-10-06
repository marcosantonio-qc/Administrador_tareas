from __future__ import annotations
from sqlalchemy import Column, Date, DateTime, Enum, ForeignKey, Integer, String, Text, UniqueConstraint, func, Index, Boolean, Time
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.db.base import Base
import enum


class RoleEnum(str, enum.Enum):
    admin = "admin"
    editor = "editor"
    viewer = "viewer"


class EventTypeEnum(str, enum.Enum):
    internal = "internal"
    external = "external"


class EventStatusEnum(str, enum.Enum):
    pending = "pending"
    confirmed = "confirmed"
    cancelled = "cancelled"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[RoleEnum] = mapped_column(Enum(RoleEnum), nullable=False, default=RoleEnum.viewer)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.sysdatetime())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.sysdatetime(), onupdate=func.sysdatetime())


class Room(Base):
    __tablename__ = "rooms"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False, unique=True, index=True)
    location: Mapped[str] = mapped_column(String(255), nullable=True)
    capacity: Mapped[int] = mapped_column(Integer, nullable=False)
    area: Mapped[str] = mapped_column(String(120), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.sysdatetime())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.sysdatetime(), onupdate=func.sysdatetime())

    events: Mapped[list[Event]] = relationship("Event", back_populates="room")

    __table_args__ = (
        Index("ix_rooms_name", "name", unique=True),
    )


class Event(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[EventTypeEnum] = mapped_column(Enum(EventTypeEnum), nullable=False)
    organizer: Mapped[str | None] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text)
    contact: Mapped[str | None] = mapped_column(String(255))
    status: Mapped[EventStatusEnum] = mapped_column(Enum(EventStatusEnum), default=EventStatusEnum.pending, nullable=False)

    attendees: Mapped[int] = mapped_column(Integer, nullable=True)

    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id", ondelete="RESTRICT"), nullable=False, index=True)
    date: Mapped[Date] = mapped_column(Date, nullable=False, index=True)
    start_time: Mapped[Time] = mapped_column(Time, nullable=False)
    end_time: Mapped[Time] = mapped_column(Time, nullable=False)

    created_by_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    updated_by_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.sysdatetime())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.sysdatetime(), onupdate=func.sysdatetime())

    room: Mapped[Room] = relationship("Room", back_populates="events")

    __table_args__ = (
        # Fast search by room + date for overlap checks
        Index("ix_events_room_date", "room_id", "date"),
        # Prevent invalid times
        UniqueConstraint("room_id", "date", "start_time", "end_time", name="uq_room_date_time_exact"),
    )


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    action: Mapped[str] = mapped_column(String(64), nullable=False)
    entity: Mapped[str] = mapped_column(String(64), nullable=False)
    entity_id: Mapped[str] = mapped_column(String(64), nullable=False)
    detail: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.sysdatetime())
