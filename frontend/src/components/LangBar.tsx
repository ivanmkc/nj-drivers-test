import { useMemo } from 'react';
import { getAllLangs, getLangLabel } from '../i18n';
import ThemeToggle from './ThemeToggle';

interface LangBarProps {
  currentLang: string;
  availableLangs?: string[];
  onSwitch: (lang: string) => void;
}

export default function LangBar({ currentLang, availableLangs, onSwitch }: LangBarProps) {
  const allLangs = useMemo(() => getAllLangs(), []);
  const available = useMemo(() => new Set(availableLangs || allLangs), [availableLangs, allLangs]);

  return (
    <div className="flex justify-end gap-1 mb-3">
      {allLangs.map((lang) => {
        const disabled = !available.has(lang);
        const active = lang === currentLang && !disabled;
        return (
          <button
            key={lang}
            disabled={disabled}
            onClick={() => !disabled && onSwitch(lang)}
            className={`px-3 min-h-[44px] border-[1.5px] rounded-full text-xs font-semibold transition-colors
              ${active ? 'border-primary bg-primary-surface text-primary' : 'border-border bg-surface text-muted'}
              ${disabled ? 'opacity-30 cursor-not-allowed' : 'cursor-pointer'}`}
          >
            {getLangLabel(lang)}
          </button>
        );
      })}
      <ThemeToggle />
    </div>
  );
}
