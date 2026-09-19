"""Central configuration, read from environment variables (and .env if present)."""

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parents[1]

load_dotenv(ROOT_DIR / ".env")


def _int(name: str, default: int) -> int:
    return int(os.getenv(name, default))


def _float(name: str, default: float) -> float:
    return float(os.getenv(name, default))


@dataclass(frozen=True)
class Settings:
    data_dir: Path = ROOT_DIR / "data" / "knowledge_base_v1"

    # Chunking
    chunk_size: int = field(default_factory=lambda: _int("CHUNK_SIZE", 500))
    chunk_overlap: int = field(default_factory=lambda: _int("CHUNK_OVERLAP", 60))

    # Embeddings: "local" (no key) or "openai" (OpenAI-compatible endpoint)
    embedding_provider: str = field(default_factory=lambda: os.getenv("EMBEDDING_PROVIDER", "local"))
    embedding_model: str = field(default_factory=lambda: os.getenv("EMBEDDING_MODEL", "text-embedding-3-small"))

    # OpenAI-compatible endpoint (embeddings if provider=openai, and the LLM)
    openai_api_key: str = field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))
    openai_base_url: str = field(default_factory=lambda: os.getenv("OPENAI_BASE_URL", ""))
    llm_model: str = field(default_factory=lambda: os.getenv("LLM_MODEL", "gpt-4o-mini"))

    # Chroma
    chroma_dir: Path = field(default_factory=lambda: ROOT_DIR / os.getenv("CHROMA_DIR", "chroma_db"))
    chroma_collection: str = field(default_factory=lambda: os.getenv("CHROMA_COLLECTION", "knowledge_base"))

    # Semantic search. min_score is cosine similarity (0-1); 0.30 is calibrated for the local
    # MiniLM model (in-scope questions score >= 0.50, off-topic <= 0.20). Re-check it if you
    # switch embedding models.
    top_k: int = field(default_factory=lambda: _int("TOP_K", 4))
    min_score: float = field(default_factory=lambda: _float("MIN_SCORE", 0.30))


def get_settings() -> Settings:
    return Settings()
