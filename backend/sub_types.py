from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from db import get_db
from models import SubscriptionType

class SubType(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    label: str = Field(min_length=1, max_length=100)

class SubTypeUpdate(BaseModel):
    label: str = Field(min_length=1, max_length=100)

class SubTypePatch(BaseModel):
    label: str | None = Field(default=None, min_length=1, max_length=100)

class SubTypeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    label: str | None



router = APIRouter(prefix="/types", tags=["types"])

@router.get("")
def get_types(db: Session = Depends(get_db)):
    types = db.scalars(select(SubscriptionType).order_by(SubscriptionType.name)).all()
    return {"items": [SubTypeOut.model_validate(sub_type) for sub_type in types]}

@router.get("/{name}")
def get_type(name: str, db: Session = Depends(get_db)):
    return {"items": SubTypeOut.model_validate(_get_type_or_404(db, name))}


@router.post("")
def create_type(sub: SubType, db: Session = Depends(get_db)):
    new_type = SubscriptionType(**sub.model_dump())
    db.add(new_type)
    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        print(f"Error creating type: {e.orig}")
        raise HTTPException(status_code=400, detail="Taki typ juz istnieje")

    return {"items": SubTypeOut.model_validate(new_type)}

def _get_type_or_404(db: Session, name: str) -> SubscriptionType:
    sub_type = db.get(SubscriptionType, name)

    if sub_type is None:
        raise HTTPException(status_code=404, detail="Nie ma takiego typu")

    return sub_type


def _update_type(name: str, fields: dict, db: Session):
    if not fields:
        raise HTTPException(status_code=400, detail="Brak pol do aktualizacji")

    sub_type = _get_type_or_404(db, name)
    for field, value in fields.items():
        setattr(sub_type, field, value)

    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        print(f"Error updating type: {e.orig}")
        raise HTTPException(status_code=400, detail="Nieprawidlowe dane typu")

    return {"items": SubTypeOut.model_validate(sub_type)}


@router.put("/{name}")
def replace_type(name: str, sub: SubTypeUpdate, db: Session = Depends(get_db)):
    return _update_type(name, sub.model_dump(), db)


@router.patch("/{name}")
def update_type(name: str, sub: SubTypePatch, db: Session = Depends(get_db)):
    return _update_type(name, sub.model_dump(exclude_unset=True, exclude_none=True), db)
