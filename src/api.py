"""
HTTP API for the web UI.

    uvicorn src.api:app --port 8000

GET  /api/health
POST /api/chat   {"question": "..."}  ->  {"status", "answer", "sources", "reason"}

status: "answered" | "refused" (nothing relevant in the knowledge base) | "blocked" (input guardrail)
"""

import logging
import re
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from src.config import get_settings
from src.generation.chain import build_rag_chain
from src.generation.prompts import NO_ANSWER
from src.guardrails import GuardrailViolation
from src.guardrails.input_guards import MAX_INPUT_CHARS
from src.knowledge_base import KnowledgeBaseLoader

logger = logging.getLogger("rag.api")

_CITATION = re.compile(r"\[((?:[a-z0-9]+-)+\d{3})\]", re.IGNORECASE)


class ChatRequest(BaseModel):
    # Sizes are enforced by the input guardrail (which explains itself); this only bounds the payload.
    question: str = Field(max_length=MAX_INPUT_CHARS * 4)


class SourceLink(BaseModel):
    title: str
    url: str


class Source(BaseModel):
    id: str
    topic: str
    category: str
    links: list[SourceLink]


class ChatResponse(BaseModel):
    status: str
    answer: str
    sources: list[Source] = []
    reason: str | None = None


def _links(entry: dict) -> list[SourceLink]:
    links = [SourceLink(title=e.get("title") or e["url"], url=e["url"])
             for e in entry.get("official_evidence", []) if isinstance(e, dict) and e.get("url")]
    links += [SourceLink(title=url, url=url) for url in entry.get("official_links", [])]
    return links


def cited_sources(answer: str, entries: dict[str, dict]) -> list[Source]:
    """The knowledge-base entries the answer cites, in order of first appearance."""
    sources, seen = [], set()
    for match in _CITATION.finditer(answer):
        entry_id = match.group(1).lower()
        if entry_id in entries and entry_id not in seen:
            seen.add(entry_id)
            entry = entries[entry_id]
            sources.append(Source(id=entry["id"], topic=entry["topic"], category=entry["category"], links=_links(entry)))
    return sources


def create_app(chain=None) -> FastAPI:
    """`chain` can be injected (tests); by default the real RAG chain is built at startup."""
    state: dict = {}

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        entries = KnowledgeBaseLoader(get_settings().data_dir).load_entries().entries
        state["entries"] = {e["id"].lower(): e for e in entries}
        state["chain"] = chain or build_rag_chain()
        yield

    app = FastAPI(title="Knowledge Assistant API", lifespan=lifespan)

    @app.get("/api/health")
    def health():
        return {"status": "ok", "entries": len(state["entries"]), "llm_model": get_settings().llm_model}

    @app.post("/api/chat", response_model=ChatResponse)
    def chat(request: ChatRequest):
        try:
            answer = state["chain"].invoke(request.question)
        except GuardrailViolation as blocked:
            return ChatResponse(status="blocked", answer="", reason=blocked.reason)
        except Exception:
            logger.exception("Chat request failed")
            raise HTTPException(status_code=502, detail="The assistant could not complete the request. Please try again.")

        if answer.strip() == NO_ANSWER:
            return ChatResponse(status="refused", answer=answer)
        return ChatResponse(status="answered", answer=answer, sources=cited_sources(answer, state["entries"]))

    return app


app = create_app()
