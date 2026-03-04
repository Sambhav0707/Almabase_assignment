from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models import User
from app.schemas import (
    ReviewResponse,
    ReviewAnswerItem,
    EditAnswerRequest,
    EditAnswerResponse,
)
from app.services.review_service import get_answers_for_questionnaire, update_answer

router = APIRouter(prefix="/review", tags=["Review"])


@router.get("/{questionnaire_id}", response_model=ReviewResponse)
async def review_answers(
    questionnaire_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieve all generated answers for a questionnaire, ordered by question number.
    """
    answers = await get_answers_for_questionnaire(questionnaire_id, user.id, db)
    items = [
        ReviewAnswerItem(
            answer_id=ans.id,
            question_number=ans.question_number,
            question=ans.question_text,
            generated_answer=ans.generated_answer,
            edited_answer=ans.edited_answer,
            citations=ans.citations,
        )
        for ans in answers
    ]
    return ReviewResponse(questionnaire_id=questionnaire_id, items=items)


@router.patch("/{answer_id}", response_model=EditAnswerResponse)
async def edit_answer(
    answer_id: int,
    payload: EditAnswerRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Edit the answer text for a specific generated answer.
    Sets the edited_answer field which takes priority during export.
    """
    answer = await update_answer(answer_id, user.id, payload.edited_answer, db)
    return EditAnswerResponse(
        answer_id=answer.id,
        question_number=answer.question_number,
        question=answer.question_text,
        generated_answer=answer.generated_answer,
        edited_answer=answer.edited_answer,
        citations=answer.citations,
        updated_at=answer.updated_at,
    )
