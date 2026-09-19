"use client";

import { useEffect, useRef } from "react";
import { useChat } from "@/hooks/useChat";
import { Composer } from "./Composer";
import { Hero } from "./Hero";
import { MessageBubble } from "./MessageBubble";
import { NavBar } from "./NavBar";
import { ThinkingIndicator } from "./ThinkingIndicator";

export function Chat() {
  const { messages, pending, send, reset } = useChat();
  const scroller = useRef<HTMLDivElement>(null);
  const empty = messages.length === 0 && !pending;

  // Empty state: start at the top. Otherwise keep the newest message in view.
  useEffect(() => {
    const el = scroller.current;
    if (!el) return;
    if (empty) {
      el.scrollTop = 0;
      return;
    }
    const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    el.scrollTo({ top: el.scrollHeight, behavior: reduce ? "auto" : "smooth" });
  }, [messages.length, pending, empty]);

  return (
    <div className="flex h-dvh flex-col bg-canvas">
      <NavBar onNewChat={reset} canReset={!empty} />

      <div ref={scroller} className="thin-scroll min-h-0 flex-1 overflow-y-auto">
        {empty ? (
          <Hero onPick={send} />
        ) : (
          <div role="log" aria-live="polite" className="mx-auto w-full max-w-4xl space-y-10 px-4 py-10 sm:px-6">
            {messages.map((message) => (
              <MessageBubble key={message.id} message={message} onRetry={send} />
            ))}
            {pending && <ThinkingIndicator />}
          </div>
        )}
      </div>

      <Composer onSend={send} busy={pending} />
    </div>
  );
}
