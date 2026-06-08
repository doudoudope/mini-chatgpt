from unittest.mock import MagicMock, patch


def test_get_job_pending(client):
    mock_result = MagicMock()
    mock_result.state = "PENDING"
    with patch("routers.jobs.AsyncResult", return_value=mock_result):
        res = client.get("/jobs/some-job-id")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "pending"
    assert data["message"] is None


def test_get_job_done(client):
    mock_result = MagicMock()
    mock_result.state = "SUCCESS"
    mock_result.result = {
        "id": "msg-id",
        "session_id": "session-id",
        "role": "assistant",
        "content": "Hello!",
        "created_at": "2026-06-08T10:00:00",
    }
    with patch("routers.jobs.AsyncResult", return_value=mock_result):
        res = client.get("/jobs/some-job-id")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "done"
    assert data["message"]["content"] == "Hello!"
    assert data["message"]["role"] == "assistant"


def test_get_job_failed(client):
    mock_result = MagicMock()
    mock_result.state = "FAILURE"
    with patch("routers.jobs.AsyncResult", return_value=mock_result):
        res = client.get("/jobs/some-job-id")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "failed"
    assert data["message"] is None
