import os
import re

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import QuestionnaireAnswer, Questionnaire


NOT_FOUND_ANSWER = "Not found in references."


async def export_questionnaire(
    questionnaire_id: int, user_id: int, session: AsyncSession
) -> str:
    """
    Export all answers for a questionnaire as a Markdown document.

    Uses edited_answer if available, otherwise falls back to generated_answer.
    Includes a coverage summary at the top.

    Returns the relative path to the exported file.
    """
    # Verify questionnaire ownership
    questionnaire = await session.get(Questionnaire, questionnaire_id)
    if questionnaire is None or questionnaire.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Questionnaire not found",
        )

    # Fetch answers ordered by question_number
    result = await session.execute(
        select(QuestionnaireAnswer)
        .where(
            QuestionnaireAnswer.questionnaire_id == questionnaire_id,
            QuestionnaireAnswer.user_id == user_id,
        )
        .order_by(QuestionnaireAnswer.question_number)
    )
    answers = list(result.scalars().all())

    if not answers:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No answers found for this questionnaire. Run /rag/generate first.",
        )

    # Build coverage summary
    total_questions = len(answers)
    answered_with_citations = 0
    not_found_count = 0

    for ans in answers:
        final_answer = ans.edited_answer or ans.generated_answer
        if final_answer.strip() == NOT_FOUND_ANSWER:
            not_found_count += 1
        elif ans.citations:
            answered_with_citations += 1

    # Build Markdown content
    lines: list[str] = []
    lines.append("# Questionnaire Response\n")
    lines.append(f"Total Questions: {total_questions}")
    lines.append(f"Answered With Citations: {answered_with_citations}")
    lines.append(f"Not Found In References: {not_found_count}\n")

    for ans in answers:
        final_answer = ans.edited_answer or ans.generated_answer
        citation_text = format_citations(ans.citations)

        # Remove redundant leading numbers (e.g., '1. ' or '1) ' or '1 ') from the parsed question safely
        clean_question = re.sub(r"^\d+[\.\)\s]\s*", "", ans.question_text)

        lines.append(f"## {ans.question_number}. {clean_question}\n")
        lines.append("Answer:")
        lines.append(f"{final_answer}\n")

        if citation_text:
            lines.append("Citations:")
            lines.append(f"{citation_text}\n")

        lines.append("---\n")

    content = "\n".join(lines)

    # Write to file
    export_dir = os.path.join("exports", str(user_id))
    os.makedirs(export_dir, exist_ok=True)

    file_name = f"questionnaire_{questionnaire_id}.md"
    file_path = os.path.join(export_dir, file_name)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

    return file_path


def format_citations(citations: list[dict]) -> str:
    """
    Convert citation metadata list to readable citation text.

    Groups chunks by file name for cleaner output.

    Examples:
        [Doc: report.pdf - Chunk 2, Chunk 6]
        [Doc: security.pdf - Chunk 4]
    """
    if not citations:
        return ""

    # Group chunks by file_name and use a set to deduplicate
    # (handles cases where the user uploaded the same document multiple times)
    file_chunks: dict[str, set[int]] = {}
    for cit in citations:
        file_name = cit.get("file_name", "unknown")
        chunk_index = cit.get("chunk_index", 0)
        if file_name not in file_chunks:
            file_chunks[file_name] = set()
        file_chunks[file_name].add(chunk_index)

    parts: list[str] = []
    for file_name, chunks in file_chunks.items():
        chunk_labels = ", ".join(f"Chunk {c}" for c in sorted(chunks))
        parts.append(f"[Doc: {file_name} - {chunk_labels}]")

    return "\n".join(parts)
