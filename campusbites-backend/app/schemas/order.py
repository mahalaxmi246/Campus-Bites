from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models import OrderStatus
from app.schemas.cart import CartItemInput


class OrderCreateRequest(BaseModel):
    canteen_id: int
    items: list[CartItemInput]


class OrderItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    menu_item_id: int
    item_name_snapshot: str
    price_snapshot: float
    quantity: int
    subtotal: float


class OrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    token_number: int
    status: OrderStatus
    subtotal: float
    handling_fee: float
    total_amount: float
    created_at: datetime
    items: list[OrderItemResponse] = []