"""
RBAC boundary tests for require_role (Week 2, Day 4's dependency).

No real staff/admin-protected endpoint exists yet — menu CRUD, the first
one, lands Week 3. So this file mounts two throwaway routes on the app
purely to exercise require_role/get_current_user in isolation. These
routes exist ONLY in the test process; they're never part of the real
running app a user or the roadmap's other endpoints touch.
"""

from fastapi import Depends

from app.core.dependencies import require_role
from app.main import app
from app.models import User, UserRole
from tests.conftest import token_for


@app.get("/api/v1/_test/admin-only")
def _admin_only_route(user: User = Depends(require_role(UserRole.admin))):
    return {"ok": True, "as": user.username}


@app.get("/api/v1/_test/staff-or-admin")
def _staff_or_admin_route(
    user: User = Depends(require_role(UserRole.staff, UserRole.admin)),
):
    return {"ok": True, "as": user.username}


# --- Authentication boundary (401): no/bad token never reaches the role check ---

def test_no_token_returns_401(client, seeded_users):
    r = client.get("/api/v1/_test/admin-only")
    assert r.status_code == 401
    assert r.json()["error"]["code"] == "NOT_AUTHENTICATED"


def test_garbage_token_returns_401(client, seeded_users):
    r = client.get("/api/v1/_test/admin-only", headers={"Authorization": "Bearer not-a-real-jwt"})
    assert r.status_code == 401
    assert r.json()["error"]["code"] == "INVALID_TOKEN"


# --- Single-role boundary (admin-only route) ---

def test_student_forbidden_from_admin_only(client, seeded_users):
    token = token_for(seeded_users["student"])
    r = client.get("/api/v1/_test/admin-only", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 403
    assert r.json()["error"]["code"] == "FORBIDDEN"


def test_staff_forbidden_from_admin_only(client, seeded_users):
    token = token_for(seeded_users["staff"])
    r = client.get("/api/v1/_test/admin-only", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 403
    assert r.json()["error"]["code"] == "FORBIDDEN"


def test_admin_allowed_on_admin_only(client, seeded_users):
    token = token_for(seeded_users["admin"])
    r = client.get("/api/v1/_test/admin-only", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert r.json() == {"ok": True, "as": "test_admin"}


# --- Multi-role boundary (staff-or-admin route) ---

def test_student_forbidden_on_multi_role_route(client, seeded_users):
    token = token_for(seeded_users["student"])
    r = client.get("/api/v1/_test/staff-or-admin", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 403


def test_staff_allowed_on_multi_role_route(client, seeded_users):
    token = token_for(seeded_users["staff"])
    r = client.get("/api/v1/_test/staff-or-admin", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert r.json()["as"] == "test_staff"


def test_admin_allowed_on_multi_role_route(client, seeded_users):
    token = token_for(seeded_users["admin"])
    r = client.get("/api/v1/_test/staff-or-admin", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert r.json()["as"] == "test_admin"