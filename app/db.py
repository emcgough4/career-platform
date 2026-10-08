from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import settings


is_sqlite = settings.database_url.startswith("sqlite")
connect_args = {"check_same_thread": False} if is_sqlite else {}
# pool_pre_ping swaps out Postgres connections the server closed while they sat idle.
engine = create_engine(settings.database_url, connect_args=connect_args, pool_pre_ping=not is_sqlite, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
Base = declarative_base()
