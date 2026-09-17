from datetime import date

from sqlalchemy import Boolean, Date, ForeignKey, Integer, String, Table, Text, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


project_tags = Table(
    "project_tags",
    Base.metadata,
    Column("project_id", ForeignKey("projects.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)


class Profile(Base):
    __tablename__ = "profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    headline: Mapped[str] = mapped_column(String(255), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    location: Mapped[str | None] = mapped_column(String(255))
    availability: Mapped[str | None] = mapped_column(String(255))
    email: Mapped[str | None] = mapped_column(String(255))
    linkedin_url: Mapped[str | None] = mapped_column(String(500))
    github_url: Mapped[str | None] = mapped_column(String(500))
    portfolio_url: Mapped[str | None] = mapped_column(String(500))
    photo_url: Mapped[str | None] = mapped_column(String(500))
    introduction_text: Mapped[str | None] = mapped_column(Text)

    experiences: Mapped[list["Experience"]] = relationship(back_populates="profile")
    education: Mapped[list["Education"]] = relationship(back_populates="profile")
    skills: Mapped[list["Skill"]] = relationship(back_populates="profile")
    projects: Mapped[list["Project"]] = relationship(back_populates="profile")


class Experience(Base):
    __tablename__ = "experiences"

    id: Mapped[int] = mapped_column(primary_key=True)
    profile_id: Mapped[int] = mapped_column(ForeignKey("profiles.id"), nullable=False)
    company_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role_title: Mapped[str] = mapped_column(String(255), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date | None] = mapped_column(Date)
    is_current: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    location: Mapped[str | None] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text, nullable=False)
    achievement_summary: Mapped[str | None] = mapped_column(Text)
    skills_used: Mapped[str | None] = mapped_column(Text)
    profile: Mapped[Profile] = relationship(back_populates="experiences")


class Education(Base):
    __tablename__ = "education"

    id: Mapped[int] = mapped_column(primary_key=True)
    profile_id: Mapped[int] = mapped_column(ForeignKey("profiles.id"), nullable=False)
    institution_name: Mapped[str] = mapped_column(String(255), nullable=False)
    degree: Mapped[str] = mapped_column(String(255), nullable=False)
    field_of_study: Mapped[str | None] = mapped_column(String(255))
    start_date: Mapped[date | None] = mapped_column(Date)
    end_date: Mapped[date | None] = mapped_column(Date)
    details: Mapped[str | None] = mapped_column(Text)
    profile: Mapped[Profile] = relationship(back_populates="education")


class Skill(Base):
    __tablename__ = "skills"

    id: Mapped[int] = mapped_column(primary_key=True)
    profile_id: Mapped[int] = mapped_column(ForeignKey("profiles.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str | None] = mapped_column(String(255))
    proficiency_level: Mapped[str | None] = mapped_column(String(100))
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    profile: Mapped[Profile] = relationship(back_populates="skills")


class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(primary_key=True)
    label: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    projects: Mapped[list["Project"]] = relationship(secondary=project_tags, back_populates="tags")


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(primary_key=True)
    profile_id: Mapped[int] = mapped_column(ForeignKey("profiles.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    short_description: Mapped[str] = mapped_column(String(500), nullable=False)
    long_description: Mapped[str] = mapped_column(Text, nullable=False)
    challenge: Mapped[str | None] = mapped_column(Text)
    approach: Mapped[str | None] = mapped_column(Text)
    process: Mapped[str | None] = mapped_column(Text)
    outcome: Mapped[str | None] = mapped_column(Text)
    metrics: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(50), default="published", nullable=False)
    featured: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    published_at: Mapped[date | None] = mapped_column(Date)
    cover_image_url: Mapped[str | None] = mapped_column(String(500))
    project_url: Mapped[str | None] = mapped_column(String(500))
    repository_url: Mapped[str | None] = mapped_column(String(500))
    year: Mapped[int | None] = mapped_column(Integer)
    profile: Mapped[Profile] = relationship(back_populates="projects")
    tags: Mapped[list[Tag]] = relationship(secondary=project_tags, back_populates="projects")
