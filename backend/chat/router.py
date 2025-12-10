# from fastapi import APIRouter, Depends
# from pydantic import BaseModel
# from sqlalchemy.orm import Session
# from auth.jwt import get_current_user
# from database import get_db
# from qa.qa_service import answer_question

# router = APIRouter(prefix="/chat", tags=["chat"])


# class ChatRequest(BaseModel):
#     question: str


# @router.post("/query")
# def query_chat(payload: ChatRequest, user=Depends(get_current_user), db: Session = Depends(get_db)):
#     try:
#         response = answer_question(payload.question, user, db)
#         return {"answer": response["answer"]}
#     except Exception as e:
#         print("CHAT ERROR:", e)
#         return {"answer": "Internal error. Check backend logs."}

# backend/chat/router.py
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from auth.jwt import get_current_user
from database import get_db
from qa.qa_service import answer_question
from chat.models import ChatSession, ChatMessage

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatRequest(BaseModel):
    question: str
    session_id: int | None = None


class ChatSessionCreate(BaseModel):
    title: str | None = None


@router.post("/session")
def create_session(
    payload: ChatSessionCreate,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    session = ChatSession(
        user_id=user.id,
        title=payload.title or "New chat",
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return {"id": session.id, "title": session.title}


@router.get("/sessions")
def list_sessions(
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    sessions = (
        db.query(ChatSession)
        .filter(ChatSession.user_id == user.id)
        .order_by(ChatSession.updated_at.desc())
        .all()
    )

    return [
        {
            "id": s.id,
            "title": s.title,
            "created_at": s.created_at,
            "updated_at": s.updated_at,
            "preview": s.messages[0].content[:100] + "..." if s.messages else "",
        }
        for s in sessions
    ]


@router.get("/sessions/{session_id}")
def get_session_messages(
    session_id: int,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    session = (
        db.query(ChatSession)
        .filter(ChatSession.id == session_id, ChatSession.user_id == user.id)
        .first()
    )
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    return {
        "id": session.id,
        "title": session.title,
        "messages": [
            {
                "id": m.id,
                "role": m.role,
                "content": m.content,
                "created_at": m.created_at,
            }
            for m in session.messages
        ],
    }


@router.post("/query")
def query_chat(
    payload: ChatRequest,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # 1) Resolve or create session
    session: ChatSession | None = None

    if payload.session_id is not None:
        session = (
            db.query(ChatSession)
            .filter(ChatSession.id == payload.session_id, ChatSession.user_id == user.id)
            .first()
        )
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
    else:
        session = ChatSession(user_id=user.id, title="New chat")
        db.add(session)
        db.commit()
        db.refresh(session)

    # 2) Store user message
    user_msg = ChatMessage(
        session_id=session.id,
        role="user",
        content=payload.question,
    )
    db.add(user_msg)
    db.commit()

    # 3) Get LLM answer (your multi-repo RAG)
    rag_response = answer_question(payload.question, user, db)
    answer_text = rag_response["answer"] if isinstance(rag_response, dict) else str(rag_response)

    # 4) Store assistant message
    assistant_msg = ChatMessage(
        session_id=session.id,
        role="assistant",
        content=answer_text,
    )
    db.add(assistant_msg)

    # 5) Update session timestamp
    session.updated_at = assistant_msg.created_at
    db.commit()

    return {
        "session_id": session.id,
        "answer": answer_text,
    }