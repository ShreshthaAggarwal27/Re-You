from chromadb import PersistentClient
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from sqlalchemy.orm import Session
from repositories.model import Repository
import os

MODEL = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

def load_vectorstore(repo_id: int):
    path = f"vector_store/{repo_id}"

    if not os.path.exists(path):
        print(f"❌ Vector store missing for repo {repo_id}")
        return None, None

    client = PersistentClient(path=path, settings=Settings(anonymized_telemetry=False))

    try:
        col = client.get_collection("devmemory")
    except:
        print(f"❌ Collection missing for repo {repo_id}")
        return None, None

    return client, col


# def answer_question(question: str, user, db: Session):
#     # 1️⃣ Get user-selected repos
#     repos = db.query(Repository).filter(
#         Repository.user_id == user.id,
#         Repository.selected == True
#     ).all()

#     if not repos:
#         return "You have no repositories selected. Run setup first."

#     # 2️⃣ Search each repo
#     best_results = []

#     for repo in repos:
#         client, col = load_vectorstore(repo.id)
#         if col is None:
#             continue

#         result = col.query(
#             query_texts=[question],
#             n_results=3
#         )

#         best_results.append((repo.full_name, result))

#     if not best_results:
#         return "No embeddings found for selected repositories. Run setup again."

#     # 3️⃣ Format results
#     answer = "Here is what I found:\n\n"

#     for repo_name, res in best_results:
#         answer += f"\n📁 **{repo_name}**:\n"
#         documents = res["documents"][0]
#         for doc in documents:
#             answer += f"---\n{doc}\n"

#     return answer

def answer_question(question: str, user, db: Session):
    # 1️⃣ Get user-selected repos
    repos = db.query(Repository).filter(
        Repository.user_id == user.id,
        Repository.selected == True
    ).all()

    if not repos:
        return {"answer": "You have no repositories selected. Run setup first."}

    best_results = []

    # 2️⃣ Run RAG search on each repo
    for repo in repos:
        client, col = load_vectorstore(repo.id)
        if col is None:
            continue

        result = col.query(
            query_texts=[question],
            n_results=3
        )

        best_results.append((repo.full_name, result))

    if not best_results:
        return {"answer": "No embeddings found for selected repositories."}

    # 3️⃣ Build clean markdown answer
    final = ""

    for repo_name, res in best_results:
        final += f"### 📁 {repo_name}\n\n"
        docs = res["documents"][0]

        for doc in docs:
            final += f"```txt\n{doc}\n```\n\n"

    # MUST return a dict so router can access response["answer"]
    return {"answer": final}