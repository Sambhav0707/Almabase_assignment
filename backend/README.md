# Backend Architecture (FastAPI RAG System)

## Overview

The backend is built using **FastAPI** and implements the complete RAG pipeline.

Responsibilities include:

* authentication
* document ingestion
* PDF parsing
* vector indexing
* answer generation
* review system
* export generation

---

# Backend Architecture

```
Client Request
      │
      ▼
FastAPI Routes
      │
      ▼
Service Layer
      │
      ▼
Database / Vector DB
      │
      ▼
OpenRouter LLM
```

---

# Service Layer Design

The backend follows a **service-oriented architecture**.

```
routes/
   │
   ▼
services/
   │
   ▼
database + external APIs
```

Routes only handle HTTP logic, while services implement business logic.

---

# Folder Structure

```
app/
│
├── routes/
│     auth.py
│     upload.py
│     rag.py
│     review.py
│     export.py
│
├── services/
│     user_service.py
│     file_service.py
│     pdf_service.py
│     chunking_service.py
│     embedding_service.py
│     chroma_service.py
│     rag_service.py
│     review_service.py
│     export_service.py
│
├── auth/
│     jwt.py
│     hashing.py
│
├── models.py
├── schemas.py
├── database.py
└── main.py
```

---

# RAG Pipeline

```
Reference Document
       │
       ▼
Text Extraction
       │
       ▼
Chunking
       │
       ▼
Embedding Generation
       │
       ▼
Vector Storage
       │
       ▼
Question Retrieval
       │
       ▼
LLM Generation
       │
       ▼
Answer + Citations
```

---

# Database Schema

Main tables:

Users

```
id
email
password_hash
created_at
```

ReferenceDocuments

```
id
user_id
file_name
storage_key
processed
created_at
```

QuestionnaireAnswers

```
id
questionnaire_id
question_text
generated_answer
edited_answer
citations
```

---

# Embedding Pipeline

```
PDF
 │
 ▼
Text Extraction
 │
 ▼
Chunking
 │
 ▼
Embedding Generation
 │
 ▼
Vector Store (ChromaDB)
```

---

# Retrieval Process

```
User Question
      │
      ▼
Embedding
      │
      ▼
Vector Search
      │
      ▼
Relevant Chunks
      │
      ▼
LLM Prompt
      │
      ▼
Generated Answer
```

---

# Environment Variables

```
DATABASE_URL
OPENROUTER_API_KEY
CHROMA_PERSIST_DIR
UPLOAD_DIR
MAX_FILE_SIZE_MB
```

---

# Local Setup

Install dependencies

```
uv sync
```

Run server

```
uv run uvicorn app.main:app --reload
```

Open docs

```
http://localhost:8000/docs
```

---

# Deployment

Backend is deployed on Render.

Key configuration:

Build command

```
pip install uv && uv sync
```

Start command

```
uv run uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

---

# Future Improvements

* background indexing workers
* vector DB scaling
* improved retrieval ranking
* caching layer
