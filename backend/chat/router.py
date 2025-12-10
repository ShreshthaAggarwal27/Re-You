from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from auth.jwt import get_current_user
from database import get_db
from qa.qa_service import answer_question

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatRequest(BaseModel):
    question: str


@router.post("/query")
def query_chat(payload: ChatRequest, user=Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        response = answer_question(payload.question, user, db)
        return {"answer": response["answer"]}
    except Exception as e:
        print("CHAT ERROR:", e)
        return {"answer": "Internal error. Check backend logs."}