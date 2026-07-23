from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class TokenCounter(Base):
    """
    Exactly one row ever exists here (id=1), seeded by its migration. This
    is Phase 1's GLOBAL token counter — per docs/erd-notes.md, per-canteen-
    per-day scoping is explicitly deferred to Phase 3. When that lands,
    this table gets redesigned (composite key canteen_id+date), not just
    extended — don't assume today's shape survives unchanged.
    """

    __tablename__ = "token_counters"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    next_token: Mapped[int] = mapped_column(nullable=False, default=1)