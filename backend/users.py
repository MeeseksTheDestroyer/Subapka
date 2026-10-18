from datetime import datetime

from fastapi import APIRouter, Depends
from db import get_db
from pydantic import BaseModel

class UserType(BaseModel):
    id: int
    name: str
    email : str
    password: str
    created_at: datetime | None = None

router = APIRouter(prefix="/users", tags=["users"])

@router.get("")
def get_users(db=Depends(get_db)):
    with db.cursor() as cur:
        cur.execute("SELECT id, name, email, password, created_at FROM users ORDER BY id")
        return {"items": cur.fetchall()}

@router.get("/{id}")
def get_user(id: int, db=Depends(get_db)):
    with db.cursor() as cur:
        cur.execute("SELECT id, name, email, password, created_at FROM users WHERE id = %s", (id,))
        return {"items": cur.fetchone()}

@router.post("")
def create_user(user: UserType, db=Depends(get_db)):
    with db.cursor() as cur:
        try:
            cur.execute(
                "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",
                (user.name, user.email, user.password),
            )
            db.commit()
        except Exception as e:
            db.rollback()
            print(f"Error creating user: {e}")
            return {"ok": False, "error": str(e)}

        return {"ok": True}