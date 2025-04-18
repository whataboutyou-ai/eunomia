from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from eunomia.config import settings

database_url = settings.FETCHERS["internal"]["SQL_DATABASE_URL"]
if not database_url:
    raise ValueError("Environment variable INTERNAL__SQL_DATABASE_URL must be provided")

engine = create_engine(
    database_url,
    connect_args=(
        {"check_same_thread": False} if database_url.startswith("sqlite") else {}
    ),
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def init_db():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
