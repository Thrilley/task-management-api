"""create tasks table

Revision ID: 20260831_01
Revises:
Create Date: 2026-08-31
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "20260831_01"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create the PostgreSQL enum once.  create_type=False prevents create_table()
    # from issuing a second CREATE TYPE for the same enum.
    task_status = postgresql.ENUM(
        "todo", "in_progress", "done", name="task_status", create_type=False
    )
    task_status.create(op.get_bind(), checkfirst=True)
    op.create_table(
        "tasks",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", task_status, nullable=False, server_default="todo"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("tasks")
    sa.Enum(name="task_status").drop(op.get_bind(), checkfirst=True)
