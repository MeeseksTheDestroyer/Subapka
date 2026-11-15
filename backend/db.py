import os

from sqlalchemy import URL, create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = URL.create(
    "mysql+pymysql",
    username=os.environ["DB_USER"],
    password=os.environ["DB_PASSWORD"],
    host=os.environ["DB_HOST"],
    port=int(os.environ.get("DB_PORT", "3306")),
    database=os.environ["DB_NAME"],
    query={"charset": "utf8mb4"},
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine)


def get_db():
    with SessionLocal() as session:
        yield session
