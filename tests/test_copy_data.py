from datetime import date

import pytest
from sqlalchemy import create_engine, func, select, text
from sqlalchemy.orm import Session

from app.copy_data import copy_database
from app.db import Base
from app.models import Experience, Profile, Project, Tag


def make_db(path, version="0002_project_category"):
    url = f"sqlite:///{path}"
    engine = create_engine(url)
    Base.metadata.create_all(engine)
    with engine.begin() as conn:
        conn.execute(text("CREATE TABLE alembic_version (version_num VARCHAR(32) NOT NULL)"))
        conn.execute(text("INSERT INTO alembic_version VALUES (:v)"), {"v": version})
    engine.dispose()
    return url


def seed(url):
    engine = create_engine(url)
    with Session(engine) as session:
        profile = Profile(id=1, full_name="Eleanor McGough", headline="h", summary="s")
        session.add_all([
            profile,
            Experience(profile=profile, company_name="Co", role_title="Designer",
                       start_date=date(2024, 1, 1), is_current=True, description="d"),
            Project(profile=profile, title="Brand refresh", short_description="s",
                    long_description="l", featured=True, tags=[Tag(label="Brand")]),
        ])
        session.commit()
    engine.dispose()


def test_copies_every_row_with_types_intact(tmp_path):
    source = make_db(tmp_path / "source.db")
    target = make_db(tmp_path / "target.db")
    seed(source)

    counts = copy_database(source, target)

    assert counts == {"profiles": 1, "tags": 1, "education": 0, "experiences": 1,
                      "projects": 1, "skills": 0, "project_tags": 1}
    with Session(create_engine(target)) as session:
        experience = session.scalars(select(Experience)).one()
        assert experience.is_current is True
        assert experience.start_date == date(2024, 1, 1)
        project = session.scalars(select(Project)).one()
        assert project.featured is True
        assert [tag.label for tag in project.tags] == ["Brand"]


def test_refuses_a_target_that_already_has_rows(tmp_path):
    source = make_db(tmp_path / "source.db")
    target = make_db(tmp_path / "target.db")
    seed(source)
    seed(target)

    with pytest.raises(ValueError, match="already has rows"):
        copy_database(source, target)

    with create_engine(target).connect() as conn:
        assert conn.scalar(select(func.count()).select_from(Base.metadata.tables["projects"])) == 1


def test_refuses_a_target_on_another_migration(tmp_path):
    source = make_db(tmp_path / "source.db")
    target = make_db(tmp_path / "target.db", version="0001_core_schema")
    seed(source)

    with pytest.raises(ValueError, match="revision"):
        copy_database(source, target)
