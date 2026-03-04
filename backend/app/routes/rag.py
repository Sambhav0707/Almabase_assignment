from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models import User
from app.schemas import GenerateRequest, GenerateResponse
from app.services.rag_service import generate_answers

router = APIRouter(prefix="/rag", tags=["RAG"])


@router.post("/generate", response_model=GenerateResponse)
async def generate(
    payload: GenerateRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Generate answers for all questions in a questionnaire using RAG.
    Retrieves relevant chunks from the user's indexed reference documents.
    """
    result = await generate_answers(payload.questionnaire_id, user.id, db)
    return GenerateResponse(**result)
