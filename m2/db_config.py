import os
from sqlalchemy import create_engine
import sqlite3

DB_TYPE = os.getenv("DB_TYPE", "sqlite")

if DB_TYPE == "sqlite":
    DB_PATH = "supermarket.db"
    CONNECTION_STRING = f"sqlite:///{DB_PATH}"
else:
    DB_HOST = os.getenv("PGHOST", "localhost")
    DB_NAME = os.getenv("PGDATABASE", "mart_db")
    DB_USER = os.getenv("PGUSER", "postgres")
    DB_PASS = os.getenv("PGPASSWORD", "Deepak@7060")
    DB_PORT = os.getenv("PGPORT", "5432")
    CONNECTION_STRING = f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


def get_sqlite_connection():
    try:
        conn = sqlite3.connect(DB_PATH)
        return conn
    except Exception as e:
        print(f"Error connecting to SQLite: {e}")
        return None


def get_connection_string():
    return CONNECTION_STRING


def get_engine():
    try:
        engine = create_engine(get_connection_string(), echo=False)
        return engine
    except Exception as e:
        print(f"Error creating SQLAlchemy engine: {e}")
        return None
