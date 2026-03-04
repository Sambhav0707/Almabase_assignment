# AI-Powered Structured Questionnaire Answering Tool

## Overview

This project is an **AI-powered questionnaire automation system** that helps teams automatically answer structured questionnaires (such as security reviews, vendor assessments, or compliance forms) using internal documentation.

The system allows users to:

* Upload reference documents that contain source-of-truth information
* Upload structured questionnaires
* Automatically generate answers using Retrieval-Augmented Generation (RAG)
* Review and edit answers
* Export the completed questionnaire with citations

The goal of the project is to demonstrate how **AI systems can automate document-based workflows while maintaining grounded outputs and traceable citations.**

---

# Live Application

Frontend (Flutter Web):

```
https://YOUR_FIREBASE_URL.web.app
```

Backend API Docs:

```
https://almabase-assignment-2rtk.onrender.com/docs
```

GitHub Repository:

```
https://github.com/YOUR_USERNAME/almabase-assignment
```

---

# Industry & Company Context

## Industry

SaaS — Security & Compliance Automation

## Fictional Company

**SecureFlow**

SecureFlow is a SaaS platform that helps organizations automate security compliance and vendor risk management workflows. The platform integrates with internal documentation systems to streamline security assessments, vendor onboarding, and compliance audits.

Organizations frequently receive vendor questionnaires and security assessments that must be completed using internal documentation.

This tool automates that process.

---

# Key Features

## Authentication

* Secure signup/login system
* JWT-based authentication
* Protected API routes

## Document Ingestion

Users can upload:

* Reference documents (source-of-truth)
* Questionnaires (questions to answer)

Documents are stored with **user isolation**.

---

## Retrieval-Augmented Generation (RAG)

The system:

1. Extracts text from uploaded documents
2. Splits text into semantic chunks
3. Generates embeddings
4. Stores them in a vector database
5. Retrieves relevant context for each question
6. Uses an LLM to generate grounded answers

Each generated answer includes **citations referencing the source document.**

---

## Review System

Users can:

* Review generated answers
* Edit answers
* Maintain citations
* Preserve the original questionnaire structure

---

## Export

Users can export the completed questionnaire as a **Markdown document** that includes:

* Original questions
* Generated or edited answers
* Citations
* Coverage summary

---

# System Architecture

## High-Level Architecture

```
Flutter Web Frontend (Firebase Hosting)
            │
            ▼
      FastAPI Backend (Render)
            │
            ▼
      PostgreSQL Database
            │
            ▼
      Vector Database (ChromaDB)
            │
            ▼
      OpenRouter LLM API
```

---

# Backend Architecture

The backend is built with **FastAPI** and follows a modular service architecture.

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
├── models.py
├── schemas.py
├── database.py
└── main.py
```

---

# RAG Pipeline

The Retrieval-Augmented Generation pipeline follows this process:

```
Reference PDF Upload
        │
        ▼
Text Extraction (pypdf)
        │
        ▼
Chunking (800 chars + overlap)
        │
        ▼
Embedding Generation
        │
        ▼
Vector Storage (ChromaDB)
        │
        ▼
Question Parsing
        │
        ▼
Semantic Search
        │
        ▼
Context Retrieval
        │
        ▼
LLM Generation
        │
        ▼
Answer + Citations
```

---

# User Flow

```
User Signup/Login
        │
        ▼
Upload Reference Documents
        │
        ▼
Upload Questionnaire
        │
        ▼
Automatic Document Indexing
        │
        ▼
Generate Answers
        │
        ▼
Review / Edit Answers
        │
        ▼
Export Final Document
```

---

# Frontend Architecture

The frontend is built using **Flutter Web** and deployed on **Firebase Hosting**.

```
lib/
│
├── services/
│     api_service.dart
│
├── screens/
│     login_screen.dart
│     signup_screen.dart
│     dashboard_screen.dart
│     upload_screen.dart
│     review_screen.dart
│
├── models/
│     answer_model.dart
│
└── widgets/
      primary_button.dart
```

---

# Technologies Used

## Backend

* FastAPI
* SQLAlchemy (Async)
* PostgreSQL
* ChromaDB (vector database)
* PyPDF
* OpenRouter LLM API
* JWT Authentication

## Frontend

* Flutter Web
* Firebase Hosting
* HTTP package
* SharedPreferences

## Infrastructure

* Render (backend hosting)
* Firebase (frontend hosting)
* Render PostgreSQL

---

# Data Flow

```
User Uploads Reference Docs
          │
          ▼
Text Extraction
          │
          ▼
Embedding Generation
          │
          ▼
Vector Storage
          │
          ▼
User Uploads Questionnaire
          │
          ▼
Question Parsing
          │
          ▼
Vector Search
          │
          ▼
Context Retrieval
          │
          ▼
LLM Answer Generation
          │
          ▼
Answer + Citations
          │
          ▼
User Review
          │
          ▼
Export Document
```

---

# Assumptions Made

1. Reference documents contain the authoritative information needed to answer the questionnaire.
2. Questionnaires contain clearly structured questions that can be parsed heuristically.
3. Users upload reasonably formatted PDFs with readable text.
4. The system assumes questions end with `?` or are numbered.
5. Vector similarity is sufficient to retrieve relevant information for answering questions.

---

# Trade-offs

## Simplicity vs Production Scalability

For the purpose of the assignment, certain trade-offs were made:

### Local Vector Storage

ChromaDB is used as an embedded vector store instead of a managed vector database.

Pros:

* Simple setup
* Easy local development

Cons:

* Not horizontally scalable

---

### Synchronous Processing

Document indexing happens during upload instead of background jobs.

Pros:

* Simpler architecture
* No task queue required

Cons:

* Upload latency increases for large documents

---

### Basic Question Parsing

The system uses heuristic-based parsing rather than an LLM-based parser.

Pros:

* Faster
* Deterministic

Cons:

* May fail with complex questionnaire formats

---

# Improvements With More Time

If more time were available, the following improvements would be implemented.

---

## Background Job Queue

Move document indexing and embedding generation into background workers using:

* Celery
* Redis
* RabbitMQ

This would prevent blocking uploads.

---

## Vector Database Upgrade

Replace ChromaDB with a production-grade vector database:

* Pinecone
* Weaviate
* Qdrant

This would improve scalability and retrieval performance.

---

## Better Question Parsing

Use an LLM-based parser to extract questions from complex questionnaire formats.

---

## Confidence Scores

Add confidence scores based on:

* embedding similarity
* number of supporting chunks

---

## Evidence Snippets

Display the exact text snippets retrieved from reference documents that were used to generate the answer.

---

## Partial Regeneration

Allow users to regenerate answers for individual questions.

---

## Version History

Maintain multiple answer generations so users can compare different outputs.

---

# Nice-to-Have Features Implemented

The project implements one of the optional improvements:

### Coverage Summary

The export document includes:

* Total questions
* Questions answered with citations
* Questions marked **"Not found in references."**

---

# Running the Project Locally

Backend:

```
uv sync
uv run uvicorn app.main:app --reload
```

Frontend:

```
flutter run -d chrome
```

---

# Deployment

Frontend:

Firebase Hosting

Backend:

Render

Database:

Render PostgreSQL

LLM:

OpenRouter API

---

# Conclusion

This project demonstrates how Retrieval-Augmented Generation can be applied to automate structured workflows such as security questionnaires.

The system focuses on:

* grounded outputs
* clear citations
* human-in-the-loop review

This approach ensures that AI-generated answers remain **traceable, auditable, and reliable**.
