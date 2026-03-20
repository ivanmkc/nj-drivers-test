import { useEffect, useMemo } from 'react'
import type { StateSummary, QuizMode } from '../types'
import { t } from '../i18n'
import { useStore } from '../hooks/useStore'
import LangBar from './LangBar'

interface StartScreenProps {
  state: StateSummary
  lang: string
  quizMode: QuizMode
  selectedCount: number
  store: ReturnType<typeof useStore>
  onSetMode: (mode: QuizMode) => void
  onSetCount: (count: number) => void
  onStart: () => void
  onChangeState: () => void
  onShowStats: () => void
  onSwitchLang: (lang: string) => void
}

export default function StartScreen({
  state, lang, quizMode, selectedCount, store,
  onSetMode, onSetCount, onStart, onChangeState, onShowStats, onSwitchLang,
}: StartScreenProps) {
  const storeData = store.load()
  const history = storeData.history

  const weakCount = useMemo(() => {
    return Object.values(storeData.questions).filter(d => d.wrong > 0 && d.seen >= 1).length
  }, [storeData])

  const counts = useMemo(() => {
    const total = state.total_questions
    const c = [10, 25, 50, 100].filter(n => n <= total)
    if (!c.includes(total)) c.push(total)
    return c
  }, [state.total_questions])

  useEffect(() => {
    onSetCount(Math.min(50, state.total_questions))
  }, [state.total_questions, onSetCount])

  const avg = history.length ? Math.round(history.reduce((s, r) => s + r.pct, 0) / history.length) : 0
  let streak = 0
  for (let i = history.length - 1; i >= 0; i--) {
    if (history[i].pct >= state.passing_score_pct) streak++
    else break
  }

  const startDisabled = quizMode === 'weak' && weakCount === 0

  return (
    <>
      <LangBar currentLang={lang} availableLangs={state.languages} onSwitch={onSwitchLang} />
      <div className="text-center pt-[4vh]">
        <h1 className="text-2xl font-bold text-blue-600 mb-2">
          {t('title', { state: state.code.toUpperCase(), state_name: state.name, agency: state.agency, pass_pct: state.passing_score_pct })}
        </h1>
        <p className="text-gray-500 text-sm mb-1 leading-relaxed">
          {t('subtitle', { state: state.code.toUpperCase(), state_name: state.name, agency: state.agency })}
        </p>
        <p className="text-gray-400 text-xs mb-5">
          {t('passingScore', {
            pass_pct: state.passing_score_pct,
            pass_count: Math.ceil(state.test_question_count * state.passing_score_pct / 100),
            test_count: state.test_question_count,
          })}
        </p>
      </div>

      {history.length > 0 && (
        <div className="bg-white rounded-xl p-4 mb-5 border border-gray-200">
          <div className="flex justify-between items-center">
            <div className="flex gap-4">
              <div className="text-center">
                <div className="text-xl font-bold">{history.length}</div>
                <div className="text-[11px] text-gray-500 uppercase tracking-wide">{t('quizzes')}</div>
              </div>
              <div className="text-center">
                <div className="text-xl font-bold">{avg}%</div>
                <div className="text-[11px] text-gray-500 uppercase tracking-wide">{t('avgScore')}</div>
              </div>
              <div className="text-center">
                <div className="text-xl font-bold">{streak}</div>
                <div className="text-[11px] text-gray-500 uppercase tracking-wide">{t('passStreak')}</div>
              </div>
            </div>
            <button onClick={onShowStats} className="text-blue-600 text-sm font-semibold cursor-pointer whitespace-nowrap">
              {t('viewStats')}
            </button>
          </div>
        </div>
      )}

      <div className="flex gap-2 mb-4">
        {(['random', 'weak'] as const).map(mode => {
          const active = quizMode === mode
          return (
            <button
              key={mode}
              onClick={() => onSetMode(mode)}
              className={`flex-1 py-3 px-2 border-2 rounded-xl text-sm font-semibold cursor-pointer text-center transition-colors
                ${active ? 'border-blue-500 bg-blue-50 text-blue-600' : 'border-gray-200 bg-white'}`}
            >
              <span className="text-xl block mb-1">{mode === 'random' ? '\u{1F3B2}' : '\u{1F3AF}'}</span>
              <span>{t(mode === 'random' ? 'modeRandom' : 'modeWeak')}</span>
              {mode === 'weak' && weakCount > 0 && (
                <span className="inline-block bg-red-600 text-white text-[11px] px-1.5 rounded-full ml-1 font-bold">{weakCount}</span>
              )}
              <span className="text-[11px] font-normal text-gray-500 block">
                {t(mode === 'random' ? 'modeRandomDesc' : 'modeWeakDesc')}
              </span>
            </button>
          )
        })}
      </div>

      <p className="font-semibold mb-2 text-sm">{t('numQuestions')}</p>
      <div className="flex gap-2 justify-center mb-5 flex-wrap">
        {counts.map(n => {
          const label = n === state.total_questions ? 'All' : String(n)
          const active = n === selectedCount
          return (
            <button
              key={n}
              onClick={() => onSetCount(n)}
              className={`px-5 py-2.5 border-2 border-blue-600 rounded-xl text-base font-semibold cursor-pointer transition-colors
                ${active ? 'bg-blue-600 text-white' : 'bg-white text-blue-600 hover:bg-blue-50'}`}
            >
              {label}
            </button>
          )
        })}
      </div>

      <button
        onClick={onStart}
        disabled={startDisabled}
        className="w-full py-4 bg-blue-600 text-white rounded-xl text-lg font-semibold cursor-pointer hover:bg-blue-700 active:opacity-80 transition-colors disabled:opacity-50 disabled:cursor-default"
      >
        {startDisabled ? t('noWeakSpots') : t('startQuiz')}
      </button>
      <button
        onClick={onChangeState}
        className="w-full py-2.5 mt-1.5 text-gray-500 text-sm font-medium bg-transparent border-none cursor-pointer"
      >
        {t('changeState')}
      </button>
    </>
  )
}
