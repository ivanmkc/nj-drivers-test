import { useState, useEffect, useCallback, useMemo } from 'react';

export type ThemeMode = 'system' | 'light' | 'dark';

const STORAGE_KEY = 'theme';
const SYNC_EVENT = 'theme-change';

function getSystemDark(): boolean {
  return window.matchMedia('(prefers-color-scheme: dark)').matches;
}

function resolve(mode: ThemeMode): 'light' | 'dark' {
  return mode === 'system' ? (getSystemDark() ? 'dark' : 'light') : mode;
}

function apply(resolved: 'light' | 'dark') {
  document.documentElement.classList.toggle('dark', resolved === 'dark');
  const meta = document.querySelector('meta[name="theme-color"]');
  if (meta) {
    meta.setAttribute('content', resolved === 'dark' ? '#111827' : '#1a56db');
  }
}

function readStored(): ThemeMode {
  const stored = localStorage.getItem(STORAGE_KEY);
  return stored === 'light' || stored === 'dark' ? stored : 'system';
}

export function useTheme() {
  const [mode, setMode] = useState<ThemeMode>(readStored);
  const [resolved, setResolved] = useState<'light' | 'dark'>(() => resolve(readStored()));

  useEffect(() => {
    const r = resolve(mode);
    setResolved(r);
    apply(r);
    if (mode === 'system') {
      localStorage.removeItem(STORAGE_KEY);
    } else {
      localStorage.setItem(STORAGE_KEY, mode);
    }
  }, [mode]);

  useEffect(() => {
    const handler = () => {
      const m = readStored();
      setMode(m);
      const r = resolve(m);
      setResolved(r);
      apply(r);
    };
    window.addEventListener(SYNC_EVENT, handler);
    return () => window.removeEventListener(SYNC_EVENT, handler);
  }, []);

  useEffect(() => {
    if (mode !== 'system') return;
    const mql = window.matchMedia('(prefers-color-scheme: dark)');
    const handler = () => {
      const r = resolve('system');
      setResolved(r);
      apply(r);
    };
    mql.addEventListener('change', handler);
    return () => mql.removeEventListener('change', handler);
  }, [mode]);

  const cycle = useCallback(() => {
    setMode((prev) => {
      const next: ThemeMode = prev === 'system' ? 'light' : prev === 'light' ? 'dark' : 'system';
      if (next === 'system') {
        localStorage.removeItem(STORAGE_KEY);
      } else {
        localStorage.setItem(STORAGE_KEY, next);
      }
      window.dispatchEvent(new Event(SYNC_EVENT));
      return next;
    });
  }, []);

  return useMemo(() => ({ mode, resolved, cycle }), [mode, resolved, cycle]);
}
