import React from 'react';

type PanelProps = {
  children: React.ReactNode;
  className?: string;
  style?: React.CSSProperties;
};

export const Panel: React.FC<PanelProps> = ({ children, className = '', style }) => (
  <div className={`overflow-hidden rounded-xl border border-ink/15 bg-paper ${className}`} style={style}>
    {children}
  </div>
);

export const PanelHeader: React.FC<{ children: React.ReactNode; right?: React.ReactNode }> = ({
  children,
  right,
}) => (
  <div className="flex h-10 items-center justify-between border-b border-ink/10 px-4 font-mono text-[11px] uppercase tracking-wide text-ink-soft">
    <span>{children}</span>
    {right}
  </div>
);

export const PanelDark: React.FC<{ children: React.ReactNode; className?: string; style?: React.CSSProperties }> = ({
  children,
  className = '',
  style,
}) => (
  <div
    className={`rounded-xl bg-ink-deep p-1.5 shadow-[0_24px_60px_-30px_rgba(35,35,35,0.45)] ${className}`}
    style={style}
  >
    <div className="overflow-hidden rounded-lg bg-ink font-mono text-[13px] text-paper ring-1 ring-white/10">
      {children}
    </div>
  </div>
);

export const PanelDarkHeader: React.FC<{ children: React.ReactNode; right?: React.ReactNode }> = ({
  children,
  right,
}) => (
  <div className="flex h-10 items-center justify-between border-b border-white/10 px-4 text-[11px] uppercase tracking-wide text-paper/40">
    <span>{children}</span>
    {right}
  </div>
);

export const TextAreaMock: React.FC<{
  value: string;
  placeholder?: string;
  minHeight?: number;
  showCaret?: boolean;
}> = ({ value, placeholder, minHeight = 220, showCaret = false }) => (
  <div
    className="whitespace-pre-wrap rounded-md border border-ink/15 bg-white/40 p-3 font-sans text-[15px] leading-relaxed text-ink"
    style={{ minHeight }}
  >
    {value || <span className="text-ink-soft/60">{placeholder}</span>}
    {showCaret && (
      <span className="ml-0.5 inline-block h-[1.1em] w-[2px] bg-ink/70 align-text-bottom" />
    )}
  </div>
);

export const PrimaryButton: React.FC<{
  children: React.ReactNode;
  disabled?: boolean;
  loading?: boolean;
  spinFrame?: number;
}> = ({ children, disabled, loading, spinFrame = 0 }) => (
  <button
    type="button"
    className={`inline-flex h-11 items-center justify-center rounded-md px-6 font-mono text-[12px] uppercase tracking-wide ${
      disabled
        ? 'cursor-not-allowed bg-ink/20 text-ink-soft'
        : 'bg-ink text-paper shadow-sm'
    }`}
    disabled={disabled}
  >
    {loading && (
      <span
        className="mr-2 inline-block h-4 w-4 rounded-full border-2 border-paper/30 border-t-paper"
        style={{ transform: `rotate(${(spinFrame * 12) % 360}deg)` }}
      />
    )}
    {children}
  </button>
);

export const ProgressTrack: React.FC<{ progress: number }> = ({ progress }) => (
  <div className="h-1.5 w-full overflow-hidden rounded-full bg-ink/10">
    <div
      className="h-full rounded-full bg-ink"
      style={{ width: `${Math.min(100, Math.max(0, progress))}%` }}
    />
  </div>
);

export const AppShell: React.FC<{ children: React.ReactNode; title?: string }> = ({
  children,
  title = 'talento.app',
}) => (
  <div className="flex h-full w-full flex-col bg-paper text-ink">
    <div className="flex h-12 shrink-0 items-center border-b border-ink/10 px-8">
      <span className="font-mono text-[12px] uppercase tracking-[0.2em] text-ink-soft">{title}</span>
    </div>
    <div className="flex-1 overflow-hidden px-10 py-8">{children}</div>
  </div>
);

export const StatCard: React.FC<{ label: string; value: string; color?: string; style?: React.CSSProperties }> = ({
  label,
  value,
  color = 'text-ink',
  style,
}) => (
  <div className="rounded-xl border border-ink/15 bg-paper p-5 text-center" style={style}>
    <div className="mb-1 font-mono text-[11px] uppercase tracking-wide text-ink-soft">{label}</div>
    <div className={`text-3xl font-medium tabular-nums ${color}`}>{value}</div>
  </div>
);
