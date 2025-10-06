from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.schemas.schemas import RoomCreate, RoomOut
from app.models.models import Room, RoleEnum
from app.deps.auth import require_role

router = APIRouter(prefix="/rooms", tags=["rooms"])


@router.get("/", response_model=List[RoomOut])
def list_rooms(db: Session = Depends(get_db)):
    return db.query(Room).filter(Room.is_active == True).order_by(Room.name).all()


@router.post("/", response_model=RoomOut, status_code=status.HTTP_201_CREATED)
def create_room(payload: RoomCreate, db: Session = Depends(get_db), user=Depends(require_role(RoleEnum.admin))):
    if db.query(Room).filter(Room.name == payload.name).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Room with same name exists")
    room = Room(**payload.dict())
    db.add(room)
    db.commit()
    db.refresh(room)
    return room
