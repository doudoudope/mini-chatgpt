def test_rate_limit_blocks_after_10_requests(client, mock_chat):
    session_id = client.post("/sessions", json={}).json()["id"]

    for i in range(10):
        res = client.post(
            f"/sessions/{session_id}/messages", json={"content": f"message {i}"}
        )
        assert res.status_code == 201

    # 11th request must be rejected
    res = client.post(
        f"/sessions/{session_id}/messages", json={"content": "over the limit"}
    )
    assert res.status_code == 429


def test_rate_limit_not_applied_to_get_history(client, mock_chat):
    session_id = client.post("/sessions", json={}).json()["id"]

    # exhaust the POST limit
    for i in range(10):
        client.post(f"/sessions/{session_id}/messages", json={"content": f"msg {i}"})

    # GET history should still work after limit is hit
    res = client.get(f"/sessions/{session_id}/messages")
    assert res.status_code == 200
