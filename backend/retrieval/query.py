import os
from chromadb import PersistentClient
from sentence_transformers import SentenceTransformer
from chromadb.config import Settings

# ✅ Load the same embedding model used during storage
model = SentenceTransformer("all-MiniLM-L6-v2")

# ✅ Connect to existing Chroma DB
client = PersistentClient(path="vector_store", settings=Settings(anonymized_telemetry=False))
collection = client.get_collection("devmemory")

def query_rag(question, top_k=5):
    query_embedding = model.encode([question])

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=top_k,
        where={"type": {"$ne": "commit"}}   # ✅ Exclude commits
    )
    return results

if __name__ == "__main__":
    while True:
        user_input = input("\n🔍 Ask a question (or 'exit'): ")
        if user_input.lower() in ["exit", "quit"]:
            break

        results = query_rag(user_input, top_k=5)

        print("\n🧠 Top Relevant Results:")
        for i, doc in enumerate(results["documents"][0], 1):
            meta = results["metadatas"][0][i - 1]
            print(f"\n{i}. {meta}")
            print(doc[:300], "..." if len(doc) > 300 else "")
