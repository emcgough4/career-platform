"""create core schema

Revision ID: 0001_core_schema
Revises:
"""

from alembic import op
import sqlalchemy as sa


revision = "0001_core_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table("profiles",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("headline", sa.String(255), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("location", sa.String(255)),
        sa.Column("availability", sa.String(255)),
        sa.Column("email", sa.String(255)),
        sa.Column("linkedin_url", sa.String(500)),
        sa.Column("github_url", sa.String(500)),
        sa.Column("portfolio_url", sa.String(500)),
        sa.Column("photo_url", sa.String(500)),
        sa.Column("introduction_text", sa.Text()),
    )
    op.create_table("education",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("profile_id", sa.Integer(), sa.ForeignKey("profiles.id"), nullable=False),
        sa.Column("institution_name", sa.String(255), nullable=False),
        sa.Column("degree", sa.String(255), nullable=False),
        sa.Column("field_of_study", sa.String(255)),
        sa.Column("start_date", sa.Date()),
        sa.Column("end_date", sa.Date()),
        sa.Column("details", sa.Text()),
    )
    op.create_table("experiences",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("profile_id", sa.Integer(), sa.ForeignKey("profiles.id"), nullable=False),
        sa.Column("company_name", sa.String(255), nullable=False),
        sa.Column("role_title", sa.String(255), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date()),
        sa.Column("is_current", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("location", sa.String(255)),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("achievement_summary", sa.Text()),
        sa.Column("skills_used", sa.Text()),
    )
    op.create_table("skills",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("profile_id", sa.Integer(), sa.ForeignKey("profiles.id"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("category", sa.String(255)),
        sa.Column("proficiency_level", sa.String(100)),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
    )
    op.create_table("tags",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("label", sa.String(100), nullable=False, unique=True),
    )
    op.create_table("projects",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("profile_id", sa.Integer(), sa.ForeignKey("profiles.id"), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("short_description", sa.String(500), nullable=False),
        sa.Column("long_description", sa.Text(), nullable=False),
        sa.Column("challenge", sa.Text()),
        sa.Column("approach", sa.Text()),
        sa.Column("process", sa.Text()),
        sa.Column("outcome", sa.Text()),
        sa.Column("metrics", sa.Text()),
        sa.Column("status", sa.String(50), nullable=False, server_default="published"),
        sa.Column("featured", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("published_at", sa.Date()),
        sa.Column("cover_image_url", sa.String(500)),
        sa.Column("project_url", sa.String(500)),
        sa.Column("repository_url", sa.String(500)),
        sa.Column("year", sa.Integer()),
    )
    op.create_table("project_tags",
        sa.Column("project_id", sa.Integer(), sa.ForeignKey("projects.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("tag_id", sa.Integer(), sa.ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
    )


def downgrade() -> None:
    op.drop_table("project_tags")
    op.drop_table("projects")
    op.drop_table("tags")
    op.drop_table("skills")
    op.drop_table("experiences")
    op.drop_table("education")
    op.drop_table("profiles")
