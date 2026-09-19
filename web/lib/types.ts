export type SourceLink = { title: string; url: string };

export type Source = {
  id: string;
  topic: string;
  category: string;
  links: SourceLink[];
};

/** answered: normal reply · refused: nothing relevant in the knowledge base · blocked: input guardrail */
export type ChatStatus = "answered" | "refused" | "blocked";

export type ChatResponse = {
  status: ChatStatus;
  answer: string;
  sources: Source[];
  reason: string | null;
};

export type UserMessage = { id: string; role: "user"; text: string };

export type AssistantMessage = {
  id: string;
  role: "assistant";
  status: ChatStatus | "error";
  text: string;
  sources: Source[];
  reason?: string;
  /** For "error" messages: the question to send again. */
  retry?: string;
};

export type Message = UserMessage | AssistantMessage;
