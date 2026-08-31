"""add users and task owners

Revision ID: 20260831_02
Revises: 20260831_01
Create Date: 2026-08-31
"""

import sqlalchemy as sa
from alembic import op

revision = "20260831_02"
down_revision = "20260831_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("email"),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=False)
    op.add_column("tasks", sa.Column("user_id", sa.Integer(), nullable=True))
    op.create_index("ix_tasks_user_id", "tasks", ["user_id"], unique=False)
    op.create_foreign_key("fk_tasks_user_id", "tasks", "users", ["user_id"], ["id"], ondelete="CASCADE")


def downgrade() -> None:
    op.drop_constraint("fk_tasks_user_id", "tasks", type_="foreignkey")
    op.drop_index("ix_tasks_user_id", table_name="tasks")
    op.drop_column("tasks", "user_id")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
