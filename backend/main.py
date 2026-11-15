from fastapi import Depends, FastAPI
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from db import get_db
from users import router as users_router
from sub_types import router as types_router
from subs import router as subs_router


app = FastAPI()

app.include_router(users_router)
app.include_router(types_router)
app.include_router(subs_router)

@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
    except SQLAlchemyError as e:
        print(f"Health check failed: {e}")
        return JSONResponse(status_code=503, content={"status": "down"})

    return {"status": "up"}
