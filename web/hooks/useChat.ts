"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { askQuestion } from "@/lib/api";
import type { Message } from "@/lib/types";

const newId = () => globalThis.crypto?.randomUUID?.() ?? Math.random().toString(36).slice(2);

export function useChat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [pending, setPending] = useState(false);
  const controller = useRef<AbortController | null>(null);

  useEffect(() => () => controller.current?.abort(), []);

  const send = useCallback(async (raw: string) => {
    const question = raw.trim();
    if (!question || controller.current) return; // ignore empty input and double-sends

    const request = new AbortController();
    controller.current = request;
    setPending(true);
    setMessages((all) => [...all, { id: newId(), role: "user", text: question }]);

    try {
      const reply = await askQuestion(question, request.signal);
      setMessages((all) => [
        ...all,
        { id: newId(), role: "assistant", status: reply.status, text: reply.answer, sources: reply.sources, knowledgeSummary: reply.knowledge_summary, trace: reply.trace ?? undefined, reason: reply.reason ?? undefined },
      ]);
    } catch (error) {
      if ((error as Error).name === "AbortError") return;
      setMessages((all) => [
        ...all,
        { id: newId(), role: "assistant", status: "error", text: (error as Error).message, sources: [], retry: question },
      ]);
    } finally {
      if (controller.current === request) {
        controller.current = null;
        setPending(false);
      }
    }
  }, []);

  const reset = useCallback(() => {
    controller.current?.abort();
    controller.current = null;
    setPending(false);
    setMessages([]);
  }, []);

  return { messages, pending, send, reset };
}
