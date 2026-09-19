export type SourceLink = { title: string; url: string };

export type Source = {
  id: string;
  topic: string;
  category: string;
  links: SourceLink[];
  /** The knowledge-base file the entry comes from, e.g. "genai_fundamentals/langchain.json". */
  file: string;
  /** Re-ranker score scaled to 0-1; null when the results were not re-ranked. */
  relevance: number | null;
};

/** How the answer was found. */
export type Trace = {
  candidates: number;
  selected: number;
  reranked: boolean;
  verification: "passed" | "revised" | "unverified" | "skipped";
  knowledge_base: string;
  total_entries: number;
};

/** answered: normal reply · refused: nothing relevant in the knowledge base · blocked: input guardrail */
export type ChatStatus = "answered" | "refused" | "blocked";

export type ChatResponse = {
  status: ChatStatus;
  answer: string;
  sources: Source[];
  knowledge_summary: string[];
  trace: Trace | null;
  reason: string | null;
};

export type UserMessage = { id: string; role: "user"; text: string };

export type AssistantMessage = {
  id: string;
  role: "assistant";
  status: ChatStatus | "error";
  text: string;
  sources: Source[];
  /** The model's overview of what the retrieved knowledge-base documents contain. */
  knowledgeSummary?: string[];
  trace?: Trace;
  reason?: string;
  /** For "error" messages: the question to send again. */
  retry?: string;
};

export type Message = UserMessage | AssistantMessage;
