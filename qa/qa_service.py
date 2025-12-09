import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain.chains import RetrievalQA
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import SentenceTransformerEmbeddings
from chromadb import PersistentClient

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("Please set your GROQ_API_KEY in .env file")

embedding_model = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
client = PersistentClient(path="vector_store")
collection = client.get_collection("devmemory")

vectorstore = Chroma(
    client=client,
    collection_name="devmemory",
    embedding_function=embedding_model
)

llm = ChatGroq(
    model="groq/compound",
    temperature=0,
    max_tokens=None,
    timeout=None,
    api_key=GROQ_API_KEY,
)

qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=vectorstore.as_retriever(search_kwargs={
        "k": 5,
        "filter": {"type": {"$ne": "commit"}}
    }),
    chain_type="stuff",
    return_source_documents=True
)

def ask_question(question: str):
    prompt = f"""
            You are a code assistant. Search through code snippets and return only relevant code blocks.
            Question: {question}
            """
    result = qa_chain.invoke({"query": prompt})
    return result


if __name__ == "__main__":
    print("🟢 Re:You is Ready!")
    while True:
        query = input("\n ❓Ask a question (or type 'exit'): ")
        if query.lower() in ["exit", "quit"]:
            break

        response = ask_question(query)

        print("\n✅ Answer:")
        print(response["result"])

        print("\n📄 Sources:")
        for doc in response["source_documents"]:
            snippet = doc.page_content[:300] + ("..." if len(doc.page_content) > 300 else "")
            print(f" - {doc.metadata} | {snippet}")
