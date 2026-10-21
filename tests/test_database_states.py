from app.services.fallback_service import load_latest_snapshot

UNAVAILABLE = "Projects temporarily unavailable"


def test_healthy_request_reads_projects_from_the_database(client):
    response = client.get("/portfolio")
    assert response.status_code == 200
    assert "Brand refresh" in response.text
    assert UNAVAILABLE not in response.text


def test_empty_projects_table_shows_the_empty_state(empty_client):
    response = empty_client.get("/portfolio")
    assert response.status_code == 200
    assert "No case studies are published yet." in response.text


def test_database_failure_keeps_the_profile_and_returns_503(client, database):
    database.down = True
    response = client.get("/about")
    assert response.status_code == 503
    assert load_latest_snapshot()["profile"]["full_name"] in response.text
    assert UNAVAILABLE in response.text


def test_database_failure_shows_no_substitute_projects(client, database):
    database.down = True
    for route in ("/portfolio", "/projects/1"):
        response = client.get(route)
        assert response.status_code == 503
        assert UNAVAILABLE in response.text
        assert "work-grid" not in response.text and "data-reel" not in response.text


def test_every_database_page_returns_503_while_the_database_is_down(client, database):
    database.down = True
    for route in ("/resume", "/contact", "/privacy"):
        assert client.get(route).status_code == 503


def test_projects_return_after_the_database_recovers_without_a_restart(client, database):
    database.down = True
    assert client.get("/portfolio").status_code == 503
    database.down = False
    response = client.get("/portfolio")
    assert response.status_code == 200
    assert "Brand refresh" in response.text
