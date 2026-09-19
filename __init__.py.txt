"""
Generation and Context Engineering module.
Exposes the RAG chain and context formatting utilities.
"""
from src.generation.chain import build_rag_chain
from src.generation.context_builder import format_docs_to_xml
from src.generation.prompts import rag_prompt, SYSTEM_PROMPT

__all__ = [
    "build_rag_chain",
    "format_docs_to_xml",
    "rag_prompt",
    "SYSTEM_PROMPT",
]