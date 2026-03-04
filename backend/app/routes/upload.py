from fastapi import APIRouter, Depends, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models import User
from app.schemas import (
    ReferenceDocumentResponse,
    QuestionnaireResponse,
    ReferenceDocumentUploadResponse,
)
from app.services.file_service import (
    validate_pdf,
    save_file_to_disk,
    create_reference_document,
    create_questionnaire,
)
from app.services.rag_service import index_reference_document

router = APIRouter(prefix="/upload", tags=["File Upload"])


@router.post(
    "/reference",
    response_model=ReferenceDocumentUploadResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_reference(
    file: UploadFile,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Upload a PDF reference document for the authenticated user."""
    filename, content = await validate_pdf(file)

    storage_key = await save_file_to_disk(content, user.id, "reference", filename)

    doc = await create_reference_document(db, user.id, filename, storage_key)

    # Immediately extract, chunk, and embed the document
    await index_reference_document(doc.id, user.id, db)

    return {
        "message": "Document uploaded and indexed successfully",
        "doc": doc,
    }


@router.post(
    "/questionnaire",
    response_model=QuestionnaireResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_questionnaire(
    file: UploadFile,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Upload a PDF questionnaire for the authenticated user."""
    filename, content = await validate_pdf(file)

    storage_key = await save_file_to_disk(content, user.id, "questionnaire", filename)

    doc = await create_questionnaire(db, user.id, filename, storage_key)
    return doc
