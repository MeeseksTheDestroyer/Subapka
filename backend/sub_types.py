import pymysql
from fastapi import APIRouter, Depends, HTTPException
from db import get_db
from pydantic import BaseModel, Field

class SubType(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    label: str = Field(min_length=1, max_length=100)

class SubTypeUpdate(BaseModel):
    label: str = Field(min_length=1, max_length=100)

class SubTypePatch(BaseModel):
    label: str | None = Field(default=None, min_length=1, max_length=100)



router = APIRouter(prefix="/types", tags=["types"])

@router.get("")
def get_types(db=Depends(get_db)):
    with db.cursor() as cur:
        cur.execute("SELECT name, label FROM types ORDER BY name")
        return {"items": cur.fetchall()}

@router.get("/{name}")
def get_type(name: str, db=Depends(get_db)):
    with db.cursor() as cur:
        return {"items": _get_type_or_404(cur, name)}


@router.post("")
def create_type(sub: SubType, db=Depends(get_db)):
    try:
        with db.cursor() as cur:
            cur.execute("INSERT INTO types (name, label) VALUES (%s, %s)", (sub.name, sub.label))
            db.commit()
    except pymysql.IntegrityError as e:
        db.rollback()
        print(f"Error creating type: {e}")
        raise HTTPException(status_code=400, detail="Taki typ juz istnieje")

    return {"items": {"name": sub.name, "label": sub.label}}

def _get_type_or_404(cur, name: str):
    cur.execute("SELECT name, label FROM types WHERE name = %s", (name,))
    row = cur.fetchone()

    if row is None:
        raise HTTPException(status_code=404, detail="Nie ma takiego typu")

    return row


def _update_type(name: str, fields: dict, db):
    if not fields:
        raise HTTPException(status_code=400, detail="Brak pol do aktualizacji")
    try:
        with db.cursor() as cur:
            _get_type_or_404(cur, name)
            set_clause = ", ".join(f"{col} = %s" for col in fields)

            cur.execute(f"UPDATE types SET {set_clause} WHERE name = %s", (*fields.values(), name))
            db.commit()

            return {"items": _get_type_or_404(cur, name)}

    except pymysql.IntegrityError as e:
        db.rollback()
        print(f"Error updating type: {e}")
        raise HTTPException(status_code=400, detail="Nieprawidlowe dane typu")


@router.put("/{name}")
def replace_type(name: str, sub: SubTypeUpdate, db=Depends(get_db)):
    return _update_type(name, sub.model_dump(), db)


@router.patch("/{name}")
def update_type(name: str, sub: SubTypePatch, db=Depends(get_db)):
    return _update_type(name, sub.model_dump(exclude_unset=True, exclude_none=True), db)