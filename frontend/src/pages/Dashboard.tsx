import { useState, useEffect, useCallback, type FormEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import { Database, Youtube, ArrowRight, Loader2 } from 'lucide-react';
import FileDropZone from '../components/FileDropZone';
import SourceList from '../components/SourceList';
import { useToast } from '../components/Toast';
import { uploadPDF, uploadYoutube, getSources, deleteSource } from '../services/api';

export default function Dashboard() {
  const { addToast } = useToast();
  const navigate = useNavigate();

  /* ── State ────────────────────────────────────────────────── */
  const [sources, setSources] = useState<string[]>([]);
  const [sourcesLoading, setSourcesLoading] = useState(true);
  const [pdfUploading, setPdfUploading] = useState(false);
  const [youtubeUrl, setYoutubeUrl] = useState('');
  const [youtubeLoading, setYoutubeLoading] = useState(false);
  const [showChatCTA, setShowChatCTA] = useState(false);

  /* ── Fetch sources ────────────────────────────────────────── */
  const refreshSources = useCallback(async () => {
    try {
      const data = await getSources();
      setSources(data);
    } catch (err) {
      addToast(err instanceof Error ? err.message : 'Failed to load sources', 'error');
    } finally {
      setSourcesLoading(false);
    }
  }, [addToast]);

  useEffect(() => {
    refreshSources();
  }, [refreshSources]);

  /* ── PDF upload ───────────────────────────────────────────── */
  const handleFileSelect = async (file: File) => {
    setPdfUploading(true);
    try {
      const res = await uploadPDF(file);
      addToast(
        `${res.source} uploaded — ${res.chunks_stored} chunks stored`,
        'success',
      );
      setShowChatCTA(true);
      await refreshSources();
    } catch (err) {
      addToast(err instanceof Error ? err.message : 'PDF upload failed', 'error');
    } finally {
      setPdfUploading(false);
    }
  };

  /* ── YouTube upload ───────────────────────────────────────── */
  const handleYoutubeSubmit = async (e: FormEvent) => {
    e.preventDefault();
    const trimmed = youtubeUrl.trim();
    if (!trimmed) return;

    setYoutubeLoading(true);
    try {
      const res = await uploadYoutube(trimmed);
      addToast(
        `${res.source} added — ${res.chunks_stored} chunks stored`,
        'success',
      );
      setYoutubeUrl('');
      setShowChatCTA(true);
      await refreshSources();
    } catch (err) {
      addToast(err instanceof Error ? err.message : 'YouTube import failed', 'error');
    } finally {
      setYoutubeLoading(false);
    }
  };

  /* ── Delete source ────────────────────────────────────────── */
  const handleDelete = async (source: string) => {
    try {
      await deleteSource(source);
      addToast(`Deleted "${source}"`, 'info');
      await refreshSources();
    } catch (err) {
      addToast(err instanceof Error ? err.message : 'Delete failed', 'error');
    }
  };

  /* ── Render ───────────────────────────────────────────────── */
  return (
    <div className="max-w-6xl mx-auto space-y-8 py-6">
      {/* ── Upload section (2‑col desktop, 1‑col mobile) ──── */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* PDF Upload Card */}
        <div className="rounded-xl bg-[var(--bg-surface)] border border-[var(--border)] p-6 space-y-4">
          <h2 className="text-lg font-semibold text-[var(--text-primary)] flex items-center gap-2">
            <Database size={20} className="text-indigo-400" />
            Upload PDF
          </h2>
          <FileDropZone onFileSelect={handleFileSelect} isUploading={pdfUploading} />
        </div>

        {/* YouTube Card */}
        <div className="rounded-xl bg-[var(--bg-surface)] border border-[var(--border)] p-6 space-y-4">
          <h2 className="text-lg font-semibold text-[var(--text-primary)] flex items-center gap-2">
            <Youtube size={20} className="text-red-400" />
            Add YouTube Video
          </h2>

          <form onSubmit={handleYoutubeSubmit} className="flex flex-col gap-3">
            <input
              type="url"
              value={youtubeUrl}
              onChange={(e) => setYoutubeUrl(e.target.value)}
              placeholder="https://youtube.com/watch?v=..."
              disabled={youtubeLoading}
              className="
                w-full rounded-lg bg-[var(--bg-main)] border border-[var(--border)]
                px-4 py-2.5 text-sm text-[var(--text-primary)]
                placeholder:text-[var(--text-secondary)]
                focus:outline-none focus:border-indigo-400
                disabled:opacity-50 transition-colors
              "
            />
            <button
              type="submit"
              disabled={youtubeLoading || !youtubeUrl.trim()}
              className="
                flex items-center justify-center gap-2
                w-full rounded-lg px-4 py-2.5 text-sm font-medium
                bg-red-500/20 text-red-300 border border-red-500/30
                hover:bg-red-500/30 disabled:opacity-40 disabled:cursor-not-allowed
                transition-colors cursor-pointer
              "
            >
              {youtubeLoading ? (
                <>
                  <Loader2 size={16} className="animate-spin" />
                  Processing…
                </>
              ) : (
                'Add Video'
              )}
            </button>
          </form>
        </div>
      </div>

      {/* ── "Go to Chat" CTA after successful upload ──────── */}
      {showChatCTA && (
        <button
          onClick={() => navigate('/chat')}
          className="
            flex items-center gap-2 mx-auto
            rounded-lg px-6 py-2.5 text-sm font-medium
            bg-indigo-500/20 text-indigo-300 border border-indigo-500/30
            hover:bg-indigo-500/30 transition-colors cursor-pointer
          "
        >
          Go to Chat
          <ArrowRight size={16} />
        </button>
      )}

      {/* ── Knowledge Base list ────────────────────────────── */}
      <div className="rounded-xl bg-[var(--bg-surface)] border border-[var(--border)] p-6 space-y-4">
        <h2 className="text-lg font-semibold text-[var(--text-primary)] flex items-center gap-2">
          <Database size={20} className="text-indigo-400" />
          Knowledge Base
        </h2>
        <SourceList
          sources={sources}
          onDelete={handleDelete}
          isLoading={sourcesLoading}
        />
      </div>
    </div>
  );
}
