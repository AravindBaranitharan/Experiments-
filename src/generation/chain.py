from langchain_core.language_models import BaseChatModel
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import Runnable, RunnableBranch, RunnableLambda, RunnablePassthrough

from src.generation.context_builder import format_docs_to_xml
from src.generation.llm import get_llm
from src.generation.prompts import NO_ANSWER, SYSTEM_PROMPT, rag_prompt
from src.guardrails.input_guards import validate_input
from src.guardrails.output_guards import validate_output
from src.retrieval.retriever import get_retriever


def build_rag_chain(llm: BaseChatModel | Runnable | None = None, retriever: Runnable | None = None) -> Runnable:
    """
    question (str) -> answer (str)

    1. Input guardrail   - raises GuardrailViolation if the question is blocked
    2. Retrieval         - semantic search over the knowledge base
    3. Grounding gate    - nothing relevant retrieved -> refuse without calling the LLM
    4. Generation        - prompt + LLM
    5. Output guardrail  - redact secrets, block prompt leaks, drop fabricated citations

    `llm` and `retriever` default to the configured ones; pass your own to test or swap them.
    """
    retriever = retriever or get_retriever()
    llm = llm or get_llm()

    generate = (
        RunnableLambda(lambda state: {"context": format_docs_to_xml(state["docs"]), "question": state["question"]})
        | rag_prompt
        | llm
        | StrOutputParser()
    )

    def guard_output(state: dict) -> str:
        allowed_ids = {doc.metadata["id"] for doc in state["docs"]}
        return validate_output(state["answer"], allowed_ids, SYSTEM_PROMPT, allowed_phrases=[NO_ANSWER])

    answer = RunnableBranch(
        (lambda state: not state["docs"], RunnableLambda(lambda state: NO_ANSWER)),
        generate,
    )

    return (
        RunnableLambda(validate_input).with_config(run_name="input_guardrail")
        | RunnableLambda(lambda question: {"question": question, "docs": retriever.invoke(question)}).with_config(run_name="retrieve")
        | RunnablePassthrough.assign(answer=answer)
        | RunnableLambda(guard_output).with_config(run_name="output_guardrail")
    )
