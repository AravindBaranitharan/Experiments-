from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

from src.generation.prompts import rag_prompt
from src.generation.context_builder import format_docs_to_xml
from src.retrieval.retriever import get_retriever
from src.guardrails.input_guards import validate_input
from src.guardrails.output_guards import validate_output

def build_rag_chain():
    retriever = get_retriever()
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    rag_chain = (
        # 1. Team 3: Input Guardrail Gate
        RunnableLambda(validate_input)
        # 2. Context Engineering: Retrieve & build structured XML
        | {
            "context": retriever | format_docs_to_xml,
            "question": RunnablePassthrough(),
        }
        # 3. Your Prompt & Model Generation
        | rag_prompt
        | llm
        | StrOutputParser()
        # 4. Team 3: Output Guardrail Gate
        | RunnableLambda(validate_output)
    )
    
    return rag_chain