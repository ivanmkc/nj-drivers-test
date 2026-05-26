type Variant = 'light' | 'dark';

export function SourceCitation({
  state,
  agency,
  edition,
  ref: pageRef,
  variant,
  size = 'default',
}: {
  state: string;
  agency: string;
  edition: string;
  ref?: string;
  variant: Variant;
  size?: 'default' | 'compact';
}) {
  const isDark = variant === 'dark';
  const bg = isDark ? 'bg-surface-card-dark' : 'bg-surface-card-light';
  const border = isDark ? 'border-line-dark' : 'border-line-light';
  const label = isDark ? 'text-accent-light' : 'text-accent-dark';
  const body = isDark ? 'text-slate-200' : 'text-ink-muted';
  const cta = isDark ? 'text-accent-light' : 'text-primary';

  if (size === 'compact') {
    return (
      <div className={`${bg} ${border} border rounded-md flex items-stretch overflow-hidden`}>
        <div className="w-1 bg-accent" />
        <div className="px-sm py-1 flex-1">
          <div className={`${label} text-[10px] font-bold tracking-eyebrow uppercase`}>Source</div>
          <div className={`${body} text-xs`}>
            {state} · {agency} · {edition}
            {pageRef ? ` · ${pageRef}` : ''}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={`${bg} ${border} border rounded-md flex items-stretch overflow-hidden`}>
      <div className="w-1 bg-accent" />
      <div className="px-md py-sm flex-1 flex items-center justify-between">
        <div>
          <div className={`${label} text-[11px] font-bold tracking-eyebrow uppercase mb-0.5`}>
            Source
          </div>
          <div className={`${body} text-xs`}>
            {state} · {agency} · {edition}
            {pageRef ? ` · ${pageRef}` : ''}
          </div>
        </div>
        <div className={`${cta} text-xs font-medium`}>View →</div>
      </div>
    </div>
  );
}
