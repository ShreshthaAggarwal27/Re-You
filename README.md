# 🚀 DevMemory – Your AI-Powered Developer Brain

DevMemory is an AI-powered semantic search and code understanding engine that lets developers recall past implementations, retrieve code snippets, explore commit history, and understand features across repositories — all through natural language queries.

It acts as a long-term memory layer for developers and teams.

---

## ✨ Features

- 🔍 **Semantic Search Across Repos** — Search by meaning, not just keywords.  
- 🧠 **Contextual Q&A** — Ask “How does login work?” and get structured code answers.  
- 📄 **Code Snippet Retrieval** with file paths and metadata.  
- 🕒 **Commit Insights** — Understand how features changed over time.  
- 📚 **Embeddings-Based Indexing** of functions, classes, and commits.  
- ⚡ **RAG Pipeline** using Groq LLM + Chroma vector store.

---

## 🏗️ Architecture Overview

### **1. Data & Ingestion Layer**
- GitHub repo cloning (local for MVP)  
- Code extraction using AST (Python) & regex (JS)  
- Commit extraction using Git  
- Chunking functions/classes with metadata

### **2. Storage & Retrieval Layer**
- Embeddings via MiniLM (current)  
- ChromaDB as vector store  
- Metadata stored alongside chunks  
- Hybrid retrieval & reranking (future)

### **3. Query-Answering Layer**
- Retrieval-Augmented Generation (RAG)  
- LLM: Groq API (DeepSeek LLaMA model)  
- Structured answers with citations  
- CLI demo interface (frontend coming soon)

---

## 🚀 Getting Started

## ✅ **1. Create & Activate a Virtual Environment**

### **Create a new environment**
```bash
python -m venv venv
````

### **Activate the environment (Git Bash)**

```bash
source venv/Scripts/activate
```

If using Linux/macOS:

```bash
source venv/bin/activate
```

---

## ✅ **2. Install dependencies**

Once your virtual environment is active:

```bash
pip install -r requirements.txt
```

---

## ✅ **3. Set API Keys**

Create a `.env` file in the project root:

```ini
GROQ_API_KEY=your_key_here
GITHUB_ACCESS_TOKEN=your_github_access_token
```

---

## ✅ **4. Generate embeddings**

```bash
python embeddings/store_embeddings.py
```

---

## ✅ **5. Run the QA service**

```bash
python qa/qa_service.py
```

---

# 📌 Project Structure

```bash
devmemory/
│── extraction/          # Code + commit extraction
│── embeddings/          # Chunking + vector generation
│── qa/                  # RAG pipeline / answer generation
│── retrieval/           # Retrieval logic (vector search)
│── ingestion/           # Repo ingestion + parsing
│── vector_store/        # Auto-generated embeddings DB
│── data/repo/           # Your cloned GitHub repo
│── README.md
│── requirements.txt
```
