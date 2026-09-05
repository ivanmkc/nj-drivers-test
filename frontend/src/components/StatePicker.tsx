import { useState } from 'react';
import type { StateSummary } from '../types';
import { t } from '../i18n';
import LangBar from './LangBar';

const COUNTRIES: Record<string, { name: string; flag: string }> = {
  us: { name: 'United States', flag: '\u{1F1FA}\u{1F1F8}' },
  ca: { name: 'Canada', flag: '\u{1F1E8}\u{1F1E6}' },
  au: { name: 'Australia', flag: '\u{1F1E6}\u{1F1FA}' },
  uk: { name: 'United Kingdom', flag: '\u{1F1EC}\u{1F1E7}' },
  nz: { name: 'New Zealand', flag: '\u{1F1F3}\u{1F1FF}' },
  ie: { name: 'Ireland', flag: '\u{1F1EE}\u{1F1EA}' },
  sg: { name: 'Singapore', flag: '\u{1F1F8}\u{1F1EC}' },
};

function getCountry(code: string): string {
  if (code.startsWith('ca-')) return 'ca';
  if (code.startsWith('au-')) return 'au';
  if (['uk', 'nz', 'ie', 'sg'].includes(code)) return code;
  return 'us';
}

interface StatePickerProps {
  states: StateSummary[];
  lang: string;
  onSelectState: (code: string) => void;
  onSwitchLang: (lang: string) => void;
}

export default function StatePicker({
  states,
  lang,
  onSelectState,
  onSwitchLang,
}: StatePickerProps) {
  const [query, setQuery] = useState('');
  const q = query.toLowerCase().trim();

  const groups: Record<string, StateSummary[]> = {};
  for (const s of states) {
    const country = getCountry(s.code);
    if (!groups[country]) groups[country] = [];
    if (q && !s.name.toLowerCase().includes(q) && !s.code.includes(q)) continue;
    groups[country].push(s);
  }

  const order = [
    'us',
    ...Object.keys(groups)
      .filter((c) => c !== 'us')
      .sort(),
  ];
  const totalShown = order.reduce((sum, country) => sum + (groups[country]?.length ?? 0), 0);

  return (
    <>
      <LangBar currentLang={lang} onSwitch={onSwitchLang} />
      <div className="text-center pt-4">
        <h1 className="text-2xl font-bold text-primary mb-1">{t('appTitle')}</h1>
        <p className="text-muted text-base mb-4">{t('selectStateDesc')}</p>
      </div>
      <div className="relative mb-4">
        <svg
          className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-subtle pointer-events-none"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
          />
        </svg>
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search states..."
          className="w-full pl-10 pr-4 py-3 border-2 border-border rounded-xl text-base bg-surface text-foreground outline-none focus:border-primary transition-colors placeholder:text-subtle"
        />
      </div>
      <div>
        {order.map((country) => {
          const countryStates = groups[country];
          if (!countryStates?.length) return null;
          const info = COUNTRIES[country] || { name: country.toUpperCase(), flag: '' };
          return (
            <div key={country} className="mb-5">
              <div className="flex items-center gap-2 text-xs font-bold text-muted uppercase tracking-wider px-1 pb-2 border-b border-border mb-2">
                <span className="text-lg">{info.flag}</span> {info.name}{' '}
                <span className="font-normal">({countryStates.length})</span>
              </div>
              <div className="flex flex-col gap-2">
                {countryStates.map((s) => {
                  const hasQ = s.total_questions > 0;
                  return (
                    <button
                      key={s.code}
                      onClick={() => hasQ && onSelectState(s.code)}
                      disabled={!hasQ}
                      className={`flex justify-between items-center p-4 bg-surface border-2 rounded-xl transition-all text-left w-full
                        ${hasQ ? 'border-border cursor-pointer hover:border-primary active:scale-[0.98]' : 'border-border-subtle opacity-50 cursor-default'}`}
                    >
                      <div>
                        <div className="text-base font-semibold">{s.name}</div>
                        <div className="text-xs text-muted mt-0.5">
                          {s.agency} &middot;{' '}
                          {t('passingScore', {
                            pass_pct: s.passing_score_pct,
                            pass_count: Math.ceil(
                              (s.test_question_count * s.passing_score_pct) / 100,
                            ),
                            test_count: s.test_question_count,
                          })}
                        </div>
                      </div>
                      <div className="text-right">
                        {hasQ ? (
                          <div className="text-xs text-primary font-semibold">
                            {t('questionsAvailable', { count: s.total_questions })}
                          </div>
                        ) : (
                          <span className="text-[11px] text-subtle bg-gray-surface px-2 py-0.5 rounded-full">
                            {t('comingSoon')}
                          </span>
                        )}
                      </div>
                    </button>
                  );
                })}
              </div>
            </div>
          );
        })}
        {totalShown === 0 && (
          <div className="text-subtle text-base py-10 text-center">
            No states found matching &ldquo;{query}&rdquo;
          </div>
        )}
      </div>
    </>
  );
}
