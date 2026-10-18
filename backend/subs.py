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

