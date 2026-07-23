from sqlalchemy.orm import Session

from app.core.exceptions import AppError
from app.models import TokenCounter


def get_next_token_number(db: Session) -> int:
    """
    FR8, hardened against concurrency. Yesterday's naive approach
    (MAX(token_number)+1) has a classic race: two students checking out
    at the same instant can both read the same max BEFORE either commits,
    and both get handed the same token number.

    with_for_update() emits SELECT ... FOR UPDATE, which under MySQL/InnoDB
    (the real production DB) takes a row lock on the single counter row.
    A second concurrent transaction calling this function blocks until the
    first one commits or rolls back, then reads the up-to-date value —
    genuinely serializing token issuance rather than racing on it.

    Honest limitation: this project's test suite runs against in-memory
    SQLite (see tests/conftest.py), and SQLite has no SELECT ... FOR UPDATE
    concept at all — SQLAlchemy's SQLite dialect silently no-ops this call.
    So this file's tests can only prove sequential correctness (never
    repeats, increments correctly, survives rollback safely); they cannot
    prove the concurrent-locking guarantee itself. That guarantee rests on
    MySQL/InnoDB's documented row-locking behavior under FOR UPDATE, not on
    anything provable in this sandboxed test environment.

    If a transaction calling this later fails and rolls back before its
    own db.commit(), the increment made here rolls back with it — the
    "reserved" number becomes available again for the next caller. Safe,
    because nothing is ever visible to other transactions until commit.
    """
    counter = db.query(TokenCounter).filter(TokenCounter.id == 1).with_for_update().first()
    if counter is None:
        # Should be impossible if migration 004 ran — fail loudly rather
        # than silently falling back to something that could collide.
        raise AppError(
            code="TOKEN_COUNTER_MISSING",
            message="Token counter not initialized",
            status_code=500,
        )

    token = counter.next_token
    counter.next_token += 1
    return token