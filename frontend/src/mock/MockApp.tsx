import { useEffect, useState } from 'react';
import { Home } from './screens/Home';
import { StatePicker } from './screens/StatePicker';
import { Quiz } from './screens/Quiz';
import { Results } from './screens/Results';
import { Stats } from './screens/Stats';
import { Tokens } from './screens/Tokens';
import { PhoneFrame } from './PhoneFrame';

type Variant = 'light' | 'dark';
type ScreenId = 'tokens' | 'home' | 'picker' | 'quiz' | 'results' | 'stats';

const SCREENS: Record<ScreenId, (v: Variant) => React.ReactNode> = {
  tokens: () => <Tokens />,
  home: (v) => <Home variant={v} />,
  picker: (v) => <StatePicker variant={v} />,
  quiz: (v) => <Quiz variant={v} />,
  results: (v) => <Results variant={v} />,
  stats: (v) => <Stats variant={v} />,
};

function parseHash(): { screen: ScreenId | 'index'; variant: Variant } {
  const h = window.location.hash.replace(/^#\/?/, '');
  if (!h) return { screen: 'index', variant: 'light' };
  const [s, v] = h.split('/');
  const screen = (s as ScreenId) in SCREENS ? (s as ScreenId) : 'index';
  const variant: Variant = v === 'dark' ? 'dark' : 'light';
  return { screen: screen as ScreenId | 'index', variant };
}

export function MockApp() {
  const [{ screen, variant }, setRoute] = useState(parseHash());

  useEffect(() => {
    const onHash = () => setRoute(parseHash());
    window.addEventListener('hashchange', onHash);
    return () => window.removeEventListener('hashchange', onHash);
  }, []);

  if (screen === 'index') return <Index />;

  if (screen === 'tokens') {
    return (
      <div className="min-h-screen bg-surface-light px-xl py-2xl">
        <Tokens />
      </div>
    );
  }

  return (
    <div
      className={
        variant === 'dark'
          ? 'min-h-screen bg-black flex items-center justify-center'
          : 'min-h-screen bg-slate-100 flex items-center justify-center'
      }
    >
      <PhoneFrame variant={variant}>{SCREENS[screen](variant)}</PhoneFrame>
    </div>
  );
}

function Index() {
  const links: { href: string; label: string }[] = [
    { href: '#/tokens', label: '00 · Design tokens (palette / type / spacing)' },
    { href: '#/home/light', label: '01 · Home — light' },
    { href: '#/picker/light', label: '02 · State picker — light' },
    { href: '#/quiz/light', label: '03 · Quiz — light' },
    { href: '#/quiz/dark', label: '04 · Quiz — dark' },
    { href: '#/results/light', label: '05 · Results — light' },
    { href: '#/stats/light', label: '06 · Stats — light' },
  ];
  return (
    <div className="min-h-screen bg-surface-light p-2xl font-body text-ink">
      <h1 className="font-display text-4xl font-semibold mb-md">polish-ui-official-look</h1>
      <p className="text-ink-muted mb-xl">Mock screens for design review.</p>
      <ul className="space-y-sm">
        {links.map((l) => (
          <li key={l.href}>
            <a className="text-primary font-medium hover:underline" href={l.href}>
              {l.label}
            </a>
          </li>
        ))}
      </ul>
    </div>
  );
}
