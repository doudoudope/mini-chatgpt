from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session as DBSession

from database import get_db
from dependencies import limiter
from models import Message, Session
from schemas import JobResponse, MessageCreate, MessageListResponse
from tasks import process_message

router = APIRouter(prefix="/sessions", tags=["messages"])


@router.post("/{session_id}/messages", response_model=JobResponse, status_code=202)
@limiter.limit("10/minute")
def send_message(request: Request, session_id: str, body: MessageCreate, db: DBSession = Depends(get_db)):
    session = db.query(Session).filter(Session.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    user_msg = Message(session_id=session_id, role="user", content=body.content)
    db.add(user_msg)
    db.commit()

    task = process_message.delay(session_id)
    return {"job_id": task.id, "status": "pending", "message": None}


@router.get("/{session_id}/messages", response_model=MessageListResponse)
def list_messages(session_id: str, db: DBSession = Depends(get_db)):
    session = db.query(Session).filter(Session.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    messages = (
        db.query(Message)
        .filter(Message.session_id == session_id)
        .order_by(Message.created_at)
        .all()
    )
    return {"messages": messages}
