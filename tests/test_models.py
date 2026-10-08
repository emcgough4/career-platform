from app.models import Education, Experience, Profile, Project, Skill, Tag


def test_core_models_are_registered():
    assert {Profile, Experience, Education, Skill, Project, Tag}


def test_project_supports_tags():
    assert "tags" in Project.__mapper__.relationships


def test_project_tags_have_a_fixed_order():
    # Postgres returns association rows in no set order; SQLite happened to sort them by tag id.
    order_by = Project.tags.property.order_by
    assert order_by and [str(column) for column in order_by] == ["tags.id"]
