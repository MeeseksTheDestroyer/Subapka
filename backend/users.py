import pymysql
from fastapi import APIRouter, Depends, HTTPException
from db import get_db
from pydantic import BaseModel, Field

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



router = APIRouter(prefix="/users", tags=["users"])

@router.get("")
def get_users(db=Depends(get_db)):
    with db.cursor() as cur:
        cur.execute("SELECT id, name, email, created_at FROM users ORDER BY id")
        return {"items": cur.fetchall()}

@router.get("/{id}")
def get_user(id: int, db=Depends(get_db)):
    with db.cursor() as cur:
        return {"items": _get_user_or_404(cur, id)}

@router.post("")
def create_user(user: UserCreate, db=Depends(get_db)):
    try:
        with db.cursor() as cur:
            cur.execute(
                "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",
                (user.name, user.email, user.password),
            )
            new_id = cur.lastrowid
        db.commit()
    except pymysql.IntegrityError as e:
        db.rollback()
        print(f"Error creating user: {e}")
        raise HTTPException(status_code=400, detail="Uzytkownik z takim emailem juz istnieje")

    return {"ok": True, "id": new_id}


def _get_user_or_404(cur, id: int):
    cur.execute("SELECT id, name, email, created_at FROM users WHERE id = %s", (id,))
    row = cur.fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Nie ma takiego uzytkownika")
    return row


def _update_user(id: int, fields: dict, db):
    if not fields:
        raise HTTPException(status_code=400, detail="Brak pol do aktualizacji")
    try:
        with db.cursor() as cur:
            _get_user_or_404(cur, id)
            set_clause = ", ".join(f"{col} = %s" for col in fields)
            cur.execute(f"UPDATE users SET {set_clause} WHERE id = %s", (*fields.values(), id))
            db.commit()

            return {"items": _get_user_or_404(cur, id)}

    except pymysql.IntegrityError as e:
        db.rollback()
        print(f"Error updating user: {e}")
        raise HTTPException(status_code=400, detail="Uzytkownik z takim emailem lub nazwa juz istnieje")


@router.put("/{id}")
def replace_user(id: int, user: UserUpdate, db=Depends(get_db)):
    return _update_user(id, user.model_dump(), db)


@router.patch("/{id}")
def update_user(id: int, user: UserPatch, db=Depends(get_db)):
    return _update_user(id, user.model_dump(exclude_unset=True, exclude_none=True), db)