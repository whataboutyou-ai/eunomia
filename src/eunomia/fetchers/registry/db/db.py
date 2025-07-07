from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm import DeclarativeBase, declarative_base, sessionmaker

Base: DeclarativeBase = declarative_base()
SessionLocal: sessionmaker | None = None
engine: Engine | None = None


def init_db(sql_database_url: str):
    global engine, SessionLocal

    if not sql_database_url:
        raise ValueError("sql_database_url must be provided for 'registry' fetcher")

    connect_args = {}
    if sql_database_url.startswith("sqlite"):
        connect_args = {"check_same_thread": False}

        db_url = make_url(sql_database_url)
        # For an in-memory database, db_url.database is None or ":memory:"
        if db_url.database and db_url.database != ":memory:":
            db_dir = Path(db_url.database).parent

            if not db_dir.exists():
                raise FileNotFoundError(
                    f"Directory for SQLite database does not exist: '{db_dir}'. "
                    "Please create it before starting the server."
                )
            if not db_dir.is_dir():
                raise NotADirectoryError(
                    f"Path for SQLite database directory is not a directory: '{db_dir}'"
                )

    engine = create_engine(sql_database_url, connect_args=connect_args)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)


def get_db():
    if SessionLocal is None:
        raise RuntimeError("Database not initialized. Call init_db first.")

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
