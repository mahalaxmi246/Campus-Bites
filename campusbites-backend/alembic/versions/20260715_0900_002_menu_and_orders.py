"""menu_items, orders, order_items

Revision ID: 002_menu_and_orders
Revises: 001_users_and_canteens
Create Date: 2026-07-15
"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "002_menu_and_orders"
down_revision: str | None = "001_users_and_canteens"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "menu_items",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("canteen_id", sa.Integer(), sa.ForeignKey("canteens.id"), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.String(length=255), nullable=True),
        sa.Column("price", sa.DECIMAL(precision=10, scale=2), nullable=False),
        sa.Column("category", sa.String(length=50), nullable=False),
        sa.Column("is_available", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_menu_items_canteen_id", "menu_items", ["canteen_id"])
    op.create_index("ix_menu_items_category", "menu_items", ["category"])

    op.create_table(
        "orders",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("canteen_id", sa.Integer(), sa.ForeignKey("canteens.id"), nullable=False),
        sa.Column("token_number", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="placed"),
        sa.Column("subtotal", sa.DECIMAL(precision=10, scale=2), nullable=False),
        sa.Column("handling_fee", sa.DECIMAL(precision=10, scale=2), nullable=False, server_default="0"),
        sa.Column("total_amount", sa.DECIMAL(precision=10, scale=2), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_orders_user_id", "orders", ["user_id"])
    op.create_index("ix_orders_canteen_id", "orders", ["canteen_id"])
    op.create_index("ix_orders_status", "orders", ["status"])

    op.create_table(
        "order_items",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("order_id", sa.Integer(), sa.ForeignKey("orders.id"), nullable=False),
        sa.Column("menu_item_id", sa.Integer(), sa.ForeignKey("menu_items.id"), nullable=False),
        sa.Column("item_name_snapshot", sa.String(length=100), nullable=False),
        sa.Column("price_snapshot", sa.DECIMAL(precision=10, scale=2), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("subtotal", sa.DECIMAL(precision=10, scale=2), nullable=False),
    )
    op.create_index("ix_order_items_order_id", "order_items", ["order_id"])


def downgrade() -> None:
    op.drop_index("ix_order_items_order_id", table_name="order_items")
    op.drop_table("order_items")

    op.drop_index("ix_orders_status", table_name="orders")
    op.drop_index("ix_orders_canteen_id", table_name="orders")
    op.drop_index("ix_orders_user_id", table_name="orders")
    op.drop_table("orders")

    op.drop_index("ix_menu_items_category", table_name="menu_items")
    op.drop_index("ix_menu_items_canteen_id", table_name="menu_items")
    op.drop_table("menu_items")