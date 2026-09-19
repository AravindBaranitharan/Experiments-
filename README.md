# Experiments - RAG knowledge-base chatbot

Answers questions about AI/GenAI, DevOps and AWS strictly from our knowledge base.

```
question -> input guardrail -> semantic search (Chroma) -> grounding gate -> LLM -> output guardrail -> answer
```

## Layout

| Path | What it is |
|---|---|
| `data/knowledge_base_v1/` | The knowledge base (JSON, one topic per file) |
| `src/knowledge_base/` | Loader + validator (normalises and de-duplicates entries) |
| `src/retrieval/` | Chunking, embeddings, Chroma store, semantic search (`retriever.py`) |
| `src/guardrails/` | Input/output guardrails for the chain (`guardrail.py` is the earlier DevOps-agent one, unused) |
| `src/generation/` | System prompt, context builder, LLM factory, the RAG chain |
| `src/config.py` | All settings, read from environment / `.env` |
| `src/cli.py` | Command-line chatbot |
| `tests/` | `pytest` suite (runs offline; no API key needed) |
| `docs/` | Notes for the knowledge base and the original guardrail |

## Setup

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env            # then add your OPENAI_API_KEY (and OPENAI_BASE_URL if you use a gateway)
python -m src.retrieval.ingest  # build the Chroma store (first run downloads a ~80 MB local embedding model)
```

`.env` is git-ignored. Never commit keys.

## Use

```bash
python -m src.retrieval.search "how do I store files in the cloud?"   # semantic search only, no LLM
python -m src.cli "What is Amazon S3?"                                # full chatbot (needs the API key)
python -m src.cli                                                     # interactive
python -m pytest
```

## How the guardrails work

- **Input:** blocks prompt injection, credentials/secrets and harmful requests; masks emails, SSNs and card numbers.
- **Scope:** decided by retrieval, not keywords. If nothing in the knowledge base is similar enough (`MIN_SCORE`), the bot refuses **without calling the LLM**.
- **Output:** redacts secrets, replaces answers that repeat the system prompt, removes citations of documents that were not retrieved.

Regex-based injection detection cannot be complete (e.g. an on-topic question with an injected instruction in another language can still reach the model). The system prompt and output guard are the backstop.
