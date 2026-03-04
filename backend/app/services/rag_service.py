import logging
import os

from dotenv import load_dotenv
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import ReferenceDocument, Questionnaire, QuestionnaireAnswer
from app.services.pdf_service import extract_text, parse_questions
from app.services.chunking_service import chunk_text
from app.services.embedding_service import embed_texts, embed_query, generate_answer
from app.services.chroma_service import add_chunks, query_chunks

load_dotenv()

logger = logging.getLogger(__name__)

SIMILARITY_THRESHOLD: float = float(os.getenv("SIMILARITY_THRESHOLD", "1.5"))
MAX_CONTEXT_CHARS: int = int(os.getenv("MAX_CONTEXT_CHARS", "4000"))

PROMPT_TEMPLATE = """You are a precise document analyst. Answer the question using ONLY the provided context.

RULES:
- Use ONLY information found in the context below.
- Do NOT use any external or prior knowledge.
- If the answer is not present in the context, respond exactly: "Not found in references."
- Cite your sources EXACTLY using the labels provided. For example: [Doc: security_policy.pdf - Chunk 1, Chunk 2].
- Be concise and factual.

CONTEXT:
---
{context}
---

QUESTION:
{question}

ANSWER:
"""


# ── Index Pipeline ───────────────────────────────────────────


async def index_reference_document(
    doc_id: int, user_id: int, session: AsyncSession
) -> None:
    """
    Extract, chunk, embed, store, and mark a single document as processed.
    Includes transaction safety and lock checks.
    """
    # Fetch the document ensuring user isolation
    doc = await session.get(ReferenceDocument, doc_id)
    if not doc or doc.user_id != user_id:
        raise ValueError("Document not found or unauthorized")

    # Early exit if already processed to prevent duplicate processing on concurrent uploads
    if doc.processed:
        logger.info(f"Document '{doc.file_name}' (id={doc.id}) already processed.")
        return

    try:
        # 1. Extract text
        text = extract_text(doc.storage_key)
        if not text.strip():
            raise ValueError(f"No extractable text in '{doc.file_name}'")

        # 2. Chunk
        chunks = chunk_text(text)
        if not chunks:
            raise ValueError(f"No chunks produced from '{doc.file_name}'")

        logger.info(f"Document '{doc.file_name}': {len(chunks)} chunks created")

        # 3. Embed all chunks
        embeddings = await embed_texts(chunks)

        # 4. Store in ChromaDB
        add_chunks(
            user_id=user_id,
            reference_document_id=doc.id,
            file_name=doc.file_name,
            chunks=chunks,
            embeddings=embeddings,
        )

        # 5. Mark as processed in PostgreSQL using transaction safety
        doc.processed = True
        await session.commit()

        logger.info(f"Document '{doc.file_name}' (id={doc.id}) indexed successfully")

    except Exception as e:
        await session.rollback()
        logger.error(f"Failed to index '{doc.file_name}' (id={doc.id}): {str(e)}")
        raise


# ── Generate Pipeline ────────────────────────────────────────


async def generate_answers(
    questionnaire_id: int, user_id: int, session: AsyncSession
) -> dict:
    """
    Generate answers for all questions in a questionnaire using RAG.

    Pipeline per question: embed → retrieve → threshold check → prompt → generate.

    Returns structured response with questions, answers, and citations.
    """
    # 1. Load questionnaire (user-isolated)
    result = await session.execute(
        select(Questionnaire).where(
            Questionnaire.id == questionnaire_id,
            Questionnaire.user_id == user_id,
        )
    )
    questionnaire = result.scalar_one_or_none()

    if questionnaire is None:
        from fastapi import HTTPException, status

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Questionnaire not found",
        )

    # 2. Parse questions from PDF
    questions = parse_questions(questionnaire.storage_key)
    if not questions:
        from fastapi import HTTPException, status

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No questions found in questionnaire",
        )

    logger.info(
        f"Parsed {len(questions)} questions from questionnaire {questionnaire_id}"
    )

    # 3. Process each question
    results: list[dict] = []
    for i, question in enumerate(questions):
        try:
            answer_item = await _answer_single_question(question, user_id, i + 1)
            results.append(answer_item)
        except Exception as e:
            logger.error(f"Error generating answer for Q{i+1}: {e}")
            results.append(
                {
                    "question_number": i + 1,
                    "question": question,
                    "answer": "Error generating answer.",
                    "citations": [],
                }
            )

    # 4. Persist answers in the database
    # Clear old answers for this questionnaire to prevent duplicates if generated multiple times
    await session.execute(
        delete(QuestionnaireAnswer).where(
            QuestionnaireAnswer.questionnaire_id == questionnaire_id
        )
    )
    await session.commit()

    for item in results:
        answer_row = QuestionnaireAnswer(
            questionnaire_id=questionnaire_id,
            user_id=user_id,
            question_number=item["question_number"],
            question_text=item["question"],
            generated_answer=item["answer"],
            citations=item["citations"],
        )
        session.add(answer_row)
    await session.commit()

    return {
        "questionnaire_id": questionnaire_id,
        "answers_generated": len(results),
        "results": results,
    }


async def _answer_single_question(
    question: str, user_id: int, question_number: int
) -> dict:
    """Embed question, retrieve relevant chunks, build prompt, and generate answer."""

    # 1. Embed the question
    query_vec = await embed_query(question)

    # 2. Retrieve from Chroma (user-filtered)
    results = query_chunks(query_vec, user_id, top_k=5)

    distances = results["distances"][0] if results["distances"] else []
    documents = results["documents"][0] if results["documents"] else []
    metadatas = results["metadatas"][0] if results["metadatas"] else []

    # Log distances for threshold tuning
    logger.info(f"Q{question_number} distances: {distances}")

    # 3. Filter by similarity threshold
    relevant: list[tuple[str, dict, float]] = [
        (doc, meta, dist)
        for doc, meta, dist in zip(documents, metadatas, distances)
        if dist <= SIMILARITY_THRESHOLD
    ]

    # 4. No relevant chunks → not found
    if not relevant:
        return {
            "question_number": question_number,
            "question": question,
            "answer": "Not found in references.",
            "citations": [],
        }

    # 5. Build context with budget cap
    context_parts: list[str] = []
    citations: list[dict] = []
    total_chars = 0

    for idx, (doc_text, meta, dist) in enumerate(relevant, 1):
        if total_chars + len(doc_text) > MAX_CONTEXT_CHARS:
            break
        label = f"Source: [Doc: {meta['file_name']} - Chunk {meta['chunk_index']}]"
        context_parts.append(f"{label}\n{doc_text}")
        citations.append(
            {
                "file_name": meta["file_name"],
                "chunk_index": meta["chunk_index"],
                "reference_document_id": meta["reference_document_id"],
            }
        )
        total_chars += len(doc_text)

    context = "\n\n".join(context_parts)

    # 6. Build prompt and generate
    prompt = PROMPT_TEMPLATE.format(context=context, question=question)
    answer = await generate_answer(prompt)

    return {
        "question_number": question_number,
        "question": question,
        "answer": answer.strip(),
        "citations": citations,
    }
