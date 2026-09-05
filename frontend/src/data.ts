import type { DataIndex, Question } from './types';

// One in-flight/completed request per (state, language). A rejected request
// is evicted so a retry actually re-fetches.
const banks = new Map<string, Promise<Question[]>>();

export async function loadIndex(base: string): Promise<DataIndex> {
  const res = await fetch(`${base}data/index.json`);
  if (!res.ok) throw new Error(`Failed to load state index: ${res.status}`);
  return res.json();
}

export function loadQuestions(base: string, code: string, lang: string): Promise<Question[]> {
  const key = `${code}/${lang}`;
  const cached = banks.get(key);
  if (cached) return cached;
  const p = fetch(`${base}data/states/${code}/${lang}.json`).then((res) => {
    if (!res.ok) throw new Error(`Failed to load ${code}/${lang} questions: ${res.status}`);
    return res.json() as Promise<Question[]>;
  });
  p.catch(() => banks.delete(key));
  banks.set(key, p);
  return p;
}

/** Warm the cache for a state so Start Quiz is instant; failures are ignored. */
export function prefetchQuestions(base: string, code: string, langs: string[]): void {
  for (const lang of langs) {
    loadQuestions(base, code, lang).catch(() => undefined);
  }
}
