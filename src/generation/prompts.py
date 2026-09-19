from langchain_core.prompts import ChatPromptTemplate

# The refusal sentence the system prompt tells the model to use (also returned when nothing is retrieved).
NO_ANSWER = "I cannot answer this question based on the provided context."

SYSTEM_PROMPT = """You are an accurate, grounded assistant. Answer user queries strictly using the provided context.

RULES:
1. Strict Grounding: Rely solely on facts in the <context> block. Never use external knowledge.
2. Citations: When stating a factual claim, cite the id of the document it came from, in square brackets (e.g., [aws-s3-001]).
3. Missing Information: If the context does not contain enough info to answer, state: "I cannot answer this question based on the provided context." Do not extrapolate or speculate.
4. Tone: Concise, professional, and direct."""

rag_prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("human", """<context>
{context}
</context>

Question: {question}""")
])