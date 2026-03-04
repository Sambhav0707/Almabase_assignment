from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


# ── Auth Schemas ──────────────────────────────────────────────


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    email: str
    created_at: datetime

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ── Document Schemas ─────────────────────────────────────────


class ReferenceDocumentResponse(BaseModel):
    id: int
    file_name: str
    storage_key: str
    processed: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class ReferenceDocumentUploadResponse(BaseModel):
    message: str
    doc: ReferenceDocumentResponse


class QuestionnaireResponse(BaseModel):
    id: int
    file_name: str
    storage_key: str
    created_at: datetime

    model_config = {"from_attributes": True}


# ── RAG Schemas ──────────────────────────────────────────────


class GenerateRequest(BaseModel):
    questionnaire_id: int


class CitationItem(BaseModel):
    file_name: str
    chunk_index: int
    reference_document_id: int


class AnswerItem(BaseModel):
    question_number: int
    question: str
    answer: str
    citations: list[CitationItem]


class GenerateResponse(BaseModel):
    questionnaire_id: int
    answers_generated: int
    results: list[AnswerItem]


class IndexResponse(BaseModel):
    indexed_count: int
    already_processed_count: int
    errors: list[str]


# ── Review Schemas ───────────────────────────────────────────


class ReviewAnswerItem(BaseModel):
    answer_id: int
    question_number: int
    question: str
    generated_answer: str
    edited_answer: Optional[str] = None
    citations: list[CitationItem]

    model_config = {"from_attributes": True}


class ReviewResponse(BaseModel):
    questionnaire_id: int
    items: list[ReviewAnswerItem]


class EditAnswerRequest(BaseModel):
    edited_answer: str


class EditAnswerResponse(BaseModel):
    answer_id: int
    question_number: int
    question: str
    generated_answer: str
    edited_answer: Optional[str] = None
    citations: list[CitationItem]
    updated_at: datetime

    model_config = {"from_attributes": True}


# ── Export Schemas ───────────────────────────────────────────


class ExportResponse(BaseModel):
    export_file: str
