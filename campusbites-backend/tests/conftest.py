import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.core.security import hash_password
from app.main import app
from app.models import User, UserRole


@pytest.fixture()
def db_session():
    """
    Fresh in-memory SQLite DB per test — fully isolated, no leftover state
    between tests. StaticPool is required for SQLite ':memory:' so every
    connection in this test shares the same actual database (by default
    each new connection gets its own empty in-memory DB, which would break
    anything using more than one connection per test).
    """
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def client(db_session):
    """TestClient wired to the real app, but with get_db swapped for the
    isolated test DB session above — so every route we test hits SQLite,
    never your real MySQL."""

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture()
def seeded_users(db_session) -> dict[str, User]:
    """One user per role, for RBAC boundary testing."""
    users = {
        "student": User(
            full_name="RBAC Student", username="rbac_student", email="rbac_student@gmail.com",
            password_hash=hash_password("Pass@123"), role=UserRole.student,
        ),
        "staff": User(
            full_name="RBAC Staff", username="rbac_staff", email="rbac_staff@gmail.com",
            password_hash=hash_password("Pass@123"), role=UserRole.staff,
        ),
        "admin": User(
            full_name="RBAC Admin", username="rbac_admin", email="rbac_admin@gmail.com",
            password_hash=hash_password("Pass@123"), role=UserRole.admin,
        ),
    }
    db_session.add_all(users.values())
    db_session.commit()
    for user in users.values():
        db_session.refresh(user)
    return users