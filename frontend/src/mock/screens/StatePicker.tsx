import { HomeIndicator, StatusBar } from '../PhoneFrame';

type Row = {
  code: string;
  name: string;
  agency: string;
  qs: number;
  langs: string;
  selected?: boolean;
};

const SECTIONS: { letter: string; rows: Row[] }[] = [
  {
    letter: 'A',
    rows: [
      { code: 'AK', name: 'Alaska', agency: 'DMV', qs: 292, langs: 'EN · ES' },
      { code: 'AL', name: 'Alabama', agency: 'ALEA', qs: 292, langs: 'EN · ES' },
    ],
  },
  {
    letter: 'C',
    rows: [
      {
        code: 'CA',
        name: 'California',
        agency: 'DMV',
        qs: 284,
        langs: 'EN · ES · JA',
        selected: true,
      },
      { code: 'CO', name: 'Colorado', agency: 'DMV', qs: 255, langs: 'EN · ES' },
      { code: 'CT', name: 'Connecticut', agency: 'DMV', qs: 364, langs: 'EN · ES' },
    ],
  },
  {
    letter: 'D',
    rows: [{ code: 'DE', name: 'Delaware', agency: 'DMV', qs: 649, langs: 'EN · ES' }],
  },
];

export function StatePicker({ variant }: { variant: 'light' | 'dark' }) {
  const isDark = variant === 'dark';
  const body = isDark ? 'text-ink-inverse' : 'text-ink';
  const subtle = isDark ? 'text-slate-400' : 'text-ink-subtle';
  const cardBg = isDark ? 'bg-surface-card-dark' : 'bg-surface-card-light';
  const cardBorder = isDark ? 'border-line-dark' : 'border-line-light';
  const searchBg = isDark ? 'bg-surface-card-dark border-line-dark' : 'bg-white border-line-light';

  return (
    <div className="h-full flex flex-col">
      <StatusBar variant={variant} />
      <div className="px-xl pt-md">
        <button className={`${isDark ? 'text-accent-light' : 'text-primary'} text-sm font-medium`}>
          ← Back
        </button>
        <h1 className={`${body} font-display text-[28px] font-semibold mt-md`}>Pick your state</h1>
        <div className={`${subtle} text-xs mt-1`}>50 US jurisdictions · 17,753 questions</div>
      </div>

      {/* Search */}
      <div className="px-xl mt-md">
        <div className={`${searchBg} border rounded-md flex items-center gap-sm px-md py-md`}>
          <span className={subtle}>⌕</span>
          <span className={`${subtle} text-sm`}>Search by state or agency…</span>
        </div>
      </div>

      {/* Sections */}
      <div className="flex-1 overflow-hidden px-xl mt-lg space-y-md">
        {SECTIONS.map((sec) => (
          <div key={sec.letter}>
            <div className="text-accent-dark text-[11px] font-bold tracking-eyebrow uppercase mb-sm">
              {sec.letter}
            </div>
            <div className="space-y-sm">
              {sec.rows.map((r) => (
                <div
                  key={r.code}
                  className={`${cardBg} ${
                    r.selected ? 'border-primary border-2' : `${cardBorder} border`
                  } rounded-md flex overflow-hidden`}
                >
                  {r.selected && <div className="w-1 bg-accent" />}
                  <div className="p-md flex items-center justify-between flex-1">
                    <div className="flex items-center gap-md">
                      <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center font-display font-bold text-white text-[11px]">
                        {r.code}
                      </div>
                      <div>
                        <div className={`${body} font-display font-semibold`}>{r.name}</div>
                        <div className={`${subtle} text-[11px]`}>
                          {r.agency} · {r.qs} questions · {r.langs}
                        </div>
                      </div>
                    </div>
                    {r.selected ? (
                      <span className="bg-primary text-white text-[10px] font-bold tracking-eyebrow px-sm py-1 rounded-pill">
                        CURRENT
                      </span>
                    ) : (
                      <span className={`${subtle} text-lg`}>›</span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>

      <HomeIndicator variant={variant} />
    </div>
  );
}
