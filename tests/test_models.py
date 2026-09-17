from app.models import Education, Experience, Profile, Project, Skill, Tag


def test_core_models_are_registered():
    assert {Profile, Experience, Education, Skill, Project, Tag}


def test_project_supports_tags():
    assert "tags" in Project.__mapper__.relationships
