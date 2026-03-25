import {
  createContext,
  useContext,
  useState,
  useCallback,
  useEffect,
  useRef,
  type ReactNode,
} from 'react';
import { CheckCircle, XCircle, Loader2, Info, X } from 'lucide-react';
import type { ToastMessage } from '../types/index';

/* ── Context ─────────────────────────────────────────────── */

interface ToastContextValue {
  addToast: (
    message: string,
    type: ToastMessage['type'],
    duration?: number,
  ) => void;
}

const ToastContext = createContext<ToastContextValue | null>(null);

/**
 * Consume the toast context.
 * Must be used inside a `<ToastProvider>`.
 */
export function useToast(): ToastContextValue {
  const ctx = useContext(ToastContext);
  if (!ctx) throw new Error('useToast must be used within ToastProvider');
  return ctx;
}

/* ── Icons ───────────────────────────────────────────────── */

const iconMap: Record<ToastMessage['type'], ReactNode> = {
  success: <CheckCircle size={20} />,
  error: <XCircle size={20} />,
  loading: <Loader2 size={20} className="animate-spin" />,
  info: <Info size={20} />,
};

const colorMap: Record<ToastMessage['type'], string> = {
  success:
    'bg-emerald-900/80 border-emerald-700 text-emerald-200',
  error:
    'bg-red-900/80 border-red-700 text-red-200',
  loading:
    'bg-slate-800/80 border-slate-600 text-slate-200',
  info:
    'bg-blue-900/80 border-blue-700 text-blue-200',
};

/* ── Single Toast ────────────────────────────────────────── */

function ToastItem({
  toast,
  onRemove,
}: {
  toast: ToastMessage;
  onRemove: (id: string) => void;
}) {
  const [visible, setVisible] = useState(false);
  const timerRef = useRef<ReturnType<typeof setTimeout> | undefined>(undefined);

  useEffect(() => {
    // trigger enter animation
    requestAnimationFrame(() => setVisible(true));

    if (toast.type !== 'loading') {
      timerRef.current = setTimeout(() => {
        setVisible(false);
        setTimeout(() => onRemove(toast.id), 300);
      }, toast.duration ?? 4000);
    }

    return () => clearTimeout(timerRef.current);
  }, [toast, onRemove]);

  const dismiss = () => {
    setVisible(false);
    setTimeout(() => onRemove(toast.id), 300);
  };

  return (
    <div
      className={`
        flex items-center gap-3 w-80 rounded-lg border p-4 shadow-lg backdrop-blur
        transition-all duration-300 ease-in-out
        ${colorMap[toast.type]}
        ${visible ? 'translate-x-0 opacity-100' : 'translate-x-8 opacity-0'}
      `}
    >
      <span className="shrink-0">{iconMap[toast.type]}</span>
      <p className="flex-1 text-sm leading-snug">{toast.message}</p>
      <button
        onClick={dismiss}
        className="shrink-0 opacity-60 hover:opacity-100 transition-opacity cursor-pointer"
        aria-label="Dismiss"
      >
        <X size={16} />
      </button>
    </div>
  );
}

/* ── Provider ────────────────────────────────────────────── */

export function ToastProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<ToastMessage[]>([]);

  const removeToast = useCallback((id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  const addToast = useCallback(
    (message: string, type: ToastMessage['type'], duration?: number) => {
      const id = crypto.randomUUID();
      setToasts((prev) => [...prev, { id, message, type, duration }]);
    },
    [],
  );

  return (
    <ToastContext.Provider value={{ addToast }}>
      {children}

      {/* Toast container */}
      <div className="fixed top-4 right-4 z-50 flex flex-col gap-3 pointer-events-none">
        {toasts.map((t) => (
          <div key={t.id} className="pointer-events-auto">
            <ToastItem toast={t} onRemove={removeToast} />
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
}
