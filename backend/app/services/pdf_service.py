import logging
from pypdf import PdfReader

logger = logging.getLogger(__name__)


def extract_text(file_path: str) -> str:
    """
    Extract full text from a PDF file using pypdf.
    Returns cleaned text with preserved paragraph boundaries.
    Returns empty string for scanned/image-only PDFs.
    """
    try:
        reader = PdfReader(file_path)
    except Exception as e:
        logger.warning(f"Failed to read PDF {file_path}: {e}")
        return ""

    pages_text: list[str] = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            pages_text.append(text.strip())

    full_text = "\n\n".join(pages_text)

    # Clean excessive whitespace while preserving paragraph breaks
    lines = full_text.splitlines()
    cleaned_lines: list[str] = []
    for line in lines:
        stripped = " ".join(line.split())  # collapse inline whitespace
        if stripped:
            cleaned_lines.append(stripped)

    return "\n".join(cleaned_lines)


def parse_questions(file_path: str) -> list[str]:
    """
    Extract questions from a questionnaire PDF.

    Heuristic:
    - Lines ending with '?' are treated as questions.
    - Numbered lines (e.g., '1.', '2)', '3 ') with substantial content
      are treated as questions even without '?'.
    - Multi-line questions are merged until a terminator is found.
    """
    raw_text = extract_text(file_path)
    if not raw_text:
        return []

    lines = raw_text.splitlines()
    questions: list[str] = []
    buffer: list[str] = []

    for line in lines:
        stripped = line.strip()
        if not stripped:
            # Flush buffer on empty line
            if buffer:
                merged = " ".join(buffer)
                if _is_question(merged):
                    questions.append(merged)
                buffer = []
            continue

        # Check if this line starts a new numbered item
        if _is_numbered_start(stripped) and buffer:
            merged = " ".join(buffer)
            if _is_question(merged):
                questions.append(merged)
            buffer = [stripped]
        else:
            buffer.append(stripped)

        # If line ends with '?', flush as question immediately
        if stripped.endswith("?"):
            merged = " ".join(buffer)
            questions.append(merged)
            buffer = []

    # Flush remaining buffer
    if buffer:
        merged = " ".join(buffer)
        if _is_question(merged):
            questions.append(merged)

    return questions


def _is_question(text: str) -> bool:
    """Check if text looks like a question."""
    if text.endswith("?"):
        return True
    # Numbered line with substantial content (>10 chars after number)
    if _is_numbered_start(text) and len(text) > 15:
        return True
    return False


def _is_numbered_start(text: str) -> bool:
    """Check if text starts with a number followed by . or ) or space."""
    import re

    return bool(re.match(r"^\d+[\.\)\s]\s*", text))
