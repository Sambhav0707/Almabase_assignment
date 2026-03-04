from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models import User
from app.schemas import ExportResponse
from app.services.export_service import export_questionnaire

router = APIRouter(prefix="/export", tags=["Export"])


@router.post("/{questionnaire_id}", response_model=ExportResponse)
async def export(
    questionnaire_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Export all answers for a questionnaire as a Markdown document.
    Uses edited answers where available, otherwise uses generated answers.
    Includes a coverage summary at the top.
    """
    file_path = await export_questionnaire(questionnaire_id, user.id, db)
    return ExportResponse(export_file=file_path)
