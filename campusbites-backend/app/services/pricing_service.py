from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import AppError
from app.models import MenuItem
from app.schemas.cart import CartItemInput, CartValidationResult, ValidatedCartItem


def validate_cart(db: Session, items: list[CartItemInput]) -> CartValidationResult:
    """
    The single source of truth for pricing (NFR6). Never trusts a
    client-submitted price or total — always re-fetches CURRENT prices
    from the database and recomputes everything from scratch.

    Two call sites will use this:
      - POST /cart/validate (Week 4, Day 5) — pre-checkout price preview
      - Order placement (Week 5) — the actual charge, inside a transaction

    Both MUST go through this function rather than duplicating pricing
    math, so there is exactly one place a pricing bug could ever exist.
    """
    if not items:
        raise AppError(
            code="EMPTY_CART", message="Cart must contain at least one item", status_code=400
        )

    # One query for every requested item, not one query per item —
    # avoids an N+1 pattern on something that runs on every checkout.
    menu_item_ids = [i.menu_item_id for i in items]
    menu_items_by_id = {
        m.id: m for m in db.query(MenuItem).filter(MenuItem.id.in_(menu_item_ids)).all()
    }

    validated_items: list[ValidatedCartItem] = []
    subtotal = 0.0

    for cart_item in items:
        menu_item = menu_items_by_id.get(cart_item.menu_item_id)
        if menu_item is None:
            raise AppError(
                code="MENU_ITEM_NOT_FOUND",
                message=f"Menu item {cart_item.menu_item_id} not found",
                status_code=404,
            )
        if not menu_item.is_available:
            raise AppError(
                code="MENU_ITEM_UNAVAILABLE",
                message=f"'{menu_item.name}' is currently unavailable",
                status_code=400,
            )

        # menu_item.price comes back as a Decimal (it's a DECIMAL column) —
        # explicit float() here keeps all downstream arithmetic consistent
        # regardless of what type the DB driver hands back.
        line_subtotal = float(menu_item.price) * cart_item.quantity
        subtotal += line_subtotal

        validated_items.append(
            ValidatedCartItem(
                menu_item_id=menu_item.id,
                name=menu_item.name,
                price=float(menu_item.price),
                quantity=cart_item.quantity,
                line_subtotal=line_subtotal,
            )
        )

    handling_fee = settings.handling_fee
    total = subtotal + handling_fee

    return CartValidationResult(
        items=validated_items,
        subtotal=round(subtotal, 2),
        handling_fee=round(handling_fee, 2),
        total=round(total, 2),
    )