import { useState, useEffect, useCallback, useMemo } from 'react';
import type { Question, SessionResult } from '../types';
import { t } from '../i18n';
import { useStore } from '../hooks/useStore';
import ThemeToggle from './ThemeToggle';

interface QuizScreenProps {
  question: Question;
  currentIdx: number;
  totalQuestions: number;
  correctCount: number;
  wrongCount: number;
  store: ReturnType<typeof useStore>;
  basePath: string;
  onAnswer: (result: SessionResult, isCorrect: boolean) => void;
  onNext: () => void;
}

export default function QuizScreen({
  question,
  currentIdx,
  totalQuestions,
  correctCount,
  wrongCount,
  store,
  basePath,
  onAnswer,
  onNext,
}: QuizScreenProps) {
  const [answered, setAnswered] = useState(false);
  const [selected, setSelected] = useState<string | null>(null);

  useEffect(() => {
    setAnswered(false);
    setSelected(null);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }, [currentIdx]);

  // Reload store data when the question changes (currentIdx is intentionally
  // included to bust the memo after each answer is persisted via store.save).
  // eslint-disable-next-line react-hooks/exhaustive-deps
  const storeData = useMemo(() => store.load(), [store, currentIdx]);
  const qStats = storeData.questions[String(question.id)];
  const missRate =
    qStats?.wrong && qStats.seen ? Math.round((qStats.wrong / qStats.seen) * 100) : 0;

  const handleSelect = useCallback(
    (letter: string) => {
      if (answered) return;
      setAnswered(true);
      setSelected(letter);
      const isCorrect = letter === question.answer;
      onAnswer(
        {
          id: question.id,
          question: question.question,
          yourAnswer: letter,
          yourAnswerText: question.choices[letter],
          correctAnswer: question.answer,
          correctAnswerText: question.choices[question.answer],
          correct: isCorrect,
          explanation: question.explanation,
        },
        isCorrect,
      );
    },
    [answered, question, onAnswer],
  );

  const progressPct = (currentIdx / totalQuestions) * 100;
  const letters = ['A', 'B', 'C', 'D'].filter((l) => question.choices[l]);

  return (
    <>
      <div className="h-1.5 bg-border rounded-full mb-4 overflow-hidden">
        <div
          className="h-full bg-primary rounded-full transition-all duration-300"
          style={{ width: `${progressPct}%` }}
        />
      </div>
      <div className="flex justify-between items-center mb-3 text-sm text-muted">
        <span className="tabular-nums">
          {currentIdx + 1} / {totalQuestions}
        </span>
        <div className="flex items-center gap-2">
          <span className="font-semibold tabular-nums">
            <span className="text-success">{correctCount}</span> /{' '}
            <span className="text-error">{wrongCount}</span>
          </span>
          <ThemeToggle />
        </div>
      </div>
      <div>
        <span className="inline-block bg-primary-surface text-primary px-2.5 py-1 rounded-full text-xs font-semibold mb-3 uppercase tracking-wider">
          {question.category.replace(/_/g, ' ')}
        </span>
        {qStats?.wrong > 0 && (
          <span className="inline-block bg-error-surface text-error px-2.5 py-1 rounded-full text-xs font-semibold ml-1.5">
            {t('missed')} {missRate}%
          </span>
        )}
      </div>
      <div className="text-lg font-semibold leading-relaxed mb-5">{question.question}</div>

      {question.image && (
        <div className="text-center my-3">
          <img
            src={`${basePath}signs/${question.image}`}
            alt="Road sign"
            className="max-w-full max-h-60 rounded-lg border border-border inline-block"
          />
        </div>
      )}

      <div className="flex flex-col gap-2.5 mb-4">
        {letters.map((letter) => {
          let btnClass =
            'bg-surface border-border hover:border-primary active:scale-[0.98] cursor-pointer';
          let letterClass = 'bg-gray-surface text-muted';
          let trailingIcon: 'check' | 'x' | null = null;

          if (answered) {
            const isCorrectAnswer = letter === question.answer;
            const isSelected = letter === selected;
            if (isCorrectAnswer) {
              btnClass = 'border-success bg-success-surface';
              letterClass = 'bg-success text-on-accent dark:bg-success-surface dark:text-success';
              trailingIcon = 'check';
            } else if (isSelected) {
              btnClass = 'border-error bg-error-surface';
              letterClass = 'bg-error text-on-accent dark:bg-error-surface dark:text-error';
              trailingIcon = 'x';
            } else {
              btnClass = 'border-border bg-surface opacity-70';
            }
            btnClass += ' cursor-default';
          }

          const ariaLabel = `${letter}: ${question.choices[letter]}`;
          return (
            <button
              key={letter}
              onClick={() => handleSelect(letter)}
              disabled={answered}
              aria-label={ariaLabel}
              aria-pressed={answered && letter === selected ? true : undefined}
              aria-disabled={answered}
              className={`flex items-start gap-3 p-3.5 border-2 rounded-xl text-base leading-relaxed text-left w-full text-foreground transition-all ${btnClass}`}
            >
              <span
                className={`shrink-0 w-7 h-7 flex items-center justify-center rounded-full font-bold text-sm ${letterClass}`}
              >
                {letter}
              </span>
              <span className="flex-1">{question.choices[letter]}</span>
              {trailingIcon === 'check' && (
                <svg
                  className="w-5 h-5 shrink-0 mt-0.5 text-success"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth={3}
                  strokeLinecap="round"
                  strokeLinejoin="round"
                >
                  <path d="M20 6L9 17l-5-5" />
                </svg>
              )}
              {trailingIcon === 'x' && (
                <svg
                  className="w-5 h-5 shrink-0 mt-0.5 text-error"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth={3}
                  strokeLinecap="round"
                  strokeLinejoin="round"
                >
                  <path d="M18 6L6 18M6 6l12 12" />
                </svg>
              )}
              {answered && letter === question.answer && (
                <span className="sr-only">(correct answer)</span>
              )}
              {answered && letter === selected && letter !== question.answer && (
                <span className="sr-only">(your incorrect answer)</span>
              )}
            </button>
          );
        })}
      </div>

      {answered && (
        <>
          <div className="bg-primary-surface border-l-4 border-primary px-4 py-3 rounded-r-xl text-base leading-relaxed mb-4">
            {question.explanation}
          </div>
          <button
            onClick={onNext}
            className="w-full py-4 bg-primary text-on-accent rounded-xl text-[17px] font-semibold cursor-pointer hover:bg-primary-hover active:opacity-80 transition-colors"
          >
            {currentIdx < totalQuestions - 1 ? t('next') : t('seeResults')}
          </button>
        </>
      )}
    </>
  );
}
