import { useCallback } from 'react'
import type { QuizStore } from '../types'

export function useStore(stateCode: string | null) {
  const key = stateCode ? `quiz_${stateCode}` : null

  const load = useCallback((): QuizStore => {
    if (!key) return { history: [], questions: {} }
    try {
      const raw = localStorage.getItem(key)
      if (raw) return JSON.parse(raw)
    } catch {}
    return { history: [], questions: {} }
  }, [key])

  const save = useCallback((store: QuizStore) => {
    if (key) localStorage.setItem(key, JSON.stringify(store))
  }, [key])

  const clear = useCallback(() => {
    if (key) localStorage.removeItem(key)
  }, [key])

  return { load, save, clear }
}
