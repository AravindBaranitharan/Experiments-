import { StatusPill } from "./StatusPill";
import { StripeDivider } from "./StripeDivider";

export function NavBar({ onNewChat, canReset }: { onNewChat: () => void; canReset: boolean }) {
  return (
    <header className="shrink-0 bg-canvas">
      <div className="mx-auto flex h-16 w-full max-w-4xl items-center justify-between px-4 sm:px-6">
        <div className="flex items-center gap-3">
          <span aria-hidden className="flex gap-0.5">
            <span className="h-5 w-1 bg-m-blue-light" />
            <span className="h-5 w-1 bg-m-blue-dark" />
            <span className="h-5 w-1 bg-m-red" />
          </span>
          <span className="text-sm font-bold uppercase tracking-machined text-ink">Knowledge Assistant</span>
        </div>

        <div className="flex items-center gap-6">
          {canReset && (
            <button
              type="button"
              onClick={onNewChat}
              className="motion-safe:animate-fade-in text-sm font-bold uppercase tracking-machined text-body transition-colors hover:text-ink"
            >
              New chat
            </button>
          )}
          <StatusPill />
        </div>
      </div>
      <StripeDivider />
      <div className="h-px bg-hairline-strong" />
    </header>
  );
}
