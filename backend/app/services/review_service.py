from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import QuestionnaireAnswer, Questionnaire


async def get_answers_for_questionnaire(
    questionnaire_id: int, user_id: int, session: AsyncSession
) -> list[QuestionnaireAnswer]:
    """
    Fetch all answers for a questionnaire, ordered by question_number.

    Verifies questionnaire ownership before returning results.
    """
    # Verify questionnaire exists and belongs to user
    questionnaire = await session.get(Questionnaire, questionnaire_id)
    if questionnaire is None or questionnaire.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Questionnaire not found",
        )

    result = await session.execute(
        select(QuestionnaireAnswer)
        .where(
            QuestionnaireAnswer.questionnaire_id == questionnaire_id,
            QuestionnaireAnswer.user_id == user_id,
        )
        .order_by(QuestionnaireAnswer.question_number)
    )
    return list(result.scalars().all())


async def update_answer(
    answer_id: int, user_id: int, edited_answer: str, session: AsyncSession
) -> QuestionnaireAnswer:
    """
    Update the edited_answer field of a specific answer.

    Verifies answer ownership before updating.
    """
    answer = await session.get(QuestionnaireAnswer, answer_id)
    if answer is None or answer.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Answer not found",
        )

    answer.edited_answer = edited_answer
    answer.updated_at = datetime.now(timezone.utc)
    await session.commit()
    await session.refresh(answer)
    return answer
