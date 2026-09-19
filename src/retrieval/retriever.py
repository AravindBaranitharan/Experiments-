"""
Semantic search over the Chroma knowledge base.

The query is embedded with the same model used at ingestion time, then the
nearest chunks (by cosine similarity) are returned with their scores.
"""

from dataclasses import dataclass
from functools import lru_cache

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_core.runnables import Runnable, RunnableLambda

from src.config import Settings, get_settings
from src.retrieval.embeddings import embedding_label
from src.retrieval.vector_store import get_vectorstore


@dataclass(frozen=True)
class SearchResult:
    document: Document
    score: float  # cosine similarity, 0-1 (higher is more similar)


def load_store(settings: Settings | None = None, embeddings: Embeddings | None = None) -> Chroma:
    """Open the persisted store, failing clearly if it is missing or was built with another model."""
    settings = settings or get_settings()
    store = get_vectorstore(settings, embeddings)

    if store._collection.count() == 0:
        raise RuntimeError("The vector store is empty. Build it first with: python -m src.retrieval.ingest")

    built_with = (store._collection.metadata or {}).get("embedding_model")
    current = embedding_label(settings)
    if built_with and built_with != current:
        raise RuntimeError(
            f"The store was built with '{built_with}' but the current setting is '{current}'. "
            "Re-run: python -m src.retrieval.ingest"
        )
    return store


@lru_cache(maxsize=1)
def _default_store() -> Chroma:
    return load_store()


def search(
    query: str,
    k: int | None = None,
    category: str | None = None,
    min_score: float | None = None,
    settings: Settings | None = None,
    store: Chroma | None = None,
) -> list[SearchResult]:
    """
    Return up to `k` chunks most similar to `query`, best first.

    category  - only search chunks in this category (e.g. "AWS Cloud")
    min_score - drop chunks scoring below this cosine similarity
    Defaults for k and min_score come from settings (TOP_K, MIN_SCORE).
    """
    use_cached_store = store is None and settings is None
    settings = settings or get_settings()
    k = settings.top_k if k is None else k
    min_score = settings.min_score if min_score is None else min_score

    if k < 1:
        raise ValueError("k must be at least 1")
    if not query or not query.strip():
        return []

    if store is None:
        store = _default_store() if use_cached_store else load_store(settings)

    hits = store.similarity_search_with_score(
        query.strip(),
        k=k,
        filter={"category": category} if category else None,
    )

    results = []
    for document, distance in hits:
        score = round(1.0 - distance, 4)  # the collection uses cosine distance
        if score >= min_score:
            results.append(SearchResult(Document(page_content=document.page_content,
                                                 metadata={**document.metadata, "score": score}), score))
    return results


def get_retriever(
    k: int | None = None,
    category: str | None = None,
    min_score: float | None = None,
    settings: Settings | None = None,
    store: Chroma | None = None,
) -> Runnable:
    """
    A LangChain runnable: query string -> list[Document] (each with metadata["score"]).
    Drop-in for `retriever | format_docs_to_xml` in the generation chain.
    """
    def _retrieve(query: str) -> list[Document]:
        return [r.document for r in search(query, k, category, min_score, settings, store)]

    return RunnableLambda(_retrieve, name="kb_retriever")
