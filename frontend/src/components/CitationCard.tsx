import { useState } from 'react';
import { FileText, Youtube, Copy, Check } from 'lucide-react';
import type { Citation } from '../types/index';

interface CitationCardProps {
  citation: Citation;
}

export default function CitationCard({ citation }: CitationCardProps) {
  const [copied, setCopied] = useState(false);
  const isPdf = citation.type === 'pdf';

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(citation.source);
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    } catch {
      /* clipboard may be unavailable */
    }
  };

  const Icon = isPdf ? FileText : Youtube;
  const iconColor = isPdf ? 'text-indigo-400' : 'text-red-400';
  const displayName =
    citation.source.length > 35
      ? `${citation.source.slice(0, 35)}…`
      : citation.source;

  return (
    <button
      onClick={handleCopy}
      title={`Click to copy: ${citation.source}`}
      className="
        flex items-center gap-2 px-3 py-2 rounded-lg
        bg-[var(--bg-main)] border border-[var(--border)]
        hover:bg-[var(--bg-elevated)] transition-colors
        text-left cursor-pointer w-full
      "
    >
      <Icon size={14} className={`${iconColor} shrink-0`} />

      <span className="flex-1 text-xs text-[var(--text-primary)] truncate">
        {displayName}
      </span>

      {/* Badge */}
      {isPdf && citation.page != null && (
        <span className="shrink-0 text-[10px] px-1.5 py-0.5 rounded bg-indigo-500/20 text-indigo-300">
          Page {citation.page}
        </span>
      )}
      {!isPdf && citation.timestamp && (
        <span className="shrink-0 text-[10px] px-1.5 py-0.5 rounded bg-red-500/20 text-red-300">
          {citation.timestamp}
        </span>
      )}

      {/* Copy indicator */}
      {copied ? (
        <Check size={12} className="text-emerald-400 shrink-0" />
      ) : (
        <Copy size={12} className="text-[var(--text-secondary)] shrink-0 opacity-0 group-hover:opacity-100" />
      )}
    </button>
  );
}
