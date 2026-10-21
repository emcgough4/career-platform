from datetime import date

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

import app.main
import app.routes.public
from app.db import Base
from app.main import app as fastapi_app
from app.models import Education, Profile, Project, Tag


class SwitchableSessions:
    """Stands in for SessionLocal so a test can take the database down and bring it back
    while the same app keeps running."""

    def __init__(self, healthy, broken):
        self.healthy = healthy
        self.broken = broken
        self.down = False

    def __call__(self):
        return (self.broken if self.down else self.healthy)()


def seed_profile(engine, with_project=True):
    with Session(engine) as session:
        profile = Profile(id=1, full_name="Test Person", headline="Test headline", summary="Test summary")
        session.add_all([
            profile,
            Education(profile=profile, institution_name="Test University", degree="BS",
                      end_date=date(2027, 5, 1)),
        ])
        if with_project:
            session.add(Project(profile=profile, title="Brand refresh", short_description="s",
                                long_description="l", tags=[Tag(label="Brand")]))
        session.commit()


@pytest.fixture
def database(tmp_path, monkeypatch):
    engine = create_engine(f"sqlite:///{tmp_path / 'test.db'}", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    # Nothing listens on port 1, so every query fails with a refused connection.
    broken = create_engine("postgresql+psycopg://user:pass@127.0.0.1:1/none")
    sessions = SwitchableSessions(sessionmaker(bind=engine), sessionmaker(bind=broken))
    monkeypatch.setattr(app.routes.public, "SessionLocal", sessions)
    monkeypatch.setattr(app.main, "SessionLocal", sessions)
    sessions.engine = engine
    yield sessions
    engine.dispose()
    broken.dispose()


@pytest.fixture
def client(database):
    seed_profile(database.engine)
    return TestClient(fastapi_app)


@pytest.fixture
def empty_client(database):
    seed_profile(database.engine, with_project=False)
    return TestClient(fastapi_app)
