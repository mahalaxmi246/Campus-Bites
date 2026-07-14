from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DECIMAL, Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.canteen import Canteen


class MenuItem(Base):
    __tablename__ = "menu_items"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    canteen_id: Mapped[int] = mapped_column(ForeignKey("canteens.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    price: Mapped[float] = mapped_column(DECIMAL(10, 2), nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    is_available: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)

    canteen: Mapped["Canteen"] = relationship(back_populates="menu_items")