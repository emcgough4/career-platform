def test_portfolio_page_loads(client):
    response = client.get("/portfolio")
    assert response.status_code == 200
    assert "Portfolio" in response.text


def test_missing_project_detail_returns_not_found(client):
    response = client.get("/projects/999")
    assert response.status_code == 404
