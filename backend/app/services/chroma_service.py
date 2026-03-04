import logging
import os

import chromadb
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

CHROMA_PERSIST_DIR: str = os.getenv("CHROMA_PERSIST_DIR", "chroma_data")
COLLECTION_NAME = "reference_chunks"

_client: chromadb.ClientAPI | None = None
_collection: chromadb.Collection | None = None


def init_chroma() -> chromadb.Collection:
    """
    Initialize the persistent ChromaDB client and get/create the collection.
    Called once at application startup.
    """
    global _client, _collection
    _client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
    _collection = _client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "l2"},
    )
    logger.info(
        f"ChromaDB initialized: collection='{COLLECTION_NAME}', "
        f"persist_dir='{CHROMA_PERSIST_DIR}', "
        f"existing_count={_collection.count()}"
    )
    return _collection


def get_collection() -> chromadb.Collection:
    """Return the initialized collection. Raises if not initialized."""
    if _collection is None:
        raise RuntimeError(
            "ChromaDB collection not initialized. Call init_chroma() first."
        )
    return _collection


def add_chunks(
    user_id: int,
    reference_document_id: int,
    file_name: str,
    chunks: list[str],
    embeddings: list[list[float]],
) -> int:
    """
    Add document chunks to ChromaDB with metadata.

    Uses deterministic IDs: '{user_id}_{doc_id}_{chunk_index}'
    enabling idempotent re-indexing.

    Returns the number of chunks added.
    """
    collection = get_collection()

    ids = [f"{user_id}_{reference_document_id}_{i}" for i in range(len(chunks))]
    metadatas = [
        {
            "user_id": user_id,
            "reference_document_id": reference_document_id,
            "chunk_index": i,
            "file_name": file_name,
        }
        for i in range(len(chunks))
    ]

    collection.upsert(
        ids=ids,
        embeddings=embeddings,
        documents=chunks,
        metadatas=metadatas,
    )

    logger.info(
        f"Added {len(chunks)} chunks for user={user_id}, doc={reference_document_id}"
    )
    return len(chunks)


def query_chunks(
    query_embedding: list[float],
    user_id: int,
    top_k: int = 5,
) -> dict:
    """
    Query ChromaDB for similar chunks filtered by user_id.

    Returns raw Chroma results dict with keys:
    'ids', 'documents', 'metadatas', 'distances'.
    """
    collection = get_collection()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        where={"user_id": user_id},
        include=["documents", "metadatas", "distances"],
    )

    return results
