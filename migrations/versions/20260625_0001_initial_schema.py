"""initial schema

Revision ID: 20260625_0001
Revises:
Create Date: 2026-06-25 00:00:00
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "20260625_0001"
down_revision = None
branch_labels = None
depends_on = None


user_role_enum = postgresql.ENUM("ADMIN", "USER", name="userrole", create_type=False)
execution_status_enum = postgresql.ENUM(
    "PENDING",
    "RUNNING",
    "SUCCESS",
    "FAILED",
    "CANCELLED",
    name="executionstatus",
    create_type=False,
)
step_status_enum = postgresql.ENUM(
    "PENDING",
    "RUNNING",
    "SUCCESS",
    "FAILED",
    "CANCELLED",
    name="stepstatus",
    create_type=False,
)


def upgrade() -> None:
    op.execute(
        "DO $$ BEGIN CREATE TYPE userrole AS ENUM ('ADMIN', 'USER'); "
        "EXCEPTION WHEN duplicate_object THEN NULL; END $$;"
    )
    op.execute(
        "DO $$ BEGIN CREATE TYPE executionstatus AS ENUM "
        "('PENDING', 'RUNNING', 'SUCCESS', 'FAILED', 'CANCELLED'); "
        "EXCEPTION WHEN duplicate_object THEN NULL; END $$;"
    )
    op.execute(
        "DO $$ BEGIN CREATE TYPE stepstatus AS ENUM "
        "('PENDING', 'RUNNING', 'SUCCESS', 'FAILED', 'CANCELLED'); "
        "EXCEPTION WHEN duplicate_object THEN NULL; END $$;"
    )

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=True),
        sa.Column("role", user_role_enum, nullable=False, server_default="USER"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_users_id", "users", ["id"], unique=False)
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "workflows",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("definition", sa.JSON(), nullable=False),
        sa.Column("owner_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_workflows_id", "workflows", ["id"], unique=False)
    op.create_index("ix_workflows_name", "workflows", ["name"], unique=False)
    op.create_index("ix_workflows_owner_id", "workflows", ["owner_id"], unique=False)

    op.create_table(
        "executions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("workflow_id", sa.Integer(), nullable=False),
        sa.Column("initiated_by_id", sa.Integer(), nullable=False),
        sa.Column("status", execution_status_enum, nullable=False, server_default="PENDING"),
        sa.Column("current_step", sa.String(length=255), nullable=True),
        sa.Column("input_payload", sa.JSON(), nullable=True),
        sa.Column("result_payload", sa.JSON(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["workflow_id"], ["workflows.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["initiated_by_id"], ["users.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_executions_id", "executions", ["id"], unique=False)
    op.create_index("ix_executions_workflow_id", "executions", ["workflow_id"], unique=False)
    op.create_index("ix_executions_initiated_by_id", "executions", ["initiated_by_id"], unique=False)

    op.create_table(
        "execution_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("execution_id", sa.Integer(), nullable=False),
        sa.Column("step_name", sa.String(length=255), nullable=False),
        sa.Column("status", step_status_enum, nullable=False),
        sa.Column("message", sa.Text(), nullable=True),
        sa.Column("duration_ms", sa.Integer(), nullable=True),
        sa.Column("retry_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["execution_id"], ["executions.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_execution_logs_id", "execution_logs", ["id"], unique=False)
    op.create_index("ix_execution_logs_execution_id", "execution_logs", ["execution_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_execution_logs_execution_id", table_name="execution_logs")
    op.drop_index("ix_execution_logs_id", table_name="execution_logs")
    op.drop_table("execution_logs")

    op.drop_index("ix_executions_initiated_by_id", table_name="executions")
    op.drop_index("ix_executions_workflow_id", table_name="executions")
    op.drop_index("ix_executions_id", table_name="executions")
    op.drop_table("executions")

    op.drop_index("ix_workflows_owner_id", table_name="workflows")
    op.drop_index("ix_workflows_name", table_name="workflows")
    op.drop_index("ix_workflows_id", table_name="workflows")
    op.drop_table("workflows")

    op.drop_index("ix_users_email", table_name="users")
    op.drop_index("ix_users_id", table_name="users")
    op.drop_table("users")

    op.execute("DROP TYPE IF EXISTS stepstatus")
    op.execute("DROP TYPE IF EXISTS executionstatus")
    op.execute("DROP TYPE IF EXISTS userrole")
