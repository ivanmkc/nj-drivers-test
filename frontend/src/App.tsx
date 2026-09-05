import { useState, useEffect, useCallback, useMemo, useRef } from 'react';
import type {
  StateIndexEntry,
  StateSummary,
  Question,
  Screen,
  QuizMode,
  SessionResult,
} from './types';
import { loadI18n, getLang, setLang, t } from './i18n';
import { loadIndex, loadQuestions, prefetchQuestions } from './data';
import { useStore } from './hooks/useStore';
import { shuffleArray } from './utils';
import { DEFAULT_QUESTION_COUNT } from './constants';
import LoadingScreen from './components/LoadingScreen';
import StatePicker from './components/StatePicker';
import StartScreen from './components/StartScreen';
import QuizScreen from './components/QuizScreen';
import ResultsScreen from './components/ResultsScreen';
import StatsScreen from './components/StatsScreen';

const BASE = import.meta.env.BASE_URL;

export default function App() {
  const [screen, setScreen] = useState<Screen>('loading');
  const [allStates, setAllStates] = useState<StateSummary[]>([]);
  const [enQuestions, setEnQuestions] = useState<Question[]>([]);
  const [stateLoading, setStateLoading] = useState(false);
  const [currentState, setCurrentState] = useState<StateSummary | null>(null);
  const [lang, setLangState] = useState(getLang());
  const [quizMode, setQuizMode] = useState<QuizMode>('random');
  const [selectedCount, setSelectedCount] = useState(DEFAULT_QUESTION_COUNT);
  const [questions, setQuestions] = useState<Question[]>([]);
  const [currentIdx, setCurrentIdx] = useState(0);
  const [sessionResults, setSessionResults] = useState<SessionResult[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [statsEnteredFromResults, setStatsEnteredFromResults] = useState(false);

  const correctCount = useMemo(
    () => sessionResults.filter((r) => r.correct).length,
    [sessionResults],
  );
  const wrongCount = useMemo(
    () => sessionResults.filter((r) => !r.correct).length,
    [sessionResults],
  );

  const store = useStore(currentState?.code ?? null);

  const isPoppingState = useRef(false);

  const navigateTo = useCallback((target: Screen) => {
    setScreen(target);
    if (!isPoppingState.current) {
      window.history.pushState({ screen: target }, '');
    }
  }, []);

  useEffect(() => {
    window.history.replaceState({ screen }, '');

    const handlePopState = (e: PopStateEvent) => {
      const target: Screen | undefined = e.state?.screen;
      isPoppingState.current = true;

      if (target === 'quiz' || target === 'results') {
        setScreen('start');
        setQuizMode('random');
      } else if (target) {
        setScreen(target);
      } else {
        setScreen('state-picker');
      }

      isPoppingState.current = false;
    };

    window.addEventListener('popstate', handlePopState);
    return () => window.removeEventListener('popstate', handlePopState);
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  // Load the i18n strings and the state index (metadata only). Question
  // banks are fetched per state + language when needed, see data.ts.
  useEffect(() => {
    Promise.all([loadI18n(BASE), loadIndex(BASE)])
      .then(([, index]) => {
        const states: StateSummary[] = index.states.map((s: StateIndexEntry) => ({
          code: s.code,
          name: s.name,
          agency: s.agency,
          passing_score_pct: s.passing_score_pct,
          test_question_count: s.test_question_count,
          languages: Object.keys(s.languages),
          total_questions: s.languages.en ?? 0,
          source: s.source,
          categories: s.categories,
          verification: s.verification,
          official_test_languages: s.official_test_languages,
        }));
        setAllStates(states);

        const saved = localStorage.getItem('quiz_state');
        if (saved) {
          const s = states.find((st) => st.code === saved && st.total_questions > 0);
          if (s) {
            setCurrentState(s);
            prefetchQuestions(BASE, s.code, [getLang(), 'en']);
            navigateTo('start');
            return;
          }
        }
        navigateTo('state-picker');
      })
      .catch((err) => {
        setError(err instanceof Error ? err.message : 'Failed to load application data');
      });
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  const switchLang = useCallback((newLang: string) => {
    setLang(newLang);
    setLangState(newLang);
  }, []);

  const selectState = useCallback(
    (code: string) => {
      const s = allStates.find((st) => st.code === code);
      if (s) {
        setCurrentState(s);
        localStorage.setItem('quiz_state', code);
        prefetchQuestions(BASE, code, [lang, 'en']);
        navigateTo('start');
        setQuizMode('random');
      }
    },
    [allStates, lang, navigateTo],
  );

  const startQuiz = useCallback(async () => {
    if (!currentState) return;
    // Fall back to English when the state has no bank in the UI language.
    const bankLang = currentState.languages.includes(lang) ? lang : 'en';
    setStateLoading(true);
    let allQs: Question[];
    let enQs: Question[];
    try {
      // The English bank is always needed: manual excerpts attach to it.
      [allQs, enQs] = await Promise.all([
        loadQuestions(BASE, currentState.code, bankLang),
        loadQuestions(BASE, currentState.code, 'en'),
      ]);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load questions');
      return;
    } finally {
      setStateLoading(false);
    }
    setEnQuestions(enQs);

    let qs: Question[];
    if (quizMode === 'weak') {
      const storeData = store.load();
      const weakIds = Object.entries(storeData.questions)
        .filter(([, d]) => d.wrong > 0 && d.seen >= 1)
        .sort((a, b) => b[1].wrong / b[1].seen - a[1].wrong / a[1].seen)
        .map(([id]) => parseInt(id));
      const idSet = new Set(weakIds.slice(0, selectedCount));
      qs = shuffleArray(allQs.filter((q) => idSet.has(q.id))).slice(0, selectedCount);
    } else {
      qs = shuffleArray(allQs).slice(0, Math.min(selectedCount, allQs.length));
    }

    setQuestions(qs);
    setCurrentIdx(0);
    setSessionResults([]);
    navigateTo('quiz');
  }, [currentState, lang, quizMode, selectedCount, store, navigateTo]);

  const recordAnswer = useCallback(
    (result: SessionResult, isCorrect: boolean) => {
      setSessionResults((prev) => [...prev, result]);

      const storeData = store.load();
      const qId = String(result.id);
      if (!storeData.questions[qId]) {
        storeData.questions[qId] = { seen: 0, wrong: 0, category: result.category };
      }
      if (!storeData.questions[qId].category) {
        storeData.questions[qId].category = result.category;
      }
      storeData.questions[qId].seen++;
      if (!isCorrect) storeData.questions[qId].wrong++;
      store.save(storeData);
    },
    [store],
  );

  const finishQuiz = useCallback(() => {
    const pct = Math.round((correctCount / questions.length) * 100);
    const storeData = store.load();
    storeData.history.push({
      date: new Date().toISOString(),
      correct: correctCount,
      total: questions.length,
      pct,
      mode: quizMode,
    });
    store.save(storeData);
    navigateTo('results');
  }, [correctCount, questions.length, store, quizMode, navigateTo]);

  const goHome = useCallback(() => {
    navigateTo('start');
    setQuizMode('random');
  }, [navigateTo]);

  const enQuestionsMap = useMemo(() => new Map(enQuestions.map((q) => [q.id, q])), [enQuestions]);

  if (error) {
    return (
      <div className="max-w-lg mx-auto px-4 py-20 text-center">
        <div className="text-error text-lg font-semibold mb-2">Failed to load</div>
        <div className="text-muted text-base mb-4">{error}</div>
        <button
          onClick={() => window.location.reload()}
          className="px-6 py-2 bg-primary text-on-primary rounded-xl text-sm font-semibold cursor-pointer hover:bg-primary-hover transition-colors"
        >
          Retry
        </button>
      </div>
    );
  }

  if (screen === 'loading' || stateLoading) return <LoadingScreen />;

  return (
    <div className="max-w-lg mx-auto px-4 py-4">
      {screen === 'state-picker' && (
        <StatePicker
          states={allStates}
          lang={lang}
          onSelectState={selectState}
          onSwitchLang={switchLang}
        />
      )}
      {screen === 'start' && currentState && (
        <StartScreen
          state={currentState}
          lang={lang}
          quizMode={quizMode}
          selectedCount={selectedCount}
          store={store}
          onSetMode={setQuizMode}
          onSetCount={setSelectedCount}
          onStart={startQuiz}
          onChangeState={() => navigateTo('state-picker')}
          onShowStats={() => {
            setStatsEnteredFromResults(false);
            navigateTo('stats');
          }}
          onSwitchLang={switchLang}
        />
      )}
      {screen === 'quiz' && currentState && questions.length > 0 && (
        <QuizScreen
          question={questions[currentIdx]}
          currentIdx={currentIdx}
          totalQuestions={questions.length}
          correctCount={correctCount}
          wrongCount={wrongCount}
          store={store}
          basePath={BASE}
          enQuestionsMap={enQuestionsMap}
          sourceName={currentState.source}
          onAnswer={recordAnswer}
          onNext={
            currentIdx + 1 >= questions.length ? finishQuiz : () => setCurrentIdx((i) => i + 1)
          }
          onExit={goHome}
        />
      )}
      {screen === 'results' && currentState && (
        <ResultsScreen
          correctCount={correctCount}
          totalQuestions={questions.length}
          passingPct={currentState.passing_score_pct}
          agency={currentState.agency}
          sessionResults={sessionResults}
          onNewQuiz={goHome}
          onShowStats={() => {
            setStatsEnteredFromResults(true);
            navigateTo('stats');
          }}
        />
      )}
      {screen === 'stats' && currentState && (
        <StatsScreen
          state={currentState}
          store={store}
          onBack={statsEnteredFromResults ? () => navigateTo('results') : goHome}
        />
      )}
      {(screen === 'state-picker' || screen === 'start') && (
        <footer className="mt-10 pb-6 text-center text-xs text-subtle">
          <p className="mb-2">{t('footerDisclaimer')}</p>
          <nav className="flex justify-center gap-4">
            <a className="underline hover:text-muted" href={`${BASE}about/`}>
              {t('footerAbout')}
            </a>
            <a className="underline hover:text-muted" href={`${BASE}privacy/`}>
              {t('footerPrivacy')}
            </a>
            <a className="underline hover:text-muted" href={`${BASE}support/`}>
              {t('footerSupport')}
            </a>
          </nav>
        </footer>
      )}
    </div>
  );
}
