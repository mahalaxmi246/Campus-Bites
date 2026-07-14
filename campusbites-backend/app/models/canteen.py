from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.menu_item import MenuItem
    from app.models.order import Order


class Canteen(Base):
    __tablename__ = "canteens"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    location: Mapped[str | None] = mapped_column(String(150), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)

    menu_items: Mapped[list["MenuItem"]] = relationship(back_populates="canteen")
    orders: Mapped[list["Order"]] = relationship(back_populates="canteen")