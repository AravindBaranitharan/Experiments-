from operator import itemgetter

from langchain_core.language_models import BaseChatModel
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import Runnable, RunnableBranch, RunnableLambda, RunnablePassthrough

from src.generation.context_builder import format_docs_to_xml
from src.generation.formatting import clean_answer
from src.generation.llm import get_llm
from src.generation.prompts import NO_ANSWER, SYSTEM_PROMPT, rag_prompt
from src.generation.verify import AnswerVerifier, get_verifier
from src.guardrails.input_guards import validate_input
from src.guardrails.output_guards import validate_output
from src.retrieval.retriever import get_retriever


def build_rag_pipeline(
    llm: BaseChatModel | Runnable | None = None,
    retriever: Runnable | None = None,
    verifier: AnswerVerifier | None = None,
) -> Runnable:
    """
    question (str) -> {"question", "docs", "answer", "verification"}

    1. Input guardrail   - raises GuardrailViolation if the question is blocked
    2. Retrieval         - vector search, chunks merged into entries, LLM re-ranking
    3. Grounding gate    - nothing relevant retrieved -> refuse without calling the LLM
    4. Generation        - system prompt + context + LLM
    5. Verification      - audit the draft against the documents; rewrite it if it makes unsupported claims
    6. Output guardrail  - redact secrets, block prompt leaks, drop fabricated citations

    `docs` are the entries the model was given (with relevance metadata); `answer` is the final reply;
    `verification` is "passed", "revised", "unverified" or "skipped".
    `llm`, `retriever` and `verifier` default to the configured ones; pass your own to test or swap them.
    """
    retriever = retriever or get_retriever()
    llm = llm or get_llm()
    verifier = verifier or get_verifier()

    generate = (
        RunnableLambda(lambda state: {"context": format_docs_to_xml(state["docs"]), "question": state["question"]})
        | rag_prompt
        | llm
        | StrOutputParser()
        | RunnableLambda(clean_answer)
    )

    answer = RunnableBranch(
        (lambda state: not state["docs"], RunnableLambda(lambda state: NO_ANSWER)),
        generate,
    )

    def verify(state: dict) -> dict:
        if verifier is None or not state["docs"] or state["answer"] == NO_ANSWER:
            return {**state, "verification": "skipped"}
        result = verifier.verify(state["question"], format_docs_to_xml(state["docs"]), state["answer"])
        return {**state, "answer": result.answer, "verification": result.status}

    def guard_output(state: dict) -> dict:
        allowed_ids = {doc.metadata["id"] for doc in state["docs"]}
        guarded = validate_output(state["answer"], allowed_ids, SYSTEM_PROMPT, allowed_phrases=[NO_ANSWER])
        return {**state, "answer": guarded}

    return (
        RunnableLambda(validate_input).with_config(run_name="input_guardrail")
        | RunnableLambda(lambda question: {"question": question, "docs": retriever.invoke(question)}).with_config(run_name="retrieve")
        | RunnablePassthrough.assign(answer=answer)
        | RunnableLambda(verify).with_config(run_name="verify_grounding")
        | RunnableLambda(guard_output).with_config(run_name="output_guardrail")
    )


def build_rag_chain(
    llm: BaseChatModel | Runnable | None = None,
    retriever: Runnable | None = None,
    verifier: AnswerVerifier | None = None,
) -> Runnable:
    """question (str) -> answer (str). Same steps as build_rag_pipeline, returning only the answer."""
    return build_rag_pipeline(llm, retriever, verifier) | itemgetter("answer")
