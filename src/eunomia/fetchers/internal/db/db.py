from sqlalchemy import create_engine
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm import DeclarativeBase, declarative_base, sessionmaker

Base: DeclarativeBase = declarative_base()
SessionLocal: sessionmaker | None = None
engine: Engine | None = None


def init_db(sql_database_url: str):
    global engine, SessionLocal

    if not sql_database_url:
        raise ValueError("SQL_DATABASE_URL must be provided for 'internal' fetcher")

    engine = create_engine(
        sql_database_url,
        connect_args=(
            {"check_same_thread": False}
            if sql_database_url.startswith("sqlite")
            else {}
        ),
    )
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
