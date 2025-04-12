from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from eunomia.config import settings

engine = create_engine(
    settings.INTERNAL_SQL_DATABASE_URL,
    connect_args=(
        {"check_same_thread": False}
        if settings.INTERNAL_SQL_DATABASE_URL.startswith("sqlite")
        else {}
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
