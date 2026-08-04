import type { SessionResult } from '../types';
import { t } from '../i18n';
import ThemeToggle from './ThemeToggle';

interface ResultsScreenProps {
  correctCount: number;
  totalQuestions: number;
  passingPct: number;
  agency: string;
  sessionResults: SessionResult[];
  onNewQuiz: () => void;
  onShowStats: () => void;
}

export default function ResultsScreen({
  correctCount,
  totalQuestions,
  passingPct,
  agency,
  sessionResults,
  onNewQuiz,
  onShowStats,
}: ResultsScreenProps) {
  const pct = Math.round((correctCount / totalQuestions) * 100);
  const pass = pct >= passingPct;
  const wrongResults = sessionResults.filter((r) => !r.correct);

  return (
    <>
      <div className="flex justify-end mb-1">
        <ThemeToggle />
      </div>
      <div className="text-center pt-[4vh]">
        <div
          className={`w-40 h-40 rounded-full flex flex-col items-center justify-center mx-auto mb-6 border-[6px]
          ${pass ? 'border-success text-success' : 'border-error text-error'}`}
        >
          <div className="text-[42px] font-bold tabular-nums">{pct}%</div>
          <div className="text-sm font-semibold uppercase">{pass ? t('pass') : t('fail')}</div>
        </div>
        <div className="text-xl font-bold mb-2">
          {pass ? t('congratulations') : t('keepPracticing')}
        </div>
        <div className="text-muted text-base mb-6 leading-relaxed">
          {t('resultDetail', {
            correct: correctCount,
            total: totalQuestions,
            pass_pct: passingPct,
            agency,
          })}
        </div>
        <button
          onClick={onNewQuiz}
          className="w-full py-4 bg-primary text-on-accent rounded-xl text-lg font-semibold cursor-pointer hover:bg-primary-hover active:opacity-80 transition-colors"
        >
          {t('newQuiz')}
        </button>
        <button
          onClick={onShowStats}
          className="w-full py-4 mt-2.5 bg-surface text-primary border-2 border-primary rounded-xl text-lg font-semibold cursor-pointer hover:bg-primary-surface transition-colors"
        >
          {t('viewStats')}
        </button>

        <div className="text-left mt-6">
          <h3 className="text-lg font-semibold mb-3">
            {wrongResults.length > 0
              ? t('reviewMissed', { count: wrongResults.length })
              : t('perfectScore')}
          </h3>
          {wrongResults.length > 0 ? (
            <div>
              {wrongResults.map((r) => (
                <div
                  key={r.id}
                  className="bg-surface rounded-xl p-3.5 mb-2.5 border-l-4 border-error"
                >
                  <div className="font-semibold text-sm mb-1.5">{r.question}</div>
                  <div className="text-xs text-muted">
                    {t('yourAnswer')}:{' '}
                    <strong className="text-foreground">
                      {r.yourAnswer}: {r.yourAnswerText}
                    </strong>
                  </div>
                  <div className="text-xs text-muted">
                    {t('correct')}:{' '}
                    <strong className="text-foreground">
                      {r.correctAnswer}: {r.correctAnswerText}
                    </strong>
                  </div>
                  <div className="text-xs text-muted mt-1.5 italic">{r.explanation}</div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-muted">{t('perfectMsg')}</p>
          )}
        </div>
      </div>
    </>
  );
}
