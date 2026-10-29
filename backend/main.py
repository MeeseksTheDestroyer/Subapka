from fastapi import Depends, FastAPI
from db import get_db
from users import router as users_router
from sub_types import router as types_router
from subs import router as subs_router

app = FastAPI()

app.include_router(users_router)
app.include_router(types_router)
app.include_router(subs_router)

@app.get("/health")
def health_check():
    return {"status": "up"}
