from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from db import get_db
from models import User

EMAIL_PATTERN = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"

class UserCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: str = Field(pattern=EMAIL_PATTERN, max_length=255)
    password: str = Field(min_length=8, max_length=128)

class UserUpdate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: str = Field(pattern=EMAIL_PATTERN, max_length=255)
    password: str = Field(min_length=8, max_length=128)

class UserPatch(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    email: str | None = Field(default=None, pattern=EMAIL_PATTERN, max_length=255)
    password: str | None = Field(default=None, min_length=8, max_length=128)

class UserOut(BaseModel):
    """To, co API zwraca o uzytkowniku (bez hasla)."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str
    created_at: datetime



router = APIRouter(prefix="/users", tags=["users"])

@router.get("")
def get_users(db: Session = Depends(get_db)):
    users = db.scalars(select(User).order_by(User.id)).all()
    return {"items": [UserOut.model_validate(user) for user in users]}

@router.get("/{id}")
def get_user(id: int, db: Session = Depends(get_db)):
    return {"items": UserOut.model_validate(_get_user_or_404(db, id))}

@router.post("")
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    new_user = User(**user.model_dump())
    db.add(new_user)
    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        print(f"Error creating user: {e.orig}")
        raise HTTPException(status_code=400, detail="Uzytkownik z takim emailem juz istnieje")

    return {"ok": True, "id": new_user.id}


def _get_user_or_404(db: Session, id: int) -> User:
    user = db.get(User, id)
    if user is None:
        raise HTTPException(status_code=404, detail="Nie ma takiego uzytkownika")
    return user


def _update_user(id: int, fields: dict, db: Session):
    if not fields:
        raise HTTPException(status_code=400, detail="Brak pol do aktualizacji")

    user = _get_user_or_404(db, id)
    for field, value in fields.items():
        setattr(user, field, value)

    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        print(f"Error updating user: {e.orig}")
        raise HTTPException(status_code=400, detail="Uzytkownik z takim emailem lub nazwa juz istnieje")

    return {"items": UserOut.model_validate(user)}


@router.put("/{id}")
def replace_user(id: int, user: UserUpdate, db: Session = Depends(get_db)):
    return _update_user(id, user.model_dump(), db)


@router.patch("/{id}")
def update_user(id: int, user: UserPatch, db: Session = Depends(get_db)):
    return _update_user(id, user.model_dump(exclude_unset=True, exclude_none=True), db)
