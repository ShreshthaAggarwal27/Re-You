import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain.chains import RetrievalQA
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import SentenceTransformerEmbeddings
from chromadb import PersistentClient

load_dotenv()

# ---------- API Key ----------
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("Please set your GROQ_API_KEY in .env file")

# ---------- Embeddings ----------
embedding_model = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

# ---------- Chroma DB ----------
client = PersistentClient(path="vector_store")
collection = client.get_collection("devmemory")

vectorstore = Chroma(
    client=client,
    collection_name="devmemory",
    embedding_function=embedding_model
)

# ---------- LLM ----------
llm = ChatGroq(
    model="groq/compound",
    temperature=0,
    max_tokens=None,
    timeout=None,
    api_key=GROQ_API_KEY,
)

# ---------- Retrieval Chain ----------
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=vectorstore.as_retriever(search_kwargs={
        "k": 5,
        "filter": {"type": {"$ne": "commit"}}
    }),
    chain_type="stuff",
    return_source_documents=True
)


# ============================================================
#   MAIN FUNCTION used by backend routes
# ============================================================
def answer_question(question: str):
    """
    Runs retrieval + LLM reasoning and returns structured output.
    """

    prompt = f"""
    You are a code assistant. Search through code snippets and return only relevant code blocks.
    Question: {question}
    """

    result = qa_chain.invoke({"query": prompt})

    final_answer = result["result"]
    source_docs = result["source_documents"]

    # Extract source metadata and code snippets cleanly
    retrieved_docs = []
    code_blocks = []

    for doc in source_docs:
        retrieved_docs.append({
            "text": doc.page_content,
            "metadata": doc.metadata
        })
        code_blocks.append(doc.page_content)

    # ---------- RETURN FORMAT EXPECTED BY FRONTEND ----------
    return {
        "answer": final_answer,
        "sources": retrieved_docs,
        "snippets": code_blocks
    }


# Keep the CLI mode for debugging
if __name__ == "__main__":
    print("🟢 Re:You is Ready!")
    while True:
        query = input("\n ❓ Ask a question (or type 'exit'): ")
        if query.lower() in ["exit", "quit"]:
            break

        response = answer_question(query)

        print("\n✅ Answer:")
        print(response["answer"])

        print("\n📄 Sources:")
        for src in response["sources"]:
            snippet = src["text"][:250] + "..."
            print(f" - {src['metadata']} | {snippet}")