import { useState, useMemo } from 'react';
import type { StateSummary } from '../types';
import { t } from '../i18n';
import { useStore } from '../hooks/useStore';
import { calcPassStreak, calcAverageScore } from '../utils';
import { MAX_WEAK_DISPLAY, GOOD_ACCURACY_PCT, FAIR_ACCURACY_PCT } from '../constants';
import ScoreChart from './ScoreChart';

interface StatsScreenProps {
  state: StateSummary;
  store: ReturnType<typeof useStore>;
  onBack: () => void;
}

export default function StatsScreen({ state, store, onBack }: StatsScreenProps) {
  const [storeData] = useState(() => store.load());
  const history = storeData.history;

  const avg = calcAverageScore(history);
  const best = history.length ? Math.max(...history.map((r) => r.pct)) : 0;
  const seen = Object.keys(storeData.questions).length;
  const streak = calcPassStreak(history, state.passing_score_pct);

  const catStats = useMemo(() => {
    const stats: Record<string, { seen: number; correct: number }> = {};
    for (const data of Object.values(storeData.questions)) {
      const cat = data.category || 'unknown';
      if (!stats[cat]) stats[cat] = { seen: 0, correct: 0 };
      stats[cat].seen += data.seen;
      stats[cat].correct += data.seen - data.wrong;
    }
    return Object.entries(stats).sort(
      (a, b) => a[1].correct / a[1].seen - b[1].correct / b[1].seen,
    );
  }, [storeData]);

  const weakIds = useMemo(() => {
    return Object.entries(storeData.questions)
      .filter(([, d]) => d.wrong > 0 && d.seen >= 1)
      .map(([id, d]) => ({
        id: parseInt(id),
        missRate: d.wrong / d.seen,
        wrong: d.wrong,
        seen: d.seen,
        category: d.category,
      }))
      .sort((a, b) => b.missRate - a.missRate || b.wrong - a.wrong);
  }, [storeData]);

  const handleClear = () => {
    if (confirm(t('resetConfirm', { state_name: state.name }))) {
      store.clear();
      onBack();
    }
  };

  return (
    <div className="pt-4">
      <button
        onClick={onBack}
        className="inline-flex items-center gap-1.5 text-blue-600 text-sm font-semibold cursor-pointer mb-5 bg-transparent border-none"
      >
        <span>&larr;</span> <span>{t('back')}</span>
      </button>
      <div className="text-xl font-bold mb-5">{t('yourProgress')}</div>

      <div className="grid grid-cols-3 gap-2.5 mb-6">
        <div className="bg-white rounded-xl py-4 px-3 text-center border border-gray-200">
          <div className="text-2xl font-bold text-blue-600">{history.length}</div>
          <div className="text-[11px] text-gray-500 uppercase tracking-wide mt-1">
            {t('quizzes')}
          </div>
        </div>
        <div className="bg-white rounded-xl py-4 px-3 text-center border border-gray-200">
          <div className="text-2xl font-bold text-green-600">{avg}%</div>
          <div className="text-[11px] text-gray-500 uppercase tracking-wide mt-1">
            {t('avgScore')}
          </div>
        </div>
        <div className="bg-white rounded-xl py-4 px-3 text-center border border-gray-200">
          <div className="text-2xl font-bold">{seen}</div>
          <div className="text-[11px] text-gray-500 uppercase tracking-wide mt-1">
            {t('qsSeen')}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-2.5 mb-6">
        <div className="bg-white rounded-xl py-4 px-3 text-center border border-gray-200">
          <div className="text-2xl font-bold text-green-600">{streak}</div>
          <div className="text-[11px] text-gray-500 uppercase tracking-wide mt-1">
            {t('passStreak')}
          </div>
        </div>
        <div className="bg-white rounded-xl py-4 px-3 text-center border border-gray-200">
          <div className="text-2xl font-bold">{best}%</div>
          <div className="text-[11px] text-gray-500 uppercase tracking-wide mt-1">
            {t('bestScore')}
          </div>
        </div>
      </div>

      <div className="bg-white rounded-xl p-4 mb-6 border border-gray-200">
        <h4 className="text-sm font-semibold mb-3">{t('scoreHistory')}</h4>
        {history.length >= 2 ? (
          <ScoreChart history={history} passingPct={state.passing_score_pct} />
        ) : (
          <div className="h-28 flex items-center justify-center text-gray-400 text-sm text-center">
            {history.length === 0 ? t('chartEmpty') : t('chartOneMore')}
          </div>
        )}
      </div>

      {catStats.length > 0 && (
        <div className="mb-6">
          <h4 className="text-sm font-semibold mb-3">{t('accuracyByCategory')}</h4>
          {catStats.map(([cat, data]) => {
            const pct = Math.round((data.correct / data.seen) * 100);
            const color =
              pct >= GOOD_ACCURACY_PCT
                ? '#16a34a'
                : pct >= FAIR_ACCURACY_PCT
                  ? '#ea580c'
                  : '#dc2626';
            return (
              <div key={cat} className="flex items-center gap-2.5 mb-2 text-xs">
                <span className="w-28 shrink-0 capitalize truncate">{cat.replace(/_/g, ' ')}</span>
                <div className="flex-1 h-2.5 bg-gray-200 rounded-full overflow-hidden">
                  <div
                    className="h-full rounded-full"
                    style={{ width: `${pct}%`, background: color }}
                  />
                </div>
                <span className="w-9 text-right font-semibold" style={{ color }}>
                  {pct}%
                </span>
              </div>
            );
          })}
        </div>
      )}

      {weakIds.length > 0 && (
        <div className="mb-6">
          <h4 className="text-sm font-semibold mb-3">{t('mostMissed')}</h4>
          {weakIds.slice(0, MAX_WEAK_DISPLAY).map((w) => (
            <div
              key={w.id}
              className="bg-white rounded-xl py-3 px-3.5 mb-2 border border-gray-200 border-l-4 border-l-orange-500"
            >
              <div className="text-sm font-semibold mb-1">Q{w.id}</div>
              <div className="text-xs text-gray-500">
                {t('missed')}{' '}
                <span className="text-red-600 font-semibold">
                  {w.wrong}/{w.seen} ({Math.round(w.missRate * 100)}%)
                </span>{' '}
                &middot; {(w.category || '').replace(/_/g, ' ')}
              </div>
            </div>
          ))}
        </div>
      )}

      <div className="border-t border-gray-200 pt-5 mt-2">
        <button
          onClick={handleClear}
          className="w-full py-3 bg-white text-red-600 border-2 border-red-100 rounded-xl text-sm font-semibold cursor-pointer hover:bg-red-50 active:bg-red-100 transition-colors"
        >
          {t('resetAll')}
        </button>
      </div>
    </div>
  );
}
