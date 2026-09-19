export type SourceLink = { title: string; url: string };

export type Source = {
  id: string;
  topic: string;
  category: string;
  links: SourceLink[];
  /** Re-ranker score scaled to 0-1; null when the results were not re-ranked. */
  relevance: number | null;
};

/** How the answer was found. */
export type Trace = {
  candidates: number;
  selected: number;
  reranked: boolean;
  verification: "passed" | "revised" | "unverified" | "skipped";
};

/** answered: normal reply · refused: nothing relevant in the knowledge base · blocked: input guardrail */
export type ChatStatus = "answered" | "refused" | "blocked";

export type ChatResponse = {
  status: ChatStatus;
  answer: string;
  sources: Source[];
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
  trace?: Trace;
  reason?: string;
  /** For "error" messages: the question to send again. */
  retry?: string;
};

export type Message = UserMessage | AssistantMessage;
