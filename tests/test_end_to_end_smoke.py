def test_public_pages_are_reachable(client):
    for route in ("/about", "/resume", "/portfolio", "/contact"):
        response = client.get(route)
        assert response.status_code == 200
