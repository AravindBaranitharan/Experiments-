import type { Source } from "@/lib/types";

export function SourceCard({ source, anchorId, index }: { source: Source; anchorId: string; index: number }) {
  return (
    <li
      id={anchorId}
      className="motion-safe:animate-fade-up scroll-mt-6 border border-hairline bg-surface-soft p-5 transition-colors target:border-ink"
      style={{ animationDelay: `${index * 90}ms` }}
    >
      <p className="text-xs font-bold uppercase tracking-machined text-muted">{source.category}</p>
      <h3 className="mt-2 text-xl font-bold leading-tight text-ink">{source.topic}</h3>
      <p className="mt-1 text-xs uppercase tracking-machined text-muted">{source.id}</p>

      {source.links.length > 0 && (
        <ul className="mt-4 space-y-1.5 border-t border-hairline-strong pt-3">
          {source.links.map((link) => (
            <li key={link.url}>
              <a
                href={link.url}
                target="_blank"
                rel="noopener noreferrer"
                className="group flex items-center justify-between gap-3 text-sm text-body transition-colors hover:text-ink"
              >
                <span className="truncate">{link.title}</span>
                <span aria-hidden className="transition-transform group-hover:translate-x-0.5 motion-reduce:transition-none">
                  ↗
                </span>
                <span className="sr-only">(opens in a new tab)</span>
              </a>
            </li>
          ))}
        </ul>
      )}
    </li>
  );
}
