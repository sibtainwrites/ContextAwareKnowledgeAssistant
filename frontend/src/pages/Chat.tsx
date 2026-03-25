import {
  useState,
  useEffect,
  useRef,
  useCallback,
  type KeyboardEvent,
  type ChangeEvent,
} from 'react';
import { Link } from 'react-router-dom';
import {
  FileText,
  Youtube,
  RefreshCw,
  Plus,
  Send,
  AlertTriangle,
} from 'lucide-react';
import MessageBubble from '../components/MessageBubble';
import { useToast } from '../components/Toast';
import { askQuestion, getSources } from '../services/api';
import type { Message } from '../types/index';

/* ── Helpers ──────────────────────────────────────────────── */

const WELCOME_MESSAGE: Message = {
  id: 'welcome',
  role: 'assistant',
  content:
    'Hello! I\'m ready to answer questions about your uploaded documents.\nAsk me anything based on your PDFs or YouTube videos in the knowledge base.',
  timestamp: new Date(),
};

function isYoutube(s: string): boolean {
  return s.includes('youtube.com') || s.includes('youtu.be');
}

/* ── Component ────────────────────────────────────────────── */

export default function Chat() {
  const { addToast } = useToast();

  /* state */
  const [messages, setMessages] = useState<Message[]>([WELCOME_MESSAGE]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sources, setSources] = useState<string[]>([]);
  const [sourcesLoading, setSourcesLoading] = useState(true);

  /* refs */
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  /* ── Fetch sources ────────────────────────────────────── */
  const refreshSources = useCallback(async () => {
    setSourcesLoading(true);
    try {
      setSources(await getSources());
    } catch (err) {
      addToast(err instanceof Error ? err.message : 'Failed to load sources', 'error');
    } finally {
      setSourcesLoading(false);
    }
  }, [addToast]);

  useEffect(() => {
    refreshSources();
  }, [refreshSources]);

  /* ── Auto-scroll ──────────────────────────────────────── */
  const scrollToBottom = useCallback(() => {
    requestAnimationFrame(() =>
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' }),
    );
  }, []);

  useEffect(scrollToBottom, [messages, scrollToBottom]);

  /* ── Auto-resize textarea ─────────────────────────────── */
  const handleInputChange = (e: ChangeEvent<HTMLTextAreaElement>) => {
    setInputValue(e.target.value);
    const ta = e.target;
    ta.style.height = 'auto';
    ta.style.height = `${Math.min(ta.scrollHeight, 120)}px`; // max ~4 rows
  };

  /* ── Send message ─────────────────────────────────────── */
  const sendMessage = useCallback(async () => {
    const text = inputValue.trim();
    if (!text || isLoading) return;

    if (sources.length === 0) {
      addToast('Upload at least one document before chatting.', 'error');
      return;
    }

    /* user message */
    const userMsg: Message = {
      id: crypto.randomUUID(),
      role: 'user',
      content: text,
      timestamp: new Date(),
    };

    /* loading placeholder */
    const loadingId = crypto.randomUUID();
    const loadingMsg: Message = {
      id: loadingId,
      role: 'assistant',
      content: '',
      timestamp: new Date(),
      isLoading: true,
    };

    setMessages((prev) => [...prev, userMsg, loadingMsg]);
    setInputValue('');
    setIsLoading(true);

    // reset textarea height
    if (textareaRef.current) textareaRef.current.style.height = 'auto';

    try {
      const res = await askQuestion(text);

      const assistantMsg: Message = {
        id: loadingId,
        role: 'assistant',
        content: res.answer,
        citations: res.citations,
        timestamp: new Date(),
        response_time_ms: res.response_time_ms,
        chunks_used: res.chunks_used,
        error: res.error,
      };

      setMessages((prev) =>
        prev.map((m) => (m.id === loadingId ? assistantMsg : m)),
      );
    } catch (err) {
      const errorMsg: Message = {
        id: loadingId,
        role: 'assistant',
        content: '',
        timestamp: new Date(),
        error: err instanceof Error ? err.message : 'Something went wrong',
      };

      setMessages((prev) =>
        prev.map((m) => (m.id === loadingId ? errorMsg : m)),
      );
    } finally {
      setIsLoading(false);
    }
  }, [inputValue, isLoading, sources.length, addToast]);

  /* ── Keyboard shortcut ────────────────────────────────── */
  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  /* ── Render ───────────────────────────────────────────── */
  return (
    <div className="flex" style={{ height: 'calc(100vh - 56px)' }}>
      {/* ── Sidebar ──────────────────────────────────────── */}
      <aside className="hidden md:flex flex-col w-60 shrink-0 bg-[var(--bg-surface)] border-r border-[var(--border)]">
        {/* Header */}
        <div className="flex items-center justify-between px-4 py-3 border-b border-[var(--border)]">
          <h3 className="text-sm font-semibold text-[var(--text-primary)]">Knowledge Base</h3>
          <button
            onClick={refreshSources}
            disabled={sourcesLoading}
            className="p-1 rounded hover:bg-[var(--bg-elevated)] text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-colors cursor-pointer"
            aria-label="Refresh sources"
          >
            <RefreshCw size={14} className={sourcesLoading ? 'animate-spin' : ''} />
          </button>
        </div>

        {/* Source list */}
        <div className="flex-1 overflow-y-auto px-2 py-2 space-y-0.5">
          {sourcesLoading ? (
            <div className="space-y-2 px-2 pt-2">
              {[0, 1, 2].map((i) => (
                <div key={i} className="h-4 rounded bg-[var(--bg-elevated)] animate-pulse" />
              ))}
            </div>
          ) : sources.length === 0 ? (
            <div className="flex flex-col items-center text-center px-4 py-8 text-[var(--text-secondary)]">
              <FileText size={28} className="mb-2 opacity-40" />
              <p className="text-xs mb-3">No documents yet</p>
              <Link
                to="/dashboard"
                className="text-xs text-indigo-400 hover:underline"
              >
                Upload documents →
              </Link>
            </div>
          ) : (
            sources.map((s) => (
              <div
                key={s}
                className="flex items-center gap-2 px-2 py-1.5 rounded text-xs text-[var(--text-secondary)] hover:bg-[var(--bg-elevated)] transition-colors"
                title={s}
              >
                {isYoutube(s) ? (
                  <Youtube size={13} className="text-red-400 shrink-0" />
                ) : (
                  <FileText size={13} className="text-indigo-400 shrink-0" />
                )}
                <span className="truncate">{s}</span>
              </div>
            ))
          )}
        </div>

        {/* Footer link */}
        <div className="px-4 py-3 border-t border-[var(--border)]">
          <Link
            to="/dashboard"
            className="flex items-center gap-1.5 text-xs text-indigo-400 hover:text-indigo-300 transition-colors"
          >
            <Plus size={13} />
            Add More Documents
          </Link>
        </div>
      </aside>

      {/* ── Main chat area ───────────────────────────────── */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Warning banner */}
        {!sourcesLoading && sources.length === 0 && (
          <div className="flex items-center gap-2 px-4 py-2.5 bg-amber-900/30 border-b border-amber-700/40 text-amber-300 text-xs">
            <AlertTriangle size={14} />
            No documents uploaded.
            <Link to="/dashboard" className="underline ml-1">
              Upload now
            </Link>
          </div>
        )}

        {/* Messages */}
        <div className="flex-1 overflow-y-auto px-4 md:px-8 py-6 space-y-5">
          {messages.map((msg) => (
            <MessageBubble key={msg.id} message={msg} />
          ))}
          <div ref={messagesEndRef} />
        </div>

        {/* Input bar */}
        <div className="shrink-0 border-t border-[var(--border)] bg-[var(--bg-surface)] px-4 md:px-8 py-3">
          <div className="relative flex items-end gap-2 max-w-3xl mx-auto">
            <textarea
              ref={textareaRef}
              value={inputValue}
              onChange={handleInputChange}
              onKeyDown={handleKeyDown}
              disabled={isLoading}
              rows={1}
              placeholder={
                sources.length === 0
                  ? 'Upload documents first…'
                  : 'Ask a question about your documents…'
              }
              className="
                flex-1 resize-none rounded-xl
                bg-[var(--bg-main)] border border-[var(--border)]
                px-4 py-3 text-sm text-[var(--text-primary)]
                placeholder:text-[var(--text-secondary)]
                focus:outline-none focus:border-indigo-400
                disabled:opacity-50 transition-colors
              "
            />

            <button
              onClick={sendMessage}
              disabled={isLoading || !inputValue.trim()}
              className="
                shrink-0 p-3 rounded-xl
                bg-indigo-600 text-white
                hover:bg-indigo-500 disabled:opacity-30 disabled:cursor-not-allowed
                transition-colors cursor-pointer
              "
              aria-label="Send message"
            >
              <Send size={18} />
            </button>
          </div>

          {/* Character counter */}
          {inputValue.length > 100 && (
            <p className="text-[11px] text-[var(--text-secondary)] text-right mt-1 max-w-3xl mx-auto">
              {inputValue.length} characters
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
