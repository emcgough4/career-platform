def test_about_page_loads(client):
    response = client.get("/about")
    assert response.status_code == 200
    assert "About" in response.text


def test_resume_page_loads(client):
    response = client.get("/resume")
    assert response.status_code == 200
    assert "Resume" in response.text
