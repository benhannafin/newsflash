from app import app


def test_health_endpoint():
    client = app.test_client()
    response = client.get("/health")

    assert response.status_code == 200

    data = response.get_json()
    assert data["status"] == "ok"
    assert data["service"] == "NewsFlash"


def test_headlines_endpoint():
    client = app.test_client()
    response = client.get("/headlines")

    assert response.status_code == 200

    data = response.get_json()
    assert "headlines" in data
    assert isinstance(data["headlines"], list)


def test_status_endpoint():
    client = app.test_client()
    response = client.get("/status")

    assert response.status_code == 200

    data = response.get_json()
    assert "api_key_loaded" in data
    assert "database_connected" in data


def test_homepage_loads():
    client = app.test_client()
    response = client.get("/")

    assert response.status_code == 200