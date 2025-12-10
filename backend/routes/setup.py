from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from auth.jwt import get_current_user
from database import get_db
from repositories.model import Repository
from ingestion.clone_repo import clone_specific_repo
from embeddings.store_embeddings import create_vector_store

router = APIRouter(prefix="/setup", tags=["setup"])


class SetupPayload(BaseModel):
    repositories: list[str]


@router.post("/complete")
def complete_setup(payload: SetupPayload, user=Depends(get_current_user), db: Session = Depends(get_db)):

    for full_name in payload.repositories:
        owner, repo_name = full_name.split("/")

        db_repo = Repository(
            user_id=user.id,
            name=repo_name,
            full_name=full_name,
            selected=True,
        )
        db.add(db_repo)
        db.commit()
        db.refresh(db_repo)

        # CLONE INTO THIS FOLDER:
        local_path = f"data/repos/{db_repo.id}"

        print(f"⬇️ Cloning {full_name} into {local_path}")
        clone_specific_repo(full_name, local_path)

        print("🧠 Generating embeddings now…")
        create_vector_store(repo_id=db_repo.id, repo_path=local_path)

    user.needs_setup = False
    db.commit()

    return {"success": True}