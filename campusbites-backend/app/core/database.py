from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings

# pool_pre_ping avoids "MySQL server has gone away" errors on idle connections.
# pool_recycle prevents stale connections beyond MySQL's default wait_timeout.
engine = create_engine(settings.database_url, pool_pre_ping=True, pool_recycle=3600)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Shared declarative base — every ORM model in app/models inherits from this."""

    pass


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency. Yields one DB session per request, always closed
    afterward — even if the request raises. Use as:
        def endpoint(db: Session = Depends(get_db)): ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
