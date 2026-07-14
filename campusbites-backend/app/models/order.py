import enum
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DECIMAL, Enum, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.canteen import Canteen
    from app.models.order_item import OrderItem
    from app.models.user import User


class OrderStatus(str, enum.Enum):
    placed = "placed"
    preparing = "preparing"
    ready = "ready"
    # Cancelled/Refunded/PickedUp/Accepted are added in Phase 3 (FR20) —
    # don't add them early, they need real transition-rule logic alongside.


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    canteen_id: Mapped[int] = mapped_column(ForeignKey("canteens.id"), nullable=False, index=True)
    token_number: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[OrderStatus] = mapped_column(
        Enum(OrderStatus, native_enum=False, length=20),
        default=OrderStatus.placed,
        nullable=False,
        index=True,
    )
    subtotal: Mapped[float] = mapped_column(DECIMAL(10, 2), nullable=False)
    handling_fee: Mapped[float] = mapped_column(DECIMAL(10, 2), nullable=False, default=0)
    total_amount: Mapped[float] = mapped_column(DECIMAL(10, 2), nullable=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)

    user: Mapped["User"] = relationship(back_populates="orders")
    canteen: Mapped["Canteen"] = relationship(back_populates="orders")
    items: Mapped[list["OrderItem"]] = relationship(
        back_populates="order", cascade="all, delete-orphan"
    )