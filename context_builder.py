from typing import List
from langchain_core.documents import Document

def format_docs_to_xml(docs: List[Document]) -> str:
    """
    Context Engineering step:
    - Strips whitespace
    - Extracts IDs and sources from metadata
    - Formats into clean, parsable XML tags
    """
    if not docs:
        return "<empty_context>No matching documents found.</empty_context>"

    formatted_blocks = []
    seen_texts = set()

    for idx, doc in enumerate(docs, start=1):
        clean_text = " ".join(doc.page_content.split())
        
        # Deduplication check
        if clean_text in seen_texts:
            continue
        seen_texts.add(clean_text)

        doc_id = doc.metadata.get("id", f"doc_{idx}")
        source = doc.metadata.get("source", "knowledge_base.json")
        
        formatted_blocks.append(
            f'<document id="{doc_id}" source="{source}">\n{clean_text}\n</document>'
        )

    return "\n\n".join(formatted_blocks)