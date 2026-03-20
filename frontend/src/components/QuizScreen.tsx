import { useState, useEffect, useCallback } from 'react'
import type { Question, SessionResult } from '../types'
import { t } from '../i18n'
import { useStore } from '../hooks/useStore'

interface QuizScreenProps {
  question: Question
  currentIdx: number
  totalQuestions: number
  correctCount: number
  wrongCount: number
  store: ReturnType<typeof useStore>
  basePath: string
  onAnswer: (result: SessionResult, isCorrect: boolean) => void
  onNext: () => void
}

export default function QuizScreen({
  question, currentIdx, totalQuestions,
  correctCount, wrongCount, store, basePath,
  onAnswer, onNext,
}: QuizScreenProps) {
  const [answered, setAnswered] = useState(false)
  const [selected, setSelected] = useState<string | null>(null)

  useEffect(() => {
    setAnswered(false)
    setSelected(null)
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }, [currentIdx])

  const storeData = store.load()
  const qStats = storeData.questions[String(question.id)]
  const missRate = qStats?.wrong && qStats.seen ? Math.round((qStats.wrong / qStats.seen) * 100) : 0

  const handleSelect = useCallback((letter: string) => {
    if (answered) return
    setAnswered(true)
    setSelected(letter)
    const isCorrect = letter === question.answer
    onAnswer({
      id: question.id,
      question: question.question,
      yourAnswer: letter,
      yourAnswerText: question.choices[letter],
      correctAnswer: question.answer,
      correctAnswerText: question.choices[question.answer],
      correct: isCorrect,
      explanation: question.explanation,
    }, isCorrect)
  }, [answered, question, onAnswer])

  const progressPct = (currentIdx / totalQuestions) * 100
  const letters = ['A', 'B', 'C', 'D'].filter(l => question.choices[l])

  return (
    <>
      <div className="h-1.5 bg-gray-200 rounded-full mb-4 overflow-hidden">
        <div className="h-full bg-blue-600 rounded-full transition-all duration-300" style={{ width: `${progressPct}%` }} />
      </div>
      <div className="flex justify-between items-center mb-3 text-sm text-gray-500">
        <span>{currentIdx + 1} / {totalQuestions}</span>
        <span className="font-semibold">
          <span className="text-green-600">{correctCount}</span> / <span className="text-red-600">{wrongCount}</span>
        </span>
      </div>
      <div>
        <span className="inline-block bg-blue-50 text-blue-600 px-2.5 py-1 rounded-full text-xs font-semibold mb-3 uppercase tracking-wider">
          {question.category.replace(/_/g, ' ')}
        </span>
        {qStats?.wrong > 0 && (
          <span className="inline-block bg-red-50 text-red-600 px-2.5 py-1 rounded-full text-xs font-semibold ml-1.5">
            {t('missed')} {missRate}%
          </span>
        )}
      </div>
      <div className="text-lg font-semibold leading-relaxed mb-5">{question.question}</div>

      {question.image && (
        <div className="text-center my-3">
          <img src={`${basePath}signs/${question.image}`} alt="Road sign" className="max-w-full max-h-60 rounded-lg border border-gray-200 inline-block" />
        </div>
      )}

      <div className="flex flex-col gap-2.5 mb-4">
        {letters.map(letter => {
          let btnClass = 'bg-white border-gray-200 hover:border-blue-300 active:scale-[0.98] cursor-pointer'
          let letterClass = 'bg-gray-100 text-gray-500'

          if (answered) {
            const isCorrectAnswer = letter === question.answer
            const isSelected = letter === selected
            if (isCorrectAnswer) {
              btnClass = 'border-green-600 bg-green-50'
              letterClass = 'bg-green-600 text-white'
            } else if (isSelected) {
              btnClass = 'border-red-600 bg-red-50'
              letterClass = 'bg-red-600 text-white'
            } else {
              btnClass = 'border-gray-200 bg-white opacity-70'
            }
            btnClass += ' cursor-default'
          }

          return (
            <button
              key={letter}
              onClick={() => handleSelect(letter)}
              className={`flex items-start gap-3 p-3.5 border-2 rounded-xl text-base leading-relaxed text-left w-full text-gray-900 transition-all ${btnClass}`}
            >
              <span className={`shrink-0 w-7 h-7 flex items-center justify-center rounded-full font-bold text-sm ${letterClass}`}>
                {letter}
              </span>
              <span>{question.choices[letter]}</span>
            </button>
          )
        })}
      </div>

      {answered && (
        <>
          <div className="bg-blue-50 border-l-4 border-blue-600 px-4 py-3 rounded-r-xl text-sm leading-relaxed mb-4">
            {question.explanation}
          </div>
          <button
            onClick={onNext}
            className="w-full py-4 bg-blue-600 text-white rounded-xl text-[17px] font-semibold cursor-pointer hover:bg-blue-700 active:opacity-80 transition-colors"
          >
            {currentIdx < totalQuestions - 1 ? t('next') : t('seeResults')}
          </button>
        </>
      )}
    </>
  )
}
