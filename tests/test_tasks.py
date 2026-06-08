import uuid
from unittest.mock import patch

from models import Message, Session
from tasks import process_message
from tests.conftest import TestingSessionLocal


def make_db():
    return TestingSessionLocal()


def seed(session_id, messages):
    db = TestingSessionLocal()
    db.add(Session(id=session_id))
    for role, content in messages:
        db.add(Message(session_id=session_id, role=role, content=content))
    db.commit()
    db.close()


def test_process_message_stores_assistant_reply():
    session_id = str(uuid.uuid4())
    seed(session_id, [("user", "Hello")])

    with patch("tasks.SessionLocal", side_effect=make_db):
        with patch("tasks.chat", return_value="task reply"):
            result = process_message(session_id)

    assert result["role"] == "assistant"
    assert result["content"] == "task reply"
    assert result["session_id"] == session_id


def test_process_message_passes_full_history_to_llm():
    session_id = str(uuid.uuid4())
    seed(session_id, [
        ("user", "First"),
        ("assistant", "Reply"),
        ("user", "Second"),
    ])

    with patch("tasks.SessionLocal", side_effect=make_db):
        with patch("tasks.chat", return_value="task reply") as mock_chat:
            process_message(session_id)

    history = mock_chat.call_args[0][0]
    assert len(history) == 3
    assert history[0] == {"role": "user", "content": "First"}
    assert history[1] == {"role": "assistant", "content": "Reply"}
    assert history[2] == {"role": "user", "content": "Second"}


def test_process_message_raises_on_llm_failure():
    session_id = str(uuid.uuid4())
    seed(session_id, [("user", "Hello")])

    with patch("tasks.SessionLocal", side_effect=make_db):
        with patch("tasks.chat", side_effect=Exception("API error")):
            try:
                process_message(session_id)
                assert False, "should have raised"
            except Exception as e:
                assert str(e) == "API error"
