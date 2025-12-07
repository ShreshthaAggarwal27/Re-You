# routes/me.py
from fastapi import APIRouter, Depends
from auth.jwt import get_current_user

router = APIRouter()

@router.get("/me")
def get_user(user=Depends(get_current_user)):
    return {
        "id": user.id,
        "username": user.github_username,
        "avatar": user.github_avatar,
    }
