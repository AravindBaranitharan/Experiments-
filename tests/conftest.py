import os

# The suite must never call a real LLM: keep the re-ranker and verifier off unless a test injects its own.
os.environ["RERANKER"] = "none"
os.environ["VERIFY_ANSWERS"] = "false"

import dataclasses

import pytest
from langchain_core.embeddings import DeterministicFakeEmbedding

from src.config import get_settings
from src.retrieval.ingest import ingest
from src.retrieval.vector_store import get_vectorstore


@pytest.fixture(scope="session")
def fake_store(tmp_path_factory):
    """A real Chroma store built with deterministic (non-semantic) embeddings: tests mechanics, not meaning."""
    settings = dataclasses.replace(get_settings(), chroma_dir=tmp_path_factory.mktemp("fake") / "chroma")
    embeddings = DeterministicFakeEmbedding(size=64)
    ingest(settings, embeddings)
    return get_vectorstore(settings, embeddings)
