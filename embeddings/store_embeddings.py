import sys
import os
os.environ["HF_HUB_ENABLE_HF_TRANSFER"] = "0"
os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"
os.environ["HF_HUB_DISABLE_XET_WARNING"] = "1"
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import json
from chromadb import PersistentClient
from chromadb.config import Settings
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from extraction.extract_data import run_extraction


# Load environment variables
load_dotenv()

def create_vector_store():
    # Run extraction to get chunks & commits
    code_chunks, commits = run_extraction()

    # ✅ Make sure the folder exists
    os.makedirs("vector_store", exist_ok=True)

    # ✅ Model for embeddings
    # model = SentenceTransformer("all-MiniLM-L6-v2")
    model = SentenceTransformer(
        "sentence-transformers/all-MiniLM-L6-v2",
        cache_folder="./hf_cache",
        use_auth_token=None
    )

    # ✅ Initialize Chroma (local)
    client = PersistentClient(path="vector_store", settings=Settings(anonymized_telemetry=False))

    # ✅ Create or get collection
    collection = client.get_or_create_collection(name="devmemory")

    # ✅ Prepare and insert embeddings
    documents = []
    metadatas = []
    ids = []

    # Code chunks
    for i, chunk in enumerate(code_chunks):
        text = chunk["code"]
        documents.append(text)
        metadatas.append({
            "type": chunk["type"],
            "language": chunk["language"],
            "path": chunk["path"],
            "name": chunk["name"],
        })
        ids.append(f"code_{i}")

    # Commit messages
    for i, commit in enumerate(commits):
        text = commit["message"]
        documents.append(text)
        metadatas.append({
            "type": "commit",
            "sha": commit["sha"],
            "date": commit["date"],
        })
        ids.append(f"commit_{i}")

    print(f"✅ Generating embeddings for {len(documents)} items...")
    embeddings = model.encode(documents, show_progress_bar=True)

    # ✅ Insert into Chroma
    collection.add(
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas,
        ids=ids
    )

    print(f"Code chunks extracted: {len(code_chunks)}")
    print(f"First 3 chunks: {code_chunks[:3]}")

    print("✅ Stored embeddings in ChromaDB!")
    print("🟢 Vector store saved to:", os.path.abspath("vector_store"))

if __name__ == "__main__":
    create_vector_store()
