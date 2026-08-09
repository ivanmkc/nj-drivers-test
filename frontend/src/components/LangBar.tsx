import { useMemo } from 'react';
import { getAllLangs, getLangLabel, getLangName, isOfficialLang } from '../i18n';
import ThemeToggle from './ThemeToggle';

interface LangBarProps {
  currentLang: string;
  availableLangs?: string[];
  officialTestLanguages?: string[] | null;
  onSwitch: (lang: string) => void;
}

export default function LangBar({
  currentLang,
  availableLangs,
  officialTestLanguages,
  onSwitch,
}: LangBarProps) {
  const allLangs = useMemo(() => getAllLangs(), []);
  const available = useMemo(() => new Set(availableLangs || allLangs), [availableLangs, allLangs]);

  return (
    <div className="flex items-center justify-end gap-1 mb-3">
      <svg
        className="w-5 h-5 text-muted mr-0.5 shrink-0"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth={1.5}
        strokeLinecap="round"
        strokeLinejoin="round"
        aria-hidden="true"
      >
        <circle cx="12" cy="12" r="10" />
        <ellipse cx="12" cy="12" rx="4" ry="10" />
        <path d="M2 12h20" />
      </svg>
      {allLangs.map((lang) => {
        const disabled = !available.has(lang);
        const active = lang === currentLang && !disabled;
        const official = isOfficialLang(lang, officialTestLanguages);
        const langName = getLangName(lang);
        const ariaLabel = official
          ? `${langName} — offered on the official test`
          : `${langName} — practice only in this app`;
        return (
          <button
            key={lang}
            disabled={disabled}
            onClick={() => !disabled && onSwitch(lang)}
            aria-label={officialTestLanguages != null ? ariaLabel : langName}
            className={`relative px-3 min-h-[44px] border-[1.5px] rounded-full text-xs font-semibold transition-colors
              ${active ? 'border-primary bg-primary-surface text-primary' : 'border-border bg-surface text-muted'}
              ${disabled ? 'opacity-30 cursor-not-allowed' : 'cursor-pointer'}`}
          >
            {official && (
              <span
                className="absolute -top-1 -right-1 flex items-center justify-center w-4 h-4 rounded-full bg-success text-on-accent"
                aria-hidden="true"
              >
                <svg
                  className="w-2.5 h-2.5"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth={4}
                  strokeLinecap="round"
                  strokeLinejoin="round"
                >
                  <path d="M20 6L9 17l-5-5" />
                </svg>
              </span>
            )}
            {getLangLabel(lang)}
          </button>
        );
      })}
      <ThemeToggle />
    </div>
  );
}
