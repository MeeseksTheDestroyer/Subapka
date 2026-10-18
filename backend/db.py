import os

import pymysql
from pymysql.cursors import DictCursor


def get_db():
    conn = pymysql.connect(
        host=os.environ["DB_HOST"],
        port=int(os.environ.get("DB_PORT", "3306")),
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        database=os.environ["DB_NAME"],
        charset="utf8mb4",
        cursorclass=DictCursor,
    )
    try:
        yield conn
    except Exception as err:
        print(f"Error: {err}")
        raise
    finally:
        conn.close()
