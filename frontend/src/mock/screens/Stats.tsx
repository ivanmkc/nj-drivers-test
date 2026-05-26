import { HomeIndicator, StatusBar } from '../PhoneFrame';

const CATS = [
  { name: 'Signs & signals', pct: 95, color: 'bg-success', text: 'text-success' },
  { name: 'Safe driving rules', pct: 88, color: 'bg-primary', text: 'text-ink' },
  { name: 'Sharing the road', pct: 81, color: 'bg-primary', text: 'text-ink' },
  { name: 'Penalties & points', pct: 68, color: 'bg-warning', text: 'text-warning' },
  { name: 'Alcohol & drugs', pct: 52, color: 'bg-error', text: 'text-error' },
];

export function Stats({ variant }: { variant: 'light' | 'dark' }) {
  const isDark = variant === 'dark';
  const body = isDark ? 'text-ink-inverse' : 'text-ink';
  const subtle = isDark ? 'text-slate-400' : 'text-ink-subtle';
  const cardBg = isDark ? 'bg-surface-card-dark' : 'bg-surface-card-light';
  const cardBorder = isDark ? 'border-line-dark' : 'border-line-light';
  const track = isDark ? 'bg-line-dark' : 'bg-line-light';

  return (
    <div className="h-full flex flex-col">
      <StatusBar variant={variant} />

      <div className="px-xl pt-md">
        <button className={`${isDark ? 'text-accent-light' : 'text-primary'} text-sm font-medium`}>
          ← Back
        </button>
        <h1 className={`${body} font-display text-[28px] font-semibold mt-md`}>Your progress</h1>
        <div className={`${subtle} text-xs mt-1`}>California · last 30 days</div>
        <div className="w-10 h-0.5 bg-accent mt-md" />
      </div>

      {/* Top cards */}
      <div className="px-xl mt-lg grid grid-cols-2 gap-md">
        {[
          { label: 'Sessions', value: '14', sub: '+3 this week', color: body },
          {
            label: 'Avg score',
            value: '82',
            unit: '%',
            sub: 'passing threshold 83%',
            color: 'text-success',
          },
          { label: 'Streak', value: '7', sub: 'days · keep it going', color: body },
          { label: 'Questions', value: '312', sub: 'of 284 unique', color: body },
        ].map((s) => (
          <div key={s.label} className={`${cardBg} ${cardBorder} border rounded-lg p-md`}>
            <div className="text-accent-dark text-[10px] font-bold tracking-eyebrow uppercase">
              {s.label}
            </div>
            <div className={`${s.color} font-display text-[40px] font-semibold mt-sm leading-none`}>
              {s.value}
              {s.unit && <span className="text-xl text-slate-400">{s.unit}</span>}
            </div>
            <div className={`${subtle} text-xs mt-sm`}>{s.sub}</div>
          </div>
        ))}
      </div>

      {/* Category breakdown */}
      <div className="px-xl mt-lg flex-1">
        <div className={`${subtle} text-[11px] font-bold tracking-eyebrow uppercase mb-sm`}>
          Accuracy by category
        </div>
        <div className={`${cardBg} ${cardBorder} border rounded-lg p-md space-y-md`}>
          {CATS.map((c) => (
            <div key={c.name}>
              <div className="flex justify-between items-center mb-1.5">
                <span className={`${body} text-sm`}>{c.name}</span>
                <span className={`${c.text} text-xs font-semibold`}>{c.pct}%</span>
              </div>
              <div className={`${track} h-1.5 rounded-pill overflow-hidden`}>
                <div className={`${c.color} h-full`} style={{ width: `${c.pct}%` }} />
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Action */}
      <div className="px-xl pb-xl mt-md">
        <button className="w-full bg-primary text-white font-semibold rounded-md py-sm text-sm">
          Practice weakest categories
        </button>
      </div>

      <HomeIndicator variant={variant} />
    </div>
  );
}
