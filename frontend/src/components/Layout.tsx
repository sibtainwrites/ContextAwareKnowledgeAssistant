import { type ReactNode } from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import { Brain } from 'lucide-react';

interface LayoutProps {
  children: ReactNode;
}

const navItems = [
  { to: '/dashboard', label: 'Dashboard' },
  { to: '/chat', label: 'Chat' },
];

export default function Layout({ children }: LayoutProps) {
  const location = useLocation();

  return (
    <div className="min-h-screen bg-[var(--bg-main)]">
      {/* ── Navbar ───────────────────────────────────────── */}
      <nav className="fixed top-0 inset-x-0 z-40 h-14 flex items-center justify-between px-6 bg-[var(--bg-surface)] border-b border-[var(--border)]">
        {/* Left — Brand */}
        <div className="flex items-center gap-2">
          <Brain size={24} className="text-indigo-400" />
          <span className="text-lg font-semibold text-indigo-400 tracking-tight">
            KnowledgeAI
          </span>
        </div>

        {/* Center — Nav links */}
        <div className="flex items-center gap-1">
          {navItems.map(({ to, label }) => {
            const isActive = location.pathname === to;
            return (
              <NavLink
                key={to}
                to={to}
                className={`
                  relative px-4 py-1.5 text-sm font-medium rounded-md transition-colors
                  ${
                    isActive
                      ? 'text-indigo-400'
                      : 'text-[var(--text-secondary)] hover:text-[var(--text-primary)]'
                  }
                `}
              >
                {label}
                {isActive && (
                  <span className="absolute bottom-[-13px] left-0 right-0 h-[2px] bg-indigo-400 rounded-full" />
                )}
              </NavLink>
            );
          })}
        </div>

        {/* Right — Status indicator */}
        <div className="flex items-center gap-2 text-sm text-[var(--text-secondary)]">
          <span className="relative flex h-2.5 w-2.5">
            <span className="absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75 animate-ping" />
            <span className="relative inline-flex h-2.5 w-2.5 rounded-full bg-emerald-500" />
          </span>
          Connected
        </div>
      </nav>

      {/* ── Main content ─────────────────────────────────── */}
      <main
        className="pt-14 px-6 py-6"
        style={{ minHeight: 'calc(100vh - 56px)' }}
      >
        {children}
      </main>
    </div>
  );
}
