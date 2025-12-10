import os
from chromadb import PersistentClient
from chromadb.config import Settings
from sqlalchemy.orm import Session
from sentence_transformers import SentenceTransformer
from repositories.model import Repository
from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()

# -------- LLM --------
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
llm = ChatGroq(
    api_key=GROQ_API_KEY,
    model="groq/compound",
    temperature=0,
)

# -------- Embeddings --------
MODEL = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")


def load_vectorstore(repo_id: int):
    """
    Load the vector store for a specific repo (vector_store/<repo_id>)
    """
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


def answer_question(question: str, user, db: Session):
    """
    Multi-repo RAG:
    - Retrieve top docs from each repo
    - Merge retrieved docs
    - Feed to Groq LLM for final answer
    """

    # 1️⃣ Find user-selected repositories
    repos = db.query(Repository).filter(
        Repository.user_id == user.id,
        Repository.selected == True
    ).all()

    if not repos:
        return {"answer": "You have no repositories selected. Run setup first."}

    # 2️⃣ Retrieve from each repo
    retrieved_context = []
    sources = []

    for repo in repos:
        client, col = load_vectorstore(repo.id)
        if col is None:
            continue

        result = col.query(
            query_texts=[question],
            n_results=3
        )

        docs = result["documents"][0]

        for doc in docs:
            retrieved_context.append(doc)
            sources.append({"repo": repo.full_name, "text": doc})

    if not retrieved_context:
        return {"answer": "No relevant code found in selected repositories."}

    # 3️⃣ Build context block
    context_block = "\n\n".join([f"---\n{c}" for c in retrieved_context])

    # 4️⃣ Build LLM prompt
    prompt = f"""
You are an expert AI coding assistant.

You must answer the user's question based ONLY on the retrieved code snippets.
If useful, include code blocks using triple backticks.

User Question:
{question}

Relevant Code Snippets:
{context_block}

Provide:
- Clear explanation
- Referenced code blocks
- File or function names if detectable
"""

    # 5️⃣ Generate answer from Groq LLM
    llm_answer = llm.invoke(prompt).content

    # 6️⃣ Return structured response for UI
    return {
        "answer": llm_answer,
        "sources": sources,
        "snippets": retrieved_context,
    }