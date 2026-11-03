from fastapi import APIRouter, Depends
from db import get_db
from pydantic import BaseModel

class SubType(BaseModel):
    name: str
    label: str

router = APIRouter(prefix="/types", tags=["types"])

@router.get("")
def get_types(db=Depends(get_db)):
    with db.cursor() as cur:
        cur.execute("SELECT name, label FROM types ORDER BY name")
        return {"items": cur.fetchall()}

@router.get("/{name}")
def get_type(name: str, db=Depends(get_db)):
    with db.cursor() as cur:
        cur.execute("SELECT name, label FROM types WHERE name = %s", (name,))
        row = cur.fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Nie ma takiej subskrybcji")
        return {"items": row}



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

    return {"ok": True}
