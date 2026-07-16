import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.core.security import create_access_token, hash_password
from app.main import app
from app.models import Canteen, MenuItem, User, UserRole


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
            full_name="Test Student", username="test_student", email="test_student@gmail.com",
            password_hash=hash_password("Pass@123"), role=UserRole.student,
        ),
        "staff": User(
            full_name="Test Staff", username="test_staff", email="test_staff@gmail.com",
            password_hash=hash_password("Pass@123"), role=UserRole.staff,
        ),
        "admin": User(
            full_name="Test Admin", username="test_admin", email="test_admin@gmail.com",
            password_hash=hash_password("Pass@123"), role=UserRole.admin,
        ),
    }
    db_session.add_all(users.values())
    db_session.commit()
    for user in users.values():
        db_session.refresh(user)
    return users


@pytest.fixture()
def seeded_canteen(db_session) -> Canteen:
    canteen = Canteen(name="Main Canteen", location="Block A")
    db_session.add(canteen)
    db_session.commit()
    db_session.refresh(canteen)
    return canteen


@pytest.fixture()
def seeded_menu_items(db_session, seeded_canteen) -> dict[str, MenuItem]:
    """A small menu, including one already-unavailable (86'd) item —
    needed to test the browse endpoint's default filtering behavior."""
    items = {
        "fries": MenuItem(
            canteen_id=seeded_canteen.id, name="French Fries", price=30, category="snacks"
        ),
        "thali": MenuItem(
            canteen_id=seeded_canteen.id, name="Veg Thali", price=80, category="meals"
        ),
        "tea": MenuItem(canteen_id=seeded_canteen.id, name="Tea", price=10, category="drinks"),
        "discontinued": MenuItem(
            canteen_id=seeded_canteen.id, name="Discontinued Item", price=99,
            category="snacks", is_available=False,
        ),
    }
    db_session.add_all(items.values())
    db_session.commit()
    for item in items.values():
        db_session.refresh(item)
    return items


def token_for(user: User) -> str:
    """Shared helper — generates a valid access token for a seeded user
    directly (no need to hit /auth/login in every test that just needs
    an authenticated request)."""
    return create_access_token(
        subject=str(user.id),
        extra_claims={"role": user.role.value, "username": user.username},
    )