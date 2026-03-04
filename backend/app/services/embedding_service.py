import logging
import os

import httpx
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_BASE_URL: str = os.getenv(
    "OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"
)
OPENROUTER_MODEL: str = os.getenv("OPENROUTER_MODEL", "deepseek/deepseek-chat")
OPENROUTER_EMBED_MODEL: str = os.getenv(
    "OPENROUTER_EMBED_MODEL", "openai/text-embedding-3-small"
)


def _headers() -> dict[str, str]:
    """Common headers for all OpenRouter API requests."""
    return {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://questionnaire-rag-tool.com",
        "X-Title": "Questionnaire RAG Tool",
    }


# ── Embeddings ───────────────────────────────────────────────


async def embed_texts(texts: list[str]) -> list[list[float]]:
    """
    Generate embeddings for a list of texts using OpenRouter.

    Returns a list of embedding vectors (one per input text).
    Raises HTTPException(503) if the service is unreachable.
    """
    from fastapi import HTTPException, status

    logger.info(
        f"Sending {len(texts)} text(s) to OpenRouter for embedding "
        f"(model={OPENROUTER_EMBED_MODEL})"
    )

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{OPENROUTER_BASE_URL}/embeddings",
                headers=_headers(),
                json={
                    "model": OPENROUTER_EMBED_MODEL,
                    "input": texts,
                },
            )
            response.raise_for_status()
    except (httpx.ConnectError, httpx.TimeoutException):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="LLM service unavailable",
        )
    except httpx.HTTPStatusError as e:
        logger.error(
            f"OpenRouter embedding error: {e.response.status_code} {e.response.text}"
        )
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Embedding model error: {e.response.text[:200]}",
        )

    data = response.json()
    logger.info("Received embedding response from OpenRouter")
    return [item["embedding"] for item in data["data"]]


async def embed_query(text: str) -> list[float]:
    """Generate embedding for a single query text."""
    embeddings = await embed_texts([text])
    return embeddings[0]


# ── Generation ───────────────────────────────────────────────


async def generate_answer(prompt: str) -> str:
    """
    Generate a text response from OpenRouter given a prompt.

    Returns the generated text.
    """
    from fastapi import HTTPException, status

    logger.info(f"Sending prompt to OpenRouter (model={OPENROUTER_MODEL})")

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{OPENROUTER_BASE_URL}/chat/completions",
                headers=_headers(),
                json={
                    "model": OPENROUTER_MODEL,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.2,
                },
            )
            response.raise_for_status()
    except (httpx.ConnectError, httpx.TimeoutException):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="LLM service unavailable",
        )
    except httpx.HTTPStatusError as e:
        logger.error(
            f"OpenRouter generate error: {e.response.status_code} {e.response.text}"
        )
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Generation model error: {e.response.text[:200]}",
        )

    data = response.json()
    logger.info("Received response from OpenRouter")
    return data["choices"][0]["message"]["content"]
