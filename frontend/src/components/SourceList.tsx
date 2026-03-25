import { FileText, Youtube, Trash2 } from 'lucide-react';

interface SourceListProps {
  sources: string[];
  onDelete: (source: string) => void;
  isLoading: boolean;
}

function isYoutubeSource(source: string): boolean {
  return (
    source.includes('youtube.com') ||
    source.includes('youtu.be') ||
    source.toLowerCase().startsWith('youtube')
  );
}

function SkeletonRow() {
  return (
    <div className="flex items-center gap-3 p-3 rounded-lg bg-[var(--bg-main)] animate-pulse">
      <div className="h-5 w-5 rounded bg-[var(--bg-elevated)]" />
      <div className="flex-1 space-y-1.5">
        <div className="h-3.5 w-3/4 rounded bg-[var(--bg-elevated)]" />
        <div className="h-2.5 w-1/3 rounded bg-[var(--bg-elevated)]" />
      </div>
      <div className="h-8 w-8 rounded bg-[var(--bg-elevated)]" />
    </div>
  );
}

export default function SourceList({ sources, onDelete, isLoading }: SourceListProps) {
  if (isLoading) {
    return (
      <div className="flex flex-col gap-2">
        <SkeletonRow />
        <SkeletonRow />
        <SkeletonRow />
      </div>
    );
  }

  if (sources.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-12 text-[var(--text-secondary)]">
        <FileText size={40} className="mb-3 opacity-40" />
        <p className="text-sm">No documents uploaded yet</p>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-1">
      <p className="text-xs text-[var(--text-secondary)] mb-2">
        {sources.length} source{sources.length !== 1 ? 's' : ''} in knowledge base
      </p>

      {sources.map((source) => {
        const isYT = isYoutubeSource(source);
        const Icon = isYT ? Youtube : FileText;
        const label = isYT ? 'YouTube Video' : 'PDF Document';
        const truncated = source.length > 40 ? `${source.slice(0, 40)}…` : source;

        return (
          <div
            key={source}
            className="group flex items-center gap-3 p-3 rounded-lg bg-[var(--bg-main)] hover:bg-[var(--bg-elevated)] transition-colors"
          >
            <Icon size={18} className={isYT ? 'text-red-400 shrink-0' : 'text-indigo-400 shrink-0'} />

            <div className="flex-1 min-w-0">
              <p className="text-sm text-[var(--text-primary)] truncate" title={source}>
                {truncated}
              </p>
              <p className="text-xs text-[var(--text-secondary)]">{label}</p>
            </div>

            <button
              onClick={() => {
                if (window.confirm(`Delete "${source}"? This cannot be undone.`)) {
                  onDelete(source);
                }
              }}
              className="
                shrink-0 p-1.5 rounded-md
                text-[var(--text-secondary)] hover:text-red-400 hover:bg-red-400/10
                opacity-0 group-hover:opacity-100 transition-all cursor-pointer
              "
              aria-label={`Delete ${source}`}
            >
              <Trash2 size={16} />
            </button>
          </div>
        );
      })}
    </div>
  );
}
