import type { ReactNode } from 'react';

type Variant = 'light' | 'dark';

export function PhoneFrame({ children, variant }: { children: ReactNode; variant: Variant }) {
  const bezel = variant === 'dark' ? 'bg-black' : 'bg-ink';
  const inner = variant === 'dark' ? 'bg-surface-dark' : 'bg-surface-light';
  return (
    <div className={`${bezel} rounded-[40px] p-[10px] shadow-card`}>
      <div className={`${inner} w-[400px] h-[840px] rounded-[32px] overflow-hidden relative`}>
        {children}
      </div>
    </div>
  );
}

export function StatusBar({ variant }: { variant: Variant }) {
  const fg = variant === 'dark' ? 'text-ink-inverse' : 'text-ink';
  return (
    <div className={`${fg} flex justify-between items-center px-xl pt-md text-xs font-semibold`}>
      <span>9:41</span>
      <span className="flex items-center gap-1">
        <span>●●●</span>
        <span className="ml-2">100%</span>
      </span>
    </div>
  );
}

export function HomeIndicator({ variant }: { variant: Variant }) {
  const bar = variant === 'dark' ? 'bg-line-dark' : 'bg-slate-400';
  return (
    <div className="absolute bottom-2 left-0 right-0 flex justify-center">
      <div className={`${bar} h-1 w-[120px] rounded-full`} />
    </div>
  );
}
