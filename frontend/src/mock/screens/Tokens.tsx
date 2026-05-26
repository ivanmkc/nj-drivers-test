export function Tokens() {
  const swatches: { name: string; hex: string; bg: string; fg?: string }[] = [
    { name: 'primary', hex: '#1E3A5F', bg: 'bg-primary', fg: 'text-white' },
    { name: 'surface · dark', hex: '#0F172A', bg: 'bg-surface-dark', fg: 'text-white' },
    { name: 'surface · light', hex: '#F8FAFC', bg: 'bg-surface-light border border-line-light' },
    { name: 'accent · brass', hex: '#C5A572', bg: 'bg-accent' },
    { name: 'success', hex: '#15803D', bg: 'bg-success', fg: 'text-white' },
    { name: 'error', hex: '#B91C1C', bg: 'bg-error', fg: 'text-white' },
    { name: 'warning', hex: '#B45309', bg: 'bg-warning', fg: 'text-white' },
  ];
  const spacing = [
    { name: 'xs · 4', w: 4 },
    { name: 'sm · 8', w: 8 },
    { name: 'md · 12', w: 12 },
    { name: 'lg · 16', w: 16 },
    { name: 'xl · 24', w: 24 },
    { name: '2xl · 32', w: 32 },
    { name: '3xl · 48', w: 48 },
  ];
  const radii = [
    { name: 'none · 0', cls: 'rounded-none' },
    { name: 'sm · 4', cls: 'rounded-sm' },
    { name: 'md · 8', cls: 'rounded-md' },
    { name: 'lg · 12', cls: 'rounded-lg' },
    { name: 'pill', cls: 'rounded-pill' },
  ];

  return (
    <div className="max-w-[1200px] mx-auto p-2xl font-body">
      <h1 className="font-display text-4xl font-semibold text-ink">
        polish-ui-official-look · design tokens
      </h1>
      <p className="text-ink-muted mt-sm">
        Civic / DMV-official aesthetic · navy + slate + brass · IBM Plex Serif + Inter · 4pt grid
      </p>
      <div className="border-t border-line-light mt-lg" />

      {/* Palette */}
      <div className="mt-xl">
        <div className="text-ink-muted text-xs font-bold uppercase tracking-eyebrow mb-md">
          Palette
        </div>
        <div className="grid grid-cols-7 gap-md">
          {swatches.map((s) => (
            <div key={s.name}>
              <div
                className={`${s.bg} ${s.fg ?? 'text-ink'} h-28 rounded-md flex items-end p-sm font-display text-xl font-semibold`}
              >
                Aa
              </div>
              <div className="text-ink text-sm font-semibold mt-sm">{s.name}</div>
              <div className="text-ink-subtle text-xs font-mono">{s.hex}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Typography */}
      <div className="mt-2xl grid grid-cols-2 gap-2xl">
        <div>
          <div className="text-ink-muted text-xs font-bold uppercase tracking-eyebrow mb-md">
            Typography
          </div>
          <h2 className="font-display text-4xl font-semibold text-ink">IBM Plex Serif · Display</h2>
          <p className="text-ink-muted text-sm mt-sm">
            36 / 28 / 22 — screen titles, score hero, brand mark, citation labels.
          </p>
          <div className="mt-lg">
            <p className="text-lg font-semibold text-ink">
              Inter · Body (regular / medium / semibold / bold)
            </p>
            <p className="text-ink-muted text-sm mt-sm">
              15 / 14 / 13 / 12 — question text, button labels, citation body, list rows.
            </p>
          </div>
        </div>

        <div>
          <div className="text-ink-muted text-xs font-bold uppercase tracking-eyebrow mb-md">
            Spacing · 4pt grid
          </div>
          <div className="space-y-sm font-mono text-xs text-ink-muted">
            {spacing.map((s) => (
              <div key={s.name} className="flex items-center gap-md">
                <div className="h-3.5 bg-accent" style={{ width: s.w }} />
                <span>{s.name}</span>
              </div>
            ))}
          </div>
          <div className="text-ink-muted text-xs font-bold uppercase tracking-eyebrow mt-lg mb-md">
            Radii
          </div>
          <div className="flex gap-md items-end">
            {radii.map((r) => (
              <div key={r.name} className="text-center">
                <div className={`bg-primary w-10 h-10 ${r.cls}`} />
                <div className="text-ink-subtle text-xs font-mono mt-sm">{r.name}</div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* SourceCitation preview */}
      <div className="mt-2xl">
        <div className="text-ink-muted text-xs font-bold uppercase tracking-eyebrow mb-md">
          SourceCitation · the highest-leverage new component
        </div>
        <div className="grid grid-cols-2 gap-md">
          <div className="bg-white border border-line-light rounded-md flex overflow-hidden">
            <div className="w-1 bg-accent" />
            <div className="p-md flex-1">
              <div className="text-accent-dark text-[11px] font-bold tracking-eyebrow uppercase">
                Source
              </div>
              <div className="text-ink-muted text-sm mt-0.5">
                CA · DMV · 2025 Driver Handbook · §4 p.32
              </div>
              <div className="text-ink-subtle text-xs mt-sm">
                Light variant — renders on every QuizScreen header and ResultsScreen review row.
              </div>
            </div>
          </div>
          <div className="bg-surface-dark text-white rounded-md flex overflow-hidden">
            <div className="w-1 bg-accent" />
            <div className="p-md flex-1">
              <div className="text-accent-light text-[11px] font-bold tracking-eyebrow uppercase">
                Source
              </div>
              <div className="text-slate-200 text-sm mt-0.5">SD · DPS · Rev Dec 2023 · §7 p.41</div>
              <div className="text-slate-400 text-xs mt-sm">
                Dark variant — automatic with system appearance.
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
