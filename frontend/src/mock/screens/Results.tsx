import { HomeIndicator, StatusBar } from '../PhoneFrame';

const WRONG = [
  {
    id: 14,
    category: 'Alcohol & drugs',
    prompt: 'Implied consent law requires…',
    ref: 'CA · DMV · 2025 · §6 p.49',
  },
  {
    id: 19,
    category: 'Sharing the road',
    prompt: 'Following distance behind a motorcycle…',
    ref: 'CA · DMV · 2025 · §5 p.38',
  },
  {
    id: 22,
    category: 'Penalties & points',
    prompt: 'License suspension threshold for points…',
    ref: 'CA · DMV · 2025 · §8 p.71',
  },
];

export function Results({ variant }: { variant: 'light' | 'dark' }) {
  const isDark = variant === 'dark';
  const body = isDark ? 'text-ink-inverse' : 'text-ink';
  const subtle = isDark ? 'text-slate-400' : 'text-ink-subtle';
  const cardBg = isDark ? 'bg-surface-card-dark' : 'bg-surface-card-light';
  const cardBorder = isDark ? 'border-line-dark' : 'border-line-light';

  return (
    <div className="h-full flex flex-col">
      <StatusBar variant={variant} />

      {/* Hero */}
      <div className="bg-gradient-to-b from-primary to-surface-dark px-xl pt-lg pb-xl">
        <div className="text-accent text-[11px] font-bold tracking-eyebrow mb-md">
          RESULTS · CALIFORNIA · 25 QUESTIONS
        </div>
        <div className="flex items-end gap-md mt-md">
          <div className="font-display text-[88px] leading-none font-semibold text-white">22</div>
          <div className="font-display text-3xl font-normal text-slate-400 pb-3">/ 25</div>
          <div className="ml-auto self-start mt-3">
            <span className="bg-success text-white text-xs font-bold tracking-eyebrow px-md py-1.5 rounded-pill">
              PASS
            </span>
          </div>
        </div>
        <div className="text-slate-300 text-sm mt-sm">88% · Passing threshold is 83%</div>
        <div className="text-slate-400 text-xs mt-1">Source: CA · DMV · 2025 Driver Handbook</div>

        <div className="grid grid-cols-2 gap-md mt-lg">
          <div>
            <div className="text-accent text-[10px] font-bold tracking-eyebrow uppercase">Time</div>
            <div className="text-white text-base font-semibold mt-1">9 min 14 s</div>
          </div>
          <div>
            <div className="text-accent text-[10px] font-bold tracking-eyebrow uppercase">
              Category high
            </div>
            <div className="text-white text-base font-semibold mt-1">Signs · 5/5</div>
          </div>
        </div>
      </div>

      <div className="h-[3px] bg-accent" />

      {/* Review */}
      <div className="px-xl pt-md pb-xl flex-1 overflow-hidden">
        <div className={`${subtle} text-[11px] font-bold tracking-eyebrow uppercase mb-sm`}>
          Review · 3 incorrect
        </div>
        <div className="space-y-sm">
          {WRONG.map((w) => (
            <div
              key={w.id}
              className={`${cardBg} ${cardBorder} border rounded-md flex overflow-hidden`}
            >
              <div className="w-1 bg-error" />
              <div className="p-md flex-1">
                <div className="flex items-start gap-md">
                  <div className="w-5 h-5 rounded-full bg-red-100 text-error flex items-center justify-center text-xs font-bold mt-0.5">
                    ✗
                  </div>
                  <div className="flex-1">
                    <div className={`${subtle} text-[10px] font-bold tracking-eyebrow uppercase`}>
                      Q{w.id} · {w.category}
                    </div>
                    <div className={`${body} text-sm font-medium mt-0.5`}>{w.prompt}</div>
                    <div className="text-accent-dark text-[11px] mt-1.5 tracking-wider">
                      {w.ref}
                    </div>
                  </div>
                  <div
                    className={`${isDark ? 'text-accent-light' : 'text-primary'} text-xs font-medium`}
                  >
                    Review →
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Action */}
      <div className="px-xl pb-xl space-y-sm">
        <button className="w-full bg-primary text-white font-semibold rounded-lg py-md text-base">
          Study weak topics
        </button>
        <button
          className={`${isDark ? 'text-accent-light' : 'text-primary'} w-full text-sm font-medium`}
        >
          Take another test →
        </button>
      </div>

      <HomeIndicator variant={variant} />
    </div>
  );
}
