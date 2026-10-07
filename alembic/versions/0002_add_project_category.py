"""add project category

Revision ID: 0002_project_category
Revises: 0001_core_schema
"""

from alembic import op
import sqlalchemy as sa


revision = "0002_project_category"
down_revision = "0001_core_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("projects", sa.Column("category", sa.String(100)))


def downgrade() -> None:
    with op.batch_alter_table("projects") as batch:
        batch.drop_column("category")
