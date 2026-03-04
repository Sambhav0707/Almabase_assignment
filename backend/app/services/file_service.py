import asyncio
import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import ReferenceDocument, Questionnaire
from app.utils.file_utils import sanitize_filename, generate_unique_filepath

load_dotenv()

UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "uploads")
MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE_MB", "10")) * 1024 * 1024  # bytes

PDF_MAGIC_BYTES = b"%PDF"


# ── Validation ───────────────────────────────────────────────


async def validate_pdf(file: UploadFile) -> tuple[str, bytes]:
    """
    Validate that the uploaded file is a non-empty PDF within size limits.

    Returns (sanitized_filename, file_content_bytes).
    Raises HTTPException(400) on any validation failure.
    """
    # 1. Extension check
    filename = file.filename or "unnamed"
    if not filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are allowed",
        )

    # 2. Read content (reliable size check — Starlette's file.size is inconsistent)
    content = await file.read()

    # 3. Empty check
    if len(content) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty",
        )

    # 4. Size limit
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File exceeds maximum size of {MAX_FILE_SIZE // (1024 * 1024)} MB",
        )

    # 5. Magic-byte verification
    if not content[:4].startswith(PDF_MAGIC_BYTES):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File is not a valid PDF",
        )

    safe_name = sanitize_filename(filename)
    return safe_name, content


# ── File I/O ─────────────────────────────────────────────────


def _write_bytes(path: str, data: bytes) -> None:
    """Synchronous helper — called via asyncio.to_thread."""
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as f:
        f.write(data)


async def save_file_to_disk(
    content: bytes, user_id: int, doc_type: str, filename: str
) -> str:
    """
    Save file bytes to uploads/{user_id}/{doc_type}/{filename}.
    Handles directory creation and filename deduplication.

    Returns the relative storage_key.
    """
    directory = os.path.join(UPLOAD_DIR, str(user_id), doc_type)
    os.makedirs(directory, exist_ok=True)

    dest_path = generate_unique_filepath(directory, filename)
    await asyncio.to_thread(_write_bytes, dest_path, content)

    # Store relative path as storage_key (portable)
    return dest_path.replace("\\", "/")


# ── DB Operations ────────────────────────────────────────────


async def create_reference_document(
    session: AsyncSession,
    user_id: int,
    file_name: str,
    storage_key: str,
) -> ReferenceDocument:
    """Insert a ReferenceDocument row and return the refreshed instance."""
    doc = ReferenceDocument(
        user_id=user_id,
        file_name=file_name,
        storage_key=storage_key,
        processed=False,
    )
    session.add(doc)
    await session.commit()
    await session.refresh(doc)
    return doc


async def create_questionnaire(
    session: AsyncSession,
    user_id: int,
    file_name: str,
    storage_key: str,
) -> Questionnaire:
    """Insert a Questionnaire row and return the refreshed instance."""
    doc = Questionnaire(
        user_id=user_id,
        file_name=file_name,
        storage_key=storage_key,
    )
    session.add(doc)
    await session.commit()
    await session.refresh(doc)
    return doc
