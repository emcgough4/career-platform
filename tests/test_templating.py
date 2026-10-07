from datetime import date

from app.templating import month_year, sentences


def test_month_year_formats_dates_and_iso_strings():
    assert month_year(date(2026, 1, 1)) == "Jan 2026"
    assert month_year("2024-09-15") == "Sep 2024"
    assert month_year(None) == ""


def test_sentences_splits_description_into_points():
    text = "Lead a team (Instagram, TikTok). Host “What’s Up Wednesdays.” Edit video."
    assert sentences(text) == ["Lead a team (Instagram, TikTok).", "Host “What’s Up Wednesdays.”", "Edit video."]
    assert sentences("") == []


def test_missing_page_renders_html_for_browsers(client):
    response = client.get("/projects/999", headers={"accept": "text/html"})
    assert response.status_code == 404
    assert "Page not found" in response.text


def test_missing_page_keeps_json_for_api_clients(client):
    response = client.get("/projects/999", headers={"accept": "application/json"})
    assert response.status_code == 404
    assert response.json() == {"detail": "Project not found"}


def test_fallback_marker_stays_greppable_but_hidden(client):
    response = client.get("/about")
    assert "<!-- Showing the latest saved profile snapshot. -->" in response.text


def test_nav_marks_current_page(client):
    response = client.get("/resume")
    assert 'href="/resume" aria-current="page"' in response.text
