"""token_counters + unique constraint on orders.token_number

Revision ID: 004_token_counter
Revises: 003_refresh_tokens
Create Date: 2026-07-22
"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "004_token_counter"
down_revision: str | None = "003_refresh_tokens"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "token_counters",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("next_token", sa.Integer(), nullable=False),
    )

    # Seed the single global counter row, continuing from whatever tokens
    # Week 5 Day 1's naive MAX(token_number)+1 logic may have already
    # issued in your real database — never reset numbering that's already
    # been handed to real orders.
    bind = op.get_bind()
    current_max = bind.execute(sa.text("SELECT MAX(token_number) FROM orders")).scalar()
    next_token = (current_max or 0) + 1
    bind.execute(
        sa.text("INSERT INTO token_counters (id, next_token) VALUES (1, :next_token)"),
        {"next_token": next_token},
    )

    # batch_alter_table, not a plain op.create_unique_constraint: SQLite
    # (this project's test suite) can't ALTER TABLE ADD CONSTRAINT directly
    # and needs Alembic's copy-and-move "batch mode" workaround. MySQL
    # (production) supports this natively — batch mode is a transparent
    # passthrough there, so this single code path is correct on both.
    with op.batch_alter_table("orders") as batch_op:
        batch_op.create_unique_constraint("uq_orders_token_number", ["token_number"])


def downgrade() -> None:
    with op.batch_alter_table("orders") as batch_op:
        batch_op.drop_constraint("uq_orders_token_number", type_="unique")
    op.drop_table("token_counters")