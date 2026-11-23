from datetime import datetime

import bcrypt
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

class UserLogin(BaseModel):
    email: str
    password: str

class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str
    created_at: datetime


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def check_password(password: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode(), hashed.encode())
    except ValueError:
        return False


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
    data = user.model_dump()
    data["password"] = hash_password(data["password"])
    new_user = User(**data)
    db.add(new_user)
    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        print(f"Error creating user: {e.orig}")
        raise HTTPException(status_code=400, detail="Uzytkownik z takim emailem juz istnieje")

    return {"ok": True, "id": new_user.id}


@router.post("/login")
def login(data: UserLogin, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == data.email))
    if user is None or not check_password(data.password, user.password):
        raise HTTPException(status_code=401, detail="Zly email albo haslo")
    return {"ok": True, "user": UserOut.model_validate(user)}


def _get_user_or_404(db: Session, id: int) -> User:
    user = db.get(User, id)
    if user is None:
        raise HTTPException(status_code=404, detail="Nie ma takiego uzytkownika")
    return user


def _update_user(id: int, fields: dict, db: Session):
    if not fields:
        raise HTTPException(status_code=400, detail="Brak pol do aktualizacji")

    if "password" in fields:
        fields["password"] = hash_password(fields["password"])

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
