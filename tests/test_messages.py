def create_session(client, title="Test"):
    return client.post("/sessions", json={"title": title}).json()["id"]


def send_message(client, session_id, content="Hello"):
    return client.post(
        f"/sessions/{session_id}/messages", json={"content": content}
    )


# --- Route behaviour (LLM is mocked at task level) ---

def test_send_message_returns_job_id(client, mock_task):
    session_id = create_session(client)
    res = send_message(client, session_id)
    assert res.status_code == 202
    data = res.json()
    assert data["job_id"] == "test-job-id"
    assert data["status"] == "pending"
    assert data["message"] is None


def test_send_message_enqueues_task_with_session_id(client, mock_task):
    session_id = create_session(client)
    send_message(client, session_id, "Hello")
    mock_task.delay.assert_called_once_with(session_id)


def test_send_message_persists_user_message(client, mock_task):
    session_id = create_session(client)
    send_message(client, session_id, "Hello")
    messages = client.get(f"/sessions/{session_id}/messages").json()["messages"]
    assert len(messages) == 1
    assert messages[0]["role"] == "user"
    assert messages[0]["content"] == "Hello"


def test_list_messages_empty_session(client):
    session_id = create_session(client)
    res = client.get(f"/sessions/{session_id}/messages")
    assert res.status_code == 200
    assert res.json()["messages"] == []


def test_list_messages_session_not_found(client):
    res = client.get("/sessions/nonexistent-id/messages")
    assert res.status_code == 404


# --- Error cases ---

def test_send_message_session_not_found(client, mock_task):
    res = send_message(client, "nonexistent-id")
    assert res.status_code == 404
    assert res.json()["detail"] == "Session not found"


def test_send_message_empty_content(client):
    session_id = create_session(client)
    res = client.post(f"/sessions/{session_id}/messages", json={"content": ""})
    assert res.status_code == 422


def test_send_message_whitespace_content(client):
    session_id = create_session(client)
    res = client.post(f"/sessions/{session_id}/messages", json={"content": "   "})
    assert res.status_code == 422


def test_send_message_missing_field(client):
    session_id = create_session(client)
    res = client.post(f"/sessions/{session_id}/messages", json={})
    assert res.status_code == 422
