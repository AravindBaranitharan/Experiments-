import type { ReactNode } from "react";
import { splitCitations } from "@/lib/citations";

const WORD_DELAY_MS = 22;
const MAX_DELAY_MS = 1400; // long answers must not take forever to appear

/**
 * Renders an answer with [citation] tags turned into chips. Words fade in one after another,
 * so a complete reply still reads like it is being written.
 */
export function AnswerText({ text, messageId }: { text: string; messageId: string }) {
  const nodes: ReactNode[] = [];
  let word = 0;

  splitCitations(text).forEach((part, partIndex) => {
    if (part.type === "cite") {
      nodes.push(
        <a
          key={`c${partIndex}`}
          href={`#${messageId}-${part.id}`}
          className="motion-safe:animate-fade-in mx-0.5 inline-block border border-hairline px-1.5 align-baseline text-[11px] font-bold uppercase leading-5 tracking-machined text-ink transition-colors hover:border-ink hover:bg-ink hover:text-canvas"
          style={{ animationDelay: `${Math.min(word * WORD_DELAY_MS, MAX_DELAY_MS)}ms` }}
        >
          {part.id}
        </a>,
      );
      return;
    }

    part.value.split(/(\s+)/).forEach((token, tokenIndex) => {
      if (!token) return;
      if (/^\s+$/.test(token)) {
        nodes.push(token);
        return;
      }
      nodes.push(
        <span
          key={`t${partIndex}-${tokenIndex}`}
          className="motion-safe:animate-fade-in"
          style={{ animationDelay: `${Math.min(word * WORD_DELAY_MS, MAX_DELAY_MS)}ms` }}
        >
          {token}
        </span>,
      );
      word += 1;
    });
  });

  return <p className="max-w-prose whitespace-pre-wrap text-base leading-relaxed text-body-strong">{nodes}</p>;
}
