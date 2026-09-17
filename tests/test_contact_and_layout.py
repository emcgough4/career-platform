def test_contact_page_loads(client):
    response = client.get("/contact")
    assert response.status_code == 200
    assert "Contact" in response.text


def test_stylesheet_is_served(client):
    response = client.get("/static/css/styles.css")
    assert response.status_code == 200
    assert "@media" in response.text
