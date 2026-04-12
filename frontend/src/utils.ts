import type { QuizResult } from './types';

export function calcPassStreak(history: QuizResult[], passingPct: number): number {
  let streak = 0;
  for (let i = history.length - 1; i >= 0; i--) {
    if (history[i].pct >= passingPct) streak++;
    else break;
  }
  return streak;
}

export function calcAverageScore(history: QuizResult[]): number {
  if (!history.length) return 0;
  return Math.round(history.reduce((s, r) => s + r.pct, 0) / history.length);
}

export function shuffleArray<T>(arr: T[]): T[] {
  const a = [...arr];
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}
