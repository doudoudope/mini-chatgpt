def test_no_api_key_returns_401(client):
    res = client.get("/sessions/some-id", headers={"X-API-Key": ""})
    # Completely absent header
    res = client.get("/sessions/some-id", headers={})
    assert res.status_code == 401
    assert res.json()["detail"] == "Missing API key"


def test_wrong_api_key_returns_403(client):
    res = client.get("/sessions/some-id", headers={"X-API-Key": "wrong-key"})
    assert res.status_code == 403
    assert res.json()["detail"] == "Invalid API key"


def test_valid_api_key_passes_through(client):
    # 404 means auth passed and the route ran (session just doesn't exist)
    res = client.get("/sessions/nonexistent-id")
    assert res.status_code == 404


def test_health_requires_no_api_key(client):
    # /health is intentionally unprotected
    res = client.get("/health", headers={})
    assert res.status_code == 200
