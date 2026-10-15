def test_contact_page_loads(client):
    response = client.get("/contact")
    assert response.status_code == 200
    assert "Contact" in response.text


def test_stylesheet_is_served(client):
    response = client.get("/static/css/styles.css")
    assert response.status_code == 200
    assert "@media" in response.text


def test_google_tag_loads_once_on_every_page(client):
    for path in ("/about", "/resume", "/portfolio", "/contact", "/privacy"):
        html = client.get(path).text
        assert html.count("googletagmanager.com/gtag/js?id=G-QX9JPW5PPP") == 1, path
        assert html.count("gtag('config', 'G-QX9JPW5PPP')") == 1, path
    not_found = client.get("/no-such-page", headers={"accept": "text/html"})
    assert not_found.status_code == 404
    assert not_found.text.count("gtag/js?id=G-QX9JPW5PPP") == 1
