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


def test_is_video_detects_video_files():
    from app.templating import is_video

    assert is_video("/static/media/clip.MP4")
    assert is_video("https://cdn.example.com/a.webm?x=1")
    assert not is_video("/static/media/still.jpg")
    assert not is_video(None)


def test_embed_url_supports_youtube_tiktok_and_instagram():
    from app.templating import embed_url

    assert embed_url("https://youtu.be/abc123") == "https://www.youtube-nocookie.com/embed/abc123"
    assert embed_url("https://www.youtube.com/watch?v=abc123") == "https://www.youtube-nocookie.com/embed/abc123"
    assert embed_url("https://youtube.com/shorts/abc123") == "https://www.youtube-nocookie.com/embed/abc123"
    assert embed_url("https://www.tiktok.com/@theloyolan/video/7300000000000000000") == "https://www.tiktok.com/embed/v2/7300000000000000000"
    assert embed_url("https://www.instagram.com/reel/Cabc123/") == "https://www.instagram.com/reel/Cabc123/embed"
    assert embed_url("https://example.com/post") == ""
    assert embed_url(None) == ""
