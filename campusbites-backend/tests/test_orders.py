"""
Order placement tests — transactional rollback safety (FR7/NFR3) and
token uniqueness under the hardened generator (FR8, Week 5 Day 2).
"""

from unittest.mock import patch

import pytest

from app.core.exceptions import AppError
from app.models import Order, OrderItem, TokenCounter
from app.schemas.cart import CartItemInput
from app.services.order_service import place_order
from tests.conftest import token_for


# --- Happy path ---

def test_place_order_success(client, db_session, seeded_users, seeded_canteen, seeded_menu_items, seeded_token_counter):
    token = token_for(seeded_users["student"])
    r = client.post(
        "/api/v1/orders",
        json={
            "canteen_id": seeded_canteen.id,
            "items": [
                {"menu_item_id": seeded_menu_items["fries"].id, "quantity": 2},
                {"menu_item_id": seeded_menu_items["thali"].id, "quantity": 1},
            ],
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 201
    body = r.json()
    assert body["status"] == "placed"
    assert body["subtotal"] == 30 * 2 + 80  # fries x2 + thali x1
    assert body["token_number"] == 1
    assert len(body["items"]) == 2

    assert db_session.query(Order).count() == 1
    assert db_session.query(OrderItem).count() == 2


def test_place_order_no_auth(client, seeded_canteen, seeded_menu_items, seeded_token_counter):
    r = client.post(
        "/api/v1/orders",
        json={"canteen_id": seeded_canteen.id, "items": [{"menu_item_id": seeded_menu_items["fries"].id, "quantity": 1}]},
    )
    assert r.status_code == 401


# --- Transactional rollback (NFR3): failure must leave ZERO rows behind ---

def test_nonexistent_canteen_writes_nothing(client, db_session, seeded_users, seeded_menu_items, seeded_token_counter):
    token = token_for(seeded_users["student"])
    r = client.post(
        "/api/v1/orders",
        json={"canteen_id": 9999, "items": [{"menu_item_id": seeded_menu_items["fries"].id, "quantity": 1}]},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 404
    assert r.json()["error"]["code"] == "CANTEEN_NOT_FOUND"
    assert db_session.query(Order).count() == 0
    assert db_session.query(OrderItem).count() == 0


def test_unavailable_item_writes_nothing(client, db_session, seeded_users, seeded_canteen, seeded_menu_items, seeded_token_counter):
    token = token_for(seeded_users["student"])
    r = client.post(
        "/api/v1/orders",
        json={"canteen_id": seeded_canteen.id, "items": [{"menu_item_id": seeded_menu_items["discontinued"].id, "quantity": 1}]},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 400
    assert r.json()["error"]["code"] == "MENU_ITEM_UNAVAILABLE"
    assert db_session.query(Order).count() == 0
    assert db_session.query(OrderItem).count() == 0


def test_mixed_valid_and_invalid_cart_rejects_entirely(
    client, db_session, seeded_users, seeded_canteen, seeded_menu_items, seeded_token_counter
):
    """The strongest proof of NFR3: one valid item + one unavailable item
    in the same cart must reject the WHOLE order — the valid item must
    NOT partially go through on its own."""
    token = token_for(seeded_users["student"])
    r = client.post(
        "/api/v1/orders",
        json={
            "canteen_id": seeded_canteen.id,
            "items": [
                {"menu_item_id": seeded_menu_items["fries"].id, "quantity": 1},  # valid
                {"menu_item_id": seeded_menu_items["discontinued"].id, "quantity": 1},  # invalid
            ],
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 400
    assert db_session.query(Order).count() == 0
    assert db_session.query(OrderItem).count() == 0


def test_failure_after_token_reservation_still_rolls_back_completely(
    db_session, seeded_users, seeded_canteen, seeded_menu_items, seeded_token_counter
):
    """
    Every other rollback test triggers its failure BEFORE a token is ever
    reserved (bad canteen / bad item both fail inside validate_cart, which
    runs before get_next_token_number). This test closes that gap: it
    forces a failure DURING order_item construction — AFTER a token has
    already been reserved — and proves the token reservation itself rolls
    back too, not just the order/order_items rows. Calls place_order
    directly (not via HTTP) since we need to inject the failure precisely.
    """
    student = seeded_users["student"]
    items = [
        CartItemInput(menu_item_id=seeded_menu_items["fries"].id, quantity=1),
        CartItemInput(menu_item_id=seeded_menu_items["thali"].id, quantity=1),
    ]

    with patch(
        "app.services.order_service.OrderItem", side_effect=RuntimeError("simulated mid-order failure")
    ):
        with pytest.raises(RuntimeError):
            place_order(db_session, student, seeded_canteen.id, items)

    # The session still holds whatever place_order left pending — since it
    # never reached db.commit(), rolling back here simulates exactly what
    # get_db's `finally: db.close()` does on a real request.
    db_session.rollback()

    assert db_session.query(Order).count() == 0
    assert db_session.query(OrderItem).count() == 0

    counter = db_session.query(TokenCounter).filter(TokenCounter.id == 1).first()
    assert counter.next_token == 1  # the reserved token was NOT burned


# --- Token uniqueness (FR8) ---

def test_sequential_orders_get_sequential_unique_tokens(
    client, seeded_users, seeded_canteen, seeded_menu_items, seeded_token_counter
):
    token = token_for(seeded_users["student"])
    headers = {"Authorization": f"Bearer {token}"}
    issued = []
    for _ in range(5):
        r = client.post(
            "/api/v1/orders",
            json={"canteen_id": seeded_canteen.id, "items": [{"menu_item_id": seeded_menu_items["fries"].id, "quantity": 1}]},
            headers=headers,
        )
        assert r.status_code == 201
        issued.append(r.json()["token_number"])

    assert issued == [1, 2, 3, 4, 5]
    assert len(set(issued)) == 5  # all unique, no duplicates


def test_token_number_unique_constraint_enforced_at_db_level(db_session, seeded_users, seeded_canteen):
    """
    Defense in depth: even if application logic somehow tried to reuse a
    token number, the database itself refuses it (migration 004's unique
    constraint, mirrored in the ORM model via unique=True).
    """
    student = seeded_users["student"]
    order1 = Order(
        user_id=student.id, canteen_id=seeded_canteen.id, token_number=1,
        subtotal=10, handling_fee=5, total_amount=15,
    )
    db_session.add(order1)
    db_session.commit()

    order2 = Order(
        user_id=student.id, canteen_id=seeded_canteen.id, token_number=1,  # duplicate on purpose
        subtotal=20, handling_fee=5, total_amount=25,
    )
    db_session.add(order2)
    with pytest.raises(Exception):  # SQLAlchemy raises IntegrityError
        db_session.commit()
    db_session.rollback()


def test_missing_token_counter_fails_cleanly(db_session, seeded_users, seeded_canteen, seeded_menu_items):
    """No seeded_token_counter fixture here on purpose — proves the
    TOKEN_COUNTER_MISSING guard (Week 5 Day 2) actually fires rather than
    silently producing a wrong/duplicate value."""
    student = seeded_users["student"]
    items = [CartItemInput(menu_item_id=seeded_menu_items["fries"].id, quantity=1)]

    with pytest.raises(AppError) as exc_info:
        place_order(db_session, student, seeded_canteen.id, items)

    assert exc_info.value.code == "TOKEN_COUNTER_MISSING"