import { Brain } from 'lucide-react';
import type { Message } from '../types/index';
import TypingIndicator from './TypingIndicator';
import CitationCard from './CitationCard';

interface MessageBubbleProps {
  message: Message;
}

export default function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === 'user';

  /* ── User bubble ─────────────────────────────────────── */
  if (isUser) {
    return (
      <div className="flex justify-end animate-fade-in">
        <div
          className="
            max-w-[70%] rounded-2xl rounded-br-md px-4 py-3
            bg-indigo-600 text-white text-sm leading-relaxed
          "
        >
          {message.content}
        </div>
      </div>
    );
  }

  /* ── Assistant bubble ────────────────────────────────── */
  return (
    <div className="flex gap-3 items-start animate-fade-in">
      {/* Avatar */}
      <div className="shrink-0 mt-1 h-8 w-8 rounded-full bg-[var(--bg-elevated)] flex items-center justify-center">
        <Brain size={16} className="text-indigo-400" />
      </div>

      <div className="max-w-[80%] space-y-2">
        {/* Main content */}
        <div
          className="
            rounded-2xl rounded-tl-md px-4 py-3
            bg-[var(--bg-elevated)] text-sm leading-relaxed text-[var(--text-primary)]
          "
        >
          {message.isLoading ? (
            <TypingIndicator />
          ) : message.error ? (
            <p className="text-red-400">{message.error}</p>
          ) : (
            message.content.split('\n').map((line, i) => (
              <span key={i}>
                {line}
                {i < message.content.split('\n').length - 1 && <br />}
              </span>
            ))
          )}
        </div>

        {/* Citations */}
        {!message.isLoading && message.citations && message.citations.length > 0 && (
          <div className="space-y-1.5">
            <p className="text-xs text-[var(--text-secondary)] font-medium">
              Sources used:
            </p>
            <div className="grid gap-1.5">
              {message.citations.map((c, idx) => (
                <CitationCard key={`${c.source}-${idx}`} citation={c} />
              ))}
            </div>
          </div>
        )}

        {/* Footer metadata */}
        {!message.isLoading && !message.error && message.response_time_ms != null && (
          <p className="text-[11px] text-[var(--text-secondary)]">
            Answered in {message.response_time_ms}ms
            {message.chunks_used != null && ` · Used ${message.chunks_used} chunks`}
          </p>
        )}
      </div>

      {/* Inline fade-in animation */}
      <style>{`
        @keyframes fade-in {
          from { opacity: 0; transform: translateY(8px); }
          to   { opacity: 1; transform: translateY(0); }
        }
        .animate-fade-in {
          animation: fade-in 0.3s ease-out;
        }
      `}</style>
    </div>
  );
}
