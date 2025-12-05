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

### **1. Install dependencies**
```bash
pip install -r requirements.txt
```

### **2. Set API Keys**
Create a .env file:
```ini
GROQ_API_KEY=your_key_here
```

### **3. Generate embeddings**
```bash
python embeddings/store_embeddings.py
```

### **4. Run the QA service**
```bash
python qa/qa_service.py
```

## 📌 Project Structure
```bash
devmemory/
│── extraction/
│── embeddings/
│── qa/
│── retrieval/
│── ingestion/
│── vector_store/        # auto-generated
│── data/repo/           # your cloned repo
│── README.md
│── requirements.txt
```