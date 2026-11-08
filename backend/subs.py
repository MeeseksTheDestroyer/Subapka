from datetime import date
from decimal import Decimal
from typing import Literal

import pymysql
from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel, Field

from db import get_db

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])

Status = Literal["active", "cancelled"]

COLUMNS = "id, name, price, currency, type, renewal_date, user_id, status, created_at"


class SubCreate(BaseModel):
    name: str 
    price: Decimal
    currency: str 
    type: str 
    renewal_date: date
    user_id: int 
    status: Status = "active"

class SubUpdate(BaseModel):
    name: str
    price: Decimal = Field(gt=0)
    currency: str = Field(min_length=3, max_length=3)
    type: str
    renewal_date: date
    user_id: int
    status: Status


class SubPatch(BaseModel):
    name: str | None = None
    price: Decimal | None = Field(default=None, gt=0)
    currency: str | None = Field(default=None, min_length=3, max_length=3)
    type: str | None = None
    renewal_date: date | None = None
    user_id: int | None = None
    status: Status | None = None


@router.get("")
def get_subs(user_id: int | None = None, status: Status | None = None, db=Depends(get_db)):
    query = f"SELECT {COLUMNS} FROM subscriptions WHERE 1=1"
    params = []
    if user_id is not None:
        query += " AND user_id = %s"
        params.append(user_id)
    if status is not None:
        query += " AND status = %s"
        params.append(status)
    query += " ORDER BY renewal_date, id"

    with db.cursor() as cur:
        cur.execute(query, params)
        return {"items": cur.fetchall()}


@router.get("/{sub_id}")
def get_sub(sub_id: int, db=Depends(get_db)):
    with db.cursor() as cur:
        cur.execute(f"SELECT {COLUMNS} FROM subscriptions WHERE id = %s", (sub_id,))
        row = cur.fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Nie ma takiej subskrypcji")
        return {"items": row}


@router.post("")
def create_sub(sub: SubCreate, db=Depends(get_db)):
    try:
        with db.cursor() as cur:
            cur.execute(
                "INSERT INTO subscriptions (name, price, currency, type, renewal_date, user_id, status) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (sub.name, sub.price, sub.currency, sub.type, sub.renewal_date, sub.user_id, sub.status),
            )
            new_id = cur.lastrowid
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail="Nieznany typ subskrypcji albo użytkownik")

    return {"ok": True}

def _get_sub_or_404(cur, sub_id: int):
    cur.execute(f"SELECT {COLUMNS} FROM subscriptions WHERE id = %s", (sub_id,))
    row = cur.fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Nie ma takiej subskrypcji")
    return row


def _update_sub(sub_id: int, fields: dict, db):
    if not fields:
        raise HTTPException(status_code=400, detail="Brak pól do aktualizacji")
    try:
        with db.cursor() as cur:
            sub = _get_sub_or_404(cur, sub_id)
            set_clause = ", ".join(f"{col} = %s" for col in fields)
            cur.execute(f"UPDATE subscriptions SET {set_clause} WHERE id = %s", (*fields.values(), sub_id))
            
            db.commit()
            
            return {"items": sub}

    except pymysql.IntegrityError as e:
        db.rollback()
        print(f"Error updating subscription: {e}")
        raise HTTPException(status_code=400, detail="Nieznany typ subskrypcji albo użytkownik")


@router.put("/{sub_id}")
def replace_sub(sub_id: int, sub: SubUpdate, db=Depends(get_db)):
    return _update_sub(sub_id, sub.model_dump(), db)


@router.patch("/{sub_id}")
def update_sub(sub_id: int, sub: SubPatch, db=Depends(get_db)):
    return _update_sub(sub_id, sub.model_dump(exclude_unset=True, exclude_none=True), db)
