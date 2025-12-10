import os
from pathlib import Path
from chromadb import PersistentClient
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from extraction.extract_data import run_extraction

VECTOR_BASE_DIR = "vector_store"

def create_vector_store(repo_id: int, repo_path: str):
    repo_path = Path(repo_path)

    if not repo_path.exists():
        raise FileNotFoundError(f"❌ Repo folder missing: {repo_path}")

    # Extract code + commits
    code_chunks, commits = run_extraction(repo_path)

    # Make folder: vector_store/<repo_id>/
    persist_dir = Path(VECTOR_BASE_DIR) / str(repo_id)
    persist_dir.mkdir(parents=True, exist_ok=True)

    # Load embedding model
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

    # Init chroma
    client = PersistentClient(
        path=str(persist_dir),
        settings=Settings(anonymized_telemetry=False)
    )

    collection = client.get_or_create_collection("devmemory")

    documents = []
    metadatas = []
    ids = []

    # Add code chunks
    for i, chunk in enumerate(code_chunks):
        documents.append(chunk["code"])
        metadatas.append({
            "type": chunk["type"],
            "language": chunk["language"],
            "path": chunk["path"],
            "name": chunk["name"],
        })
        ids.append(f"code_{i}")

    # Add commits
    for i, commit in enumerate(commits):
        documents.append(commit["message"])
        metadatas.append({
            "type": "commit",
            "sha": commit["sha"],
            "date": commit["date"],
        })
        ids.append(f"commit_{i}")

    print(f"🔧 Generating embeddings for repo {repo_id} ({len(documents)} items)…")
    embeddings = model.encode(documents, show_progress_bar=True)

    collection.add(
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas,
        ids=ids
    )

    print(f"🟢 Embeddings stored in: {persist_dir}")