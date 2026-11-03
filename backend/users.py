from datetime import datetime
import pymysql
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
        cur.execute("SELECT id, name, email, created_at FROM users ORDER BY id")
        return {"items": cur.fetchall()}

@router.get("/{id}")
def get_user(id: int, db=Depends(get_db)):
    with db.cursor() as cur:
        cur.execute("SELECT id, name, email, created_at FROM users WHERE id = %s", (id,))
        row = cur.fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Nie ma takiego uzytkownika")
        return {"items": row}

@router.post("")
def create_user(user: UserType, db=Depends(get_db)):
    try:    
        with db.cursor() as cur:
            cur.execute(
                "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",
                (user.name, user.email, user.password),
            )
            db.commit()
    except pymysql.IntegrityError as e:
        db.rollback()
        print(f"Error creating user: {e}")
        raise HTTPException(status_code=400, detail="Uzytkownik z takim emailem juz istnieje")

        return {"ok": True}
