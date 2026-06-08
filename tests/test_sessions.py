def test_create_session_with_title(client):
    res = client.post("/sessions", json={"title": "Chat 1"})
    assert res.status_code == 201
    data = res.json()
    assert data["title"] == "Chat 1"
    assert "id" in data
    assert "created_at" in data


def test_create_session_without_title(client):
    res = client.post("/sessions", json={})
    assert res.status_code == 201
    assert res.json()["title"] is None


def test_get_session(client):
    session_id = client.post("/sessions", json={"title": "Test"}).json()["id"]
    res = client.get(f"/sessions/{session_id}")
    assert res.status_code == 200
    assert res.json()["id"] == session_id
    assert res.json()["title"] == "Test"


def test_get_session_not_found(client):
    res = client.get("/sessions/nonexistent-id")
    assert res.status_code == 404
    assert res.json()["detail"] == "Session not found"
