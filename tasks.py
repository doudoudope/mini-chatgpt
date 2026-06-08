from celery_app import celery
from database import SessionLocal
from models import Message
from services.llm import chat


@celery.task
def process_message(session_id: str):
    db = SessionLocal()
    try:
        history = (
            db.query(Message)
            .filter(Message.session_id == session_id)
            .order_by(Message.created_at)
            .all()
        )
        messages = [{"role": m.role, "content": m.content} for m in history]

        assistant_text = chat(messages)

        assistant_msg = Message(
            session_id=session_id,
            role="assistant",
            content=assistant_text,
        )
        db.add(assistant_msg)
        db.commit()
        db.refresh(assistant_msg)

        return {
            "id": assistant_msg.id,
            "session_id": assistant_msg.session_id,
            "role": assistant_msg.role,
            "content": assistant_msg.content,
            "created_at": assistant_msg.created_at.isoformat(),
        }
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
