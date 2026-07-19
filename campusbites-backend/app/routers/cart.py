from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models import User
from app.schemas.cart import CartValidationRequest, CartValidationResult
from app.services.pricing_service import validate_cart

router = APIRouter()


@router.post("/validate", response_model=CartValidationResult)
def validate_cart_route(
    data: CartValidationRequest,
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> CartValidationResult:
    """
    NFR6 — the frontend's local cart math (Week 4, Days 1-4) is a UX
    convenience only. This is the moment that math gets replaced with
    server-verified truth: current prices, current availability, correct
    handling fee. Called right before the checkout page shows a final
    total (Week 5), and reused unchanged inside order placement itself
    so there is exactly one place pricing logic can ever go wrong.

    Requires login (matches CheckoutPage.tsx already redirecting
    unauthenticated users to /login) — there's no reason to expose this
    to anonymous callers, and gating it costs nothing since checkout
    already requires auth downstream anyway.
    """
    return validate_cart(db, data.items)