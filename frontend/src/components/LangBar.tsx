import { getAllLangs, getLangLabel } from '../i18n'

interface LangBarProps {
  currentLang: string
  availableLangs?: string[]
  onSwitch: (lang: string) => void
}

export default function LangBar({ currentLang, availableLangs, onSwitch }: LangBarProps) {
  const allLangs = getAllLangs()
  const available = new Set(availableLangs || allLangs)

  return (
    <div className="flex justify-end gap-1 mb-3">
      {allLangs.map(lang => {
        const disabled = !available.has(lang)
        const active = lang === currentLang && !disabled
        return (
          <button
            key={lang}
            disabled={disabled}
            onClick={() => !disabled && onSwitch(lang)}
            className={`px-3 py-1.5 border-[1.5px] rounded-full text-xs font-semibold transition-colors
              ${active ? 'border-blue-500 bg-blue-50 text-blue-600' : 'border-gray-200 bg-white text-gray-500'}
              ${disabled ? 'opacity-30 cursor-not-allowed' : 'cursor-pointer'}`}
          >
            {getLangLabel(lang)}
          </button>
        )
      })}
    </div>
  )
}
