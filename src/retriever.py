"""Ephemeral, session-isolated Chroma vector store and retriever for ClinicDocs AI.

Features:
- Ephemeral in-memory Chroma client (chromadb.EphemeralClient())
- Isolated collections per session: 'session_{session_id}'
- Explicit cosine distance space: metadata={'hnsw:space': 'cosine'}
- Cosine distance to similarity conversion: similarity = 1.0 - distance
- LRU collection eviction cap to protect memory on Streamlit Community Cloud
- Explicit collection cleanup on 'Clear Chat' / session reset
- Pre-LLM threshold gating to reject out-of-domain queries without LLM invocation
"""

from collections import OrderedDict
import time
from typing import Dict, List, Optional, Tuple

import chromadb
from chromadb.api import ClientAPI
from langchain_chroma import Chroma
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
from langchain_core.documents import Document

from src.config import config, logger

REFUSAL_MESSAGE = "I couldn't find this in the uploaded documents."

# -----------------------------------------------------------------------------
# Ephemeral Chroma Client & Shared FastEmbed Embedder
# -----------------------------------------------------------------------------
# Module-level ephemeral client (lives in process memory, no disk persistence)
_chroma_client: ClientAPI = chromadb.EphemeralClient()

# Shared embedding model instance
_embedder_instance: Optional[FastEmbedEmbeddings] = None


def get_embedder() -> FastEmbedEmbeddings:
    """Get or create singleton FastEmbed embeddings instance."""
    global _embedder_instance
    if _embedder_instance is None:
        logger.info(f"Initializing FastEmbed embeddings: {config.embedding_model_name}")
        _embedder_instance = FastEmbedEmbeddings(model_name=config.embedding_model_name)
    return _embedder_instance


# -----------------------------------------------------------------------------
# Session Collection Registry & LRU Eviction Cap
# -----------------------------------------------------------------------------
# Keeps track of active collections and their last access timestamps: session_id -> timestamp
_active_collections: OrderedDict[str, float] = OrderedDict()


def _enforce_collection_cap(max_collections: int) -> None:
    """Evict oldest collections if live count exceeds max_collections."""
    while len(_active_collections) > max_collections:
        oldest_session_id, _ = _active_collections.popitem(last=False)
        collection_name = f"session_{oldest_session_id}"
        try:
            _chroma_client.delete_collection(collection_name)
            logger.info(f"LRU Eviction: Deleted oldest collection '{collection_name}'")
        except Exception as e:
            logger.warning(f"Error during LRU eviction of '{collection_name}': {e}")


def get_session_collection_name(session_id: str) -> str:
    """Format safe Chroma collection name for a session."""
    clean_id = "".join(c for c in session_id if c.isalnum() or c in ("_", "-"))
    return f"session_{clean_id}"


def get_session_vector_store(session_id: str) -> Chroma:
    """Get or create the Chroma vector store for a specific session.
    
    Guarantees:
    - Cosine distance metric explicitly set (hnsw:space = cosine)
    - Session isolation: each session has a separate collection
    - LRU tracking updated
    """
    collection_name = get_session_collection_name(session_id)
    embedder = get_embedder()

    # Update LRU access record
    if session_id in _active_collections:
        _active_collections.move_to_end(session_id)
    _active_collections[session_id] = time.time()
    _enforce_collection_cap(config.max_active_collections)

    vector_store = Chroma(
        client=_chroma_client,
        collection_name=collection_name,
        embedding_function=embedder,
        collection_metadata={"hnsw:space": "cosine"},
    )
    return vector_store


def delete_session_collection(session_id: str) -> bool:
    """Explicitly delete a session's Chroma collection on Clear Chat or reset.
    
    Returns:
        bool: True if successfully deleted, False otherwise.
    """
    collection_name = get_session_collection_name(session_id)
    try:
        _chroma_client.delete_collection(collection_name)
        if session_id in _active_collections:
            del _active_collections[session_id]
        logger.info(f"Explicit cleanup: Deleted collection '{collection_name}' for session '{session_id}'")
        return True
    except Exception as e:
        logger.warning(f"Collection '{collection_name}' could not be deleted (might not exist): {e}")
        if session_id in _active_collections:
            del _active_collections[session_id]
        return False


def get_active_collection_count() -> int:
    """Return count of currently registered active collections."""
    return len(_active_collections)


# -----------------------------------------------------------------------------
# Distance to Similarity Conversion & Retrieval
# -----------------------------------------------------------------------------
def distance_to_similarity(distance: float) -> float:
    """Convert Chroma cosine distance to similarity score.
    
    Chroma uses cosine distance: d = 1 - cosine_similarity.
    Therefore: cosine_similarity = 1 - d.
    For normalized embeddings:
    - distance 0.0 -> similarity 1.0 (identical vectors)
    - distance 1.0 -> similarity 0.0 (orthogonal vectors)
    - distance 2.0 -> similarity -1.0 (opposite vectors)
    """
    return 1.0 - distance


def index_documents(session_id: str, documents: List[Document]) -> int:
    """Index chunked documents into the session's vector store.
    
    Returns:
        int: Number of chunks added.
    """
    if not documents:
        return 0
    store = get_session_vector_store(session_id)
    store.add_documents(documents)
    logger.info(f"Indexed {len(documents)} chunks into session '{session_id}'")
    return len(documents)


def retrieve_with_scores(
    session_id: str,
    query: str,
    k: Optional[int] = None,
) -> List[Tuple[Document, float]]:
    """Retrieve top-k documents with cosine similarity scores.
    
    Returns:
        List[Tuple[Document, float]]: Pairs of (Document, similarity_score) sorted descending.
    """
    top_k = k or config.retriever_k
    store = get_session_vector_store(session_id)

    # similarity_search_with_score returns (Document, distance)
    results = store.similarity_search_with_score(query, k=top_k)

    scored_docs: List[Tuple[Document, float]] = []
    for doc, dist in results:
        sim = distance_to_similarity(dist)
        scored_docs.append((doc, sim))

    # Sort descending by similarity
    scored_docs.sort(key=lambda x: x[1], reverse=True)
    return scored_docs


def check_relevance_gate(
    scored_docs: List[Tuple[Document, float]],
    threshold: Optional[float] = None,
) -> Tuple[bool, float]:
    """Check if the top retrieved chunk meets the similarity threshold.
    
    Returns:
        Tuple[bool, float]: (is_relevant, top_similarity_score)
        If is_relevant is False, the query is refused before calling the LLM.
    """
    thresh = threshold if threshold is not None else config.similarity_threshold
    if not scored_docs:
        return False, 0.0

    top_score = scored_docs[0][1]
    is_relevant = top_score >= thresh

    if not is_relevant:
        logger.info(f"Relevance Gate REFUSAL: top score {top_score:.4f} < threshold {thresh:.4f}")
    else:
        logger.info(f"Relevance Gate PASSED: top score {top_score:.4f} >= threshold {thresh:.4f}")

    return is_relevant, top_score
