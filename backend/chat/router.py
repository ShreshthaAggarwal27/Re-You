from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from auth.jwt import get_current_user
from qa.qa_service import answer_question

router = APIRouter(prefix="/chat", tags=["chat"])

class QueryRequest(BaseModel):
    question: str

@router.post("/query")
def chat_query(request: QueryRequest, user=Depends(get_current_user)):
    try:
        # response = answer_question(request.question, user.id)
        response = answer_question(request.question)

        return {
            "answer": response.get("answer", "No answer."),
            "sources": response.get("sources", []),
            "snippets": response.get("snippets", [])
        }
    except Exception as e:
        print("CHAT ERROR:", e)
        raise HTTPException(status_code=500, detail=str(e))