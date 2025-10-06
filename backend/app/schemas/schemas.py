from __future__ import annotations
from pydantic import BaseModel, EmailStr, Field, constr
from datetime import date, time, datetime
from enum import Enum


class RoleEnum(str, Enum):
    admin = "admin"
    editor = "editor"
    viewer = "viewer"


class EventTypeEnum(str, Enum):
    internal = "internal"
    external = "external"


class EventStatusEnum(str, Enum):
    pending = "pending"
    confirmed = "confirmed"
    cancelled = "cancelled"


class UserCreate(BaseModel):
    email: EmailStr
    full_name: str
    password: constr(min_length=8)
    role: RoleEnum = RoleEnum.viewer


class UserOut(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    role: RoleEnum
    is_active: bool

    class Config:
        from_attributes = True


class RoomCreate(BaseModel):
    name: str
    location: str | None = None
    capacity: int = Field(ge=1)
    area: str | None = None


class RoomOut(BaseModel):
    id: int
    name: str
    location: str | None
    capacity: int
    area: str | None

    class Config:
        from_attributes = True


class EventBase(BaseModel):
    name: str
    type: EventTypeEnum
    organizer: str | None = None
    attendees: int | None = Field(default=None, ge=1)
    room_id: int
    date: date
    start_time: time
    end_time: time
    description: str | None = None
    contact: str | None = None
    status: EventStatusEnum = EventStatusEnum.pending


class EventCreate(EventBase):
    pass


class EventUpdate(BaseModel):
    name: str | None = None
    type: EventTypeEnum | None = None
    organizer: str | None = None
    attendees: int | None = Field(default=None, ge=1)
    room_id: int | None = None
    date: date | None = None
    start_time: time | None = None
    end_time: time | None = None
    description: str | None = None
    contact: str | None = None
    status: EventStatusEnum | None = None


class EventOut(EventBase):
    id: int
    created_at: datetime
    updated_at: datetime | None = None

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: str
    role: RoleEnum
    exp: int
