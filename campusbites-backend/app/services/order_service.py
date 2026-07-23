from sqlalchemy.orm import Session

from app.core.exceptions import AppError
from app.models import Canteen, Order, OrderItem, OrderStatus, User
from app.schemas.cart import CartItemInput
from app.services.pricing_service import validate_cart
from app.services.token_service import get_next_token_number


def place_order(
    db: Session, user: User, canteen_id: int, items: list[CartItemInput]
) -> Order:
    """
    FR7 / NFR3 — the whole point of this function is that it is
    all-or-nothing. Nothing is written to the database until the single
    db.commit() at the very end. If ANYTHING fails before that point —
    a bad canteen_id, an unavailable item, a DB error while building
    order_items — every db.add() made so far is simply discarded when the
    session is torn down (see app.core.database.get_db's `finally: db.close()`).
    There is no code path that can leave a half-written order behind.

    Reuses validate_cart (Week 3 Day 3 / Week 4 Day 5) completely unchanged
    — this IS the actual charge, not a preview, but the pricing logic is
    identical on purpose (NFR6: exactly one place pricing math can be wrong).
    """
    canteen = db.query(Canteen).filter(Canteen.id == canteen_id).first()
    if canteen is None:
        raise AppError(
            code="CANTEEN_NOT_FOUND", message="Canteen does not exist", status_code=404
        )

    validated = validate_cart(db, items)
    token_number = get_next_token_number(db)

    order = Order(
        user_id=user.id,
        canteen_id=canteen_id,
        token_number=token_number,
        status=OrderStatus.placed,
        subtotal=validated.subtotal,
        handling_fee=validated.handling_fee,
        total_amount=validated.total,
    )
    db.add(order)
    db.flush()  # assigns order.id, without committing — still fully rollback-able

    for validated_item in validated.items:
        db.add(
            OrderItem(
                order_id=order.id,
                menu_item_id=validated_item.menu_item_id,
                item_name_snapshot=validated_item.name,
                price_snapshot=validated_item.price,
                quantity=validated_item.quantity,
                subtotal=validated_item.line_subtotal,
            )
        )

    db.commit()
    db.refresh(order)
    return order