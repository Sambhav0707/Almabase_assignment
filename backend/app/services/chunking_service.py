import re


def chunk_text(
    text: str,
    chunk_size: int = 800,
    overlap: int = 150,
    min_chunk_size: int = 50,
) -> list[str]:
    """
    Split text into overlapping chunks with sentence-boundary awareness.

    Args:
        text: The full document text.
        chunk_size: Target size per chunk in characters.
        overlap: Number of overlapping characters between consecutive chunks.
        min_chunk_size: Discard chunks shorter than this.

    Returns:
        List of text chunks.
    """
    if not text or not text.strip():
        return []

    # Collapse excessive whitespace
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = text.strip()

    if len(text) <= chunk_size:
        return [text] if len(text) >= min_chunk_size else []

    chunks: list[str] = []
    start = 0
    text_len = len(text)

    while start < text_len:
        end = start + chunk_size

        if end >= text_len:
            # Last chunk — take everything remaining
            chunk = text[start:].strip()
            if len(chunk) >= min_chunk_size:
                chunks.append(chunk)
            break

        # Find the last sentence boundary within the window
        boundary = _find_sentence_boundary(text, start, end)
        if boundary > start:
            chunk = text[start:boundary].strip()
        else:
            # No sentence boundary found — hard cut at chunk_size
            chunk = text[start:end].strip()
            boundary = end

        if len(chunk) >= min_chunk_size:
            chunks.append(chunk)

        # Advance with overlap
        start = boundary - overlap
        if start < 0:
            start = 0
        # Avoid infinite loop if boundary didn't advance
        if start >= boundary:
            start = boundary

    return chunks


def _find_sentence_boundary(text: str, start: int, end: int) -> int:
    """
    Find the position just after the last sentence-ending punctuation
    (. ! ?) followed by whitespace within text[start:end].

    Returns `start` if no boundary is found.
    """
    search_region = text[start:end]

    # Find last sentence-ending punctuation followed by space or newline
    best = -1
    for match in re.finditer(r"[.!?]\s", search_region):
        best = match.end()

    if best == -1:
        return start  # No boundary found

    return start + best
