from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from eunomia.config import settings

# Default to the environment variable for local development (can be SQLite or PostgreSQL)
SQLALCHEMY_DATABASE_URL = settings.LOCAL_DB_HOST

if not SQLALCHEMY_DATABASE_URL:
    raise ValueError(
        "No DATABASE_URL environment variable set and no default provided."
    )

if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
    )
else:
    engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def init_db():
    # Initialize the database (create tables if they don't exist)
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
