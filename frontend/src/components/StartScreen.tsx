import { useState, useEffect, useMemo } from 'react';
import type { StateSummary, QuizMode } from '../types';
import { t } from '../i18n';
import { useStore } from '../hooks/useStore';
import { calcPassStreak, calcAverageScore } from '../utils';
import { QUESTION_COUNT_OPTIONS, DEFAULT_QUESTION_COUNT } from '../constants';
import LangBar from './LangBar';

function prettifyCategory(cat: string): string {
  return cat.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());
}

function formatDate(iso: string): string {
  try {
    return new Date(iso).toLocaleDateString(undefined, {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  } catch {
    return iso.split('T')[0];
  }
}

interface StartScreenProps {
  state: StateSummary;
  lang: string;
  quizMode: QuizMode;
  selectedCount: number;
  store: ReturnType<typeof useStore>;
  onSetMode: (mode: QuizMode) => void;
  onSetCount: (count: number) => void;
  onStart: () => void;
  onChangeState: () => void;
  onShowStats: () => void;
  onSwitchLang: (lang: string) => void;
}

export default function StartScreen({
  state,
  lang,
  quizMode,
  selectedCount,
  store,
  onSetMode,
  onSetCount,
  onStart,
  onChangeState,
  onShowStats,
  onSwitchLang,
}: StartScreenProps) {
  const [storeData, setStoreData] = useState(() => store.load());
  useEffect(() => {
    setStoreData(store.load());
  }, [store]);
  const history = storeData.history;

  const weakCount = useMemo(() => {
    return Object.values(storeData.questions).filter((d) => d.wrong > 0 && d.seen >= 1).length;
  }, [storeData]);

  const counts = useMemo(() => {
    const total = state.total_questions;
    const c = QUESTION_COUNT_OPTIONS.filter((n) => n <= total);
    if (!c.includes(total)) c.push(total);
    return c;
  }, [state.total_questions]);

  useEffect(() => {
    onSetCount(Math.min(DEFAULT_QUESTION_COUNT, state.total_questions));
  }, [state.total_questions, onSetCount]);

  const avg = calcAverageScore(history);
  const streak = calcPassStreak(history, state.passing_score_pct);

  const startDisabled = quizMode === 'weak' && weakCount === 0;

  const [aboutOpen, setAboutOpen] = useState(false);

  const verification = state.verification;
  const categories = state.categories;

  const sortedCategories = useMemo(() => {
    if (!categories) return [];
    return Object.entries(categories).sort((a, b) => b[1] - a[1]);
  }, [categories]);

  const maxCategoryCount = useMemo(
    () => (sortedCategories.length > 0 ? sortedCategories[0][1] : 1),
    [sortedCategories],
  );

  return (
    <>
      <LangBar currentLang={lang} availableLangs={state.languages} onSwitch={onSwitchLang} />
      <div className="text-center pt-[4vh]">
        <h1 className="text-2xl font-bold text-primary mb-2">
          {t('title', {
            state: state.code.toUpperCase(),
            state_name: state.name,
            agency: state.agency,
            pass_pct: state.passing_score_pct,
          })}
        </h1>
        <button
          onClick={onChangeState}
          aria-label="Change state"
          className="inline-flex items-center gap-1 text-primary text-sm font-semibold cursor-pointer bg-transparent border-none mb-1"
        >
          <span>{state.name}</span>
          <svg
            className="w-4 h-4"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth={2.5}
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <path d="M6 9l6 6 6-6" />
          </svg>
        </button>
        <p className="text-muted text-base mb-1 leading-relaxed">
          {t('subtitle', {
            state: state.code.toUpperCase(),
            state_name: state.name,
            agency: state.agency,
          })}
        </p>
        <p className="text-subtle text-xs mb-5">
          {t('passingScore', {
            pass_pct: state.passing_score_pct,
            pass_count: Math.ceil((state.test_question_count * state.passing_score_pct) / 100),
            test_count: state.test_question_count,
          })}
        </p>
      </div>

      {(state.source || verification) && (
        <div className="bg-surface rounded-xl border border-border mb-5 overflow-hidden">
          <button
            onClick={() => setAboutOpen((prev) => !prev)}
            aria-expanded={aboutOpen}
            className="w-full flex items-center justify-between px-4 py-3 text-sm font-semibold text-foreground bg-transparent border-none cursor-pointer"
          >
            <span>About this test</span>
            <svg
              className={`w-4 h-4 text-muted transition-transform ${aboutOpen ? 'rotate-180' : ''}`}
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth={2.5}
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <path d="M6 9l6 6 6-6" />
            </svg>
          </button>

          {aboutOpen && (
            <div className="px-4 pb-4 text-sm leading-relaxed">
              {state.source && (
                <p className="mb-2">
                  <span className="text-muted">Source: </span>
                  {verification?.manual_url ? (
                    <a
                      href={verification.manual_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-primary font-medium underline"
                    >
                      {state.source}
                    </a>
                  ) : (
                    <span className="font-medium">{state.source}</span>
                  )}
                  {verification?.edition && (
                    <span className="inline-block bg-primary-surface text-primary text-[11px] font-semibold px-2 py-0.5 rounded-full ml-1.5">
                      {verification.edition}
                    </span>
                  )}
                  <span className="text-muted"> ({state.agency})</span>
                </p>
              )}

              {verification && verification.questions_judged != null && (
                <div className="mb-3">
                  <p className="flex items-start gap-1.5 mb-1.5">
                    <span className="text-success shrink-0">&#10003;</span>
                    <span>
                      All {verification.questions_judged} questions verified against the official
                      manual
                    </span>
                  </p>
                  <div className="flex flex-wrap gap-x-3 gap-y-1 text-xs text-muted">
                    {verification.precision_grade && (
                      <span>
                        Grade{' '}
                        <span className="font-semibold text-foreground">
                          {verification.precision_grade}
                        </span>
                      </span>
                    )}
                    {verification.precision_avg_fidelity != null && (
                      <span>
                        Fidelity{' '}
                        <span className="font-semibold text-foreground tabular-nums">
                          {verification.precision_avg_fidelity}/10
                        </span>
                      </span>
                    )}
                    {verification.recall_coverage_pct != null && (
                      <span>
                        Topic coverage{' '}
                        <span className="font-semibold text-foreground tabular-nums">
                          {verification.recall_coverage_pct}%
                        </span>
                      </span>
                    )}
                    {verification.translations &&
                      Object.entries(verification.translations).map(([langCode, verdict]) => (
                        <span key={langCode}>
                          {langCode.toUpperCase()}{' '}
                          <span className={verdict === 'PASS' ? 'text-success' : 'text-error'}>
                            {verdict === 'PASS' ? '✓' : '✗'}
                          </span>
                        </span>
                      ))}
                    {verification.verified_at && (
                      <span>Verified {formatDate(verification.verified_at)}</span>
                    )}
                  </div>
                </div>
              )}

              {sortedCategories.length > 0 && (
                <div>
                  <p className="text-xs text-muted font-semibold uppercase tracking-wider mb-2">
                    Categories
                  </p>
                  {sortedCategories.map(([cat, count]) => (
                    <div key={cat} className="flex items-center gap-2 mb-1.5 text-xs">
                      <span className="w-32 shrink-0 truncate">{prettifyCategory(cat)}</span>
                      <div className="flex-1 h-2 bg-border rounded-full overflow-hidden">
                        <div
                          className="h-full bg-primary rounded-full"
                          style={{ width: `${(count / maxCategoryCount) * 100}%` }}
                        />
                      </div>
                      <span className="w-7 text-right font-semibold tabular-nums text-muted">
                        {count}
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {history.length > 0 && (
        <div className="bg-surface rounded-xl p-4 mb-5 border border-border">
          <div className="flex justify-between items-center">
            <div className="flex gap-4">
              <div className="text-center">
                <div className="text-xl font-bold tabular-nums">{history.length}</div>
                <div className="text-[11px] text-muted uppercase tracking-wide">{t('quizzes')}</div>
              </div>
              <div className="text-center">
                <div className="text-xl font-bold tabular-nums">{avg}%</div>
                <div className="text-[11px] text-muted uppercase tracking-wide">
                  {t('avgScore')}
                </div>
              </div>
              <div className="text-center">
                <div className="text-xl font-bold tabular-nums">{streak}</div>
                <div className="text-[11px] text-muted uppercase tracking-wide">
                  {t('passStreak')}
                </div>
              </div>
            </div>
            <button
              onClick={onShowStats}
              className="text-primary text-sm font-semibold cursor-pointer whitespace-nowrap"
            >
              {t('viewStats')}
            </button>
          </div>
        </div>
      )}

      <div className="flex gap-2 mb-4">
        {(['random', 'weak'] as const).map((mode) => {
          const active = quizMode === mode;
          return (
            <button
              key={mode}
              onClick={() => onSetMode(mode)}
              className={`flex-1 py-3 px-2 border-2 rounded-xl text-sm font-semibold cursor-pointer text-center transition-colors
                ${active ? 'border-primary bg-primary-surface text-primary' : 'border-border bg-surface'}`}
            >
              <span className="block mb-1">
                {mode === 'random' ? (
                  <svg
                    className="w-6 h-6 mx-auto"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth={1.5}
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  >
                    <rect x="3" y="3" width="18" height="18" rx="3" />
                    <circle cx="8.5" cy="8.5" r="1" fill="currentColor" stroke="none" />
                    <circle cx="15.5" cy="8.5" r="1" fill="currentColor" stroke="none" />
                    <circle cx="8.5" cy="15.5" r="1" fill="currentColor" stroke="none" />
                    <circle cx="15.5" cy="15.5" r="1" fill="currentColor" stroke="none" />
                  </svg>
                ) : (
                  <svg
                    className="w-6 h-6 mx-auto"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth={1.5}
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  >
                    <circle cx="12" cy="12" r="9" />
                    <circle cx="12" cy="12" r="5" />
                    <circle cx="12" cy="12" r="1" fill="currentColor" stroke="none" />
                  </svg>
                )}
              </span>
              <span>{t(mode === 'random' ? 'modeRandom' : 'modeWeak')}</span>
              {mode === 'weak' && weakCount > 0 && (
                <span className="inline-block bg-error text-on-accent text-[11px] px-1.5 rounded-full ml-1 font-bold">
                  {weakCount}
                </span>
              )}
              <span className="text-[11px] font-normal text-muted block">
                {t(mode === 'random' ? 'modeRandomDesc' : 'modeWeakDesc')}
              </span>
            </button>
          );
        })}
      </div>

      <p className="font-semibold mb-2 text-sm">{t('numQuestions')}</p>
      <div className="flex gap-2 justify-center mb-5 flex-wrap">
        {counts.map((n) => {
          const label = n === state.total_questions ? 'All' : String(n);
          const active = n === selectedCount;
          return (
            <button
              key={n}
              onClick={() => onSetCount(n)}
              className={`px-5 min-h-[44px] border-2 border-primary rounded-xl text-base font-semibold cursor-pointer transition-colors tabular-nums
                ${active ? 'bg-primary text-on-primary' : 'bg-surface text-primary hover:bg-primary-surface'}`}
            >
              {label}
            </button>
          );
        })}
      </div>

      <button
        onClick={onStart}
        disabled={startDisabled}
        className="w-full py-4 bg-primary text-on-primary rounded-xl text-lg font-semibold cursor-pointer hover:bg-primary-hover active:opacity-80 transition-colors disabled:opacity-50 disabled:cursor-default"
      >
        {startDisabled ? t('noWeakSpots') : t('startQuiz')}
      </button>
    </>
  );
}
