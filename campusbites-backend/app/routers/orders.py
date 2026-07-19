from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models import User
from app.schemas.order import OrderCreateRequest, OrderResponse
from app.services.order_service import place_order

router = APIRouter()


@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(
    data: OrderCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> OrderResponse:
    """
    Any authenticated role can place an order, not just students — staff
    and admins are real people who might also want lunch, and gating this
    to students only would be an artificial restriction with no actual
    security or business reason behind it.
    """
    return place_order(db, current_user, data.canteen_id, data.items)