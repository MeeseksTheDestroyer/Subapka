from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from db import get_db
from models import Subscription

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])

Status = Literal["active", "cancelled"]


class SubCreate(BaseModel):
    name: str = Field(min_length=1)
    price: Decimal = Field(gt=0)
    currency: str = Field(min_length=3, max_length=3)
    type: str = Field(min_length=1)
    renewal_date: date
    user_id: int
    status: Status = "active"

class SubUpdate(BaseModel):
    name: str = Field(min_length=1)
    price: Decimal = Field(gt=0)
    currency: str = Field(min_length=3, max_length=3)
    type: str = Field(min_length=1)
    renewal_date: date
    user_id: int
    status: Status


class SubPatch(BaseModel):
    name: str | None = Field(default=None, min_length=1)
    price: Decimal | None = Field(default=None, gt=0)
    currency: str | None = Field(default=None, min_length=3, max_length=3)
    type: str | None = Field(default=None, min_length=1)
    renewal_date: date | None = None
    user_id: int | None = None
    status: Status | None = None


class SubOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    price: float
    currency: str
    type: str
    renewal_date: date
    user_id: int
    status: str
    created_at: datetime


@router.get("")
def get_subs(user_id: int | None = None, status: Status | None = None, db: Session = Depends(get_db)):
    query = select(Subscription)
    if user_id is not None:
        query = query.where(Subscription.user_id == user_id)
    if status is not None:
        query = query.where(Subscription.status == status)
    query = query.order_by(Subscription.renewal_date, Subscription.id)

    subs = db.scalars(query).all()
    return {"items": [SubOut.model_validate(sub) for sub in subs]}


@router.get("/{sub_id}")
def get_sub(sub_id: int, db: Session = Depends(get_db)):
    return {"items": SubOut.model_validate(_get_sub_or_404(db, sub_id))}


@router.post("")
def create_sub(sub: SubCreate, db: Session = Depends(get_db)):
    new_sub = Subscription(**sub.model_dump())
    db.add(new_sub)
    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        print(f"Error creating subscription: {e.orig}")
        raise HTTPException(status_code=400, detail="Nieznany typ subskrypcji albo użytkownik")

    return {"ok": True, "id": new_sub.id}

def _get_sub_or_404(db: Session, sub_id: int) -> Subscription:
    sub = db.get(Subscription, sub_id)
    if sub is None:
        raise HTTPException(status_code=404, detail="Nie ma takiej subskrypcji")
    return sub


def _update_sub(sub_id: int, fields: dict, db: Session):
    if not fields:
        raise HTTPException(status_code=400, detail="Brak pól do aktualizacji")

    sub = _get_sub_or_404(db, sub_id)
    for field, value in fields.items():
        setattr(sub, field, value)

    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        print(f"Error updating subscription: {e.orig}")
        raise HTTPException(status_code=400, detail="Nieznany typ subskrypcji albo użytkownik")

    return {"items": SubOut.model_validate(sub)}

def _delete_sub(sub_id: int, db: Session):
    sub = _get_sub_or_404(db, sub_id)

    try:
        db.delete(sub)
        db.commit()
    except IntegrityError as e:
        db.rollback()
        print(f"Error deleting subscription: {e.orig}")
        raise HTTPException(status_code=400, detail="Nie można usunąć subskrypcji")
    return sub

@router.put("/{sub_id}")
def replace_sub(sub_id: int, sub: SubUpdate, db: Session = Depends(get_db)):
    return _update_sub(sub_id, sub.model_dump(), db)


@router.patch("/{sub_id}")
def update_sub(sub_id: int, sub: SubPatch, db: Session = Depends(get_db)):
    return _update_sub(sub_id, sub.model_dump(exclude_unset=True, exclude_none=True), db)

@router.delete("/{sub_id}")
def delete_sub(sub_id: int, db: Session = Depends(get_db)):
    return _delete_sub(sub_id, db):