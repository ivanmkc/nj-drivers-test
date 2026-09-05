import { useState, useEffect, useCallback, useMemo, useRef } from 'react';
import type {
  Bundle,
  StateConfig,
  StateSummary,
  Question,
  Screen,
  QuizMode,
  SessionResult,
} from './types';
import { loadI18n, getLang, setLang } from './i18n';
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
  const [bundle, setBundle] = useState<Bundle | null>(null);
  const [allStates, setAllStates] = useState<StateSummary[]>([]);
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

  // Load bundle and i18n
  useEffect(() => {
    Promise.all([
      loadI18n(BASE),
      fetch(`${BASE}questions_bundle.json`).then((r) => {
        if (!r.ok) throw new Error(`Failed to load questions: ${r.status}`);
        return r.json();
      }),
    ])
      .then(([, bundleData]) => {
        setBundle(bundleData);
        const states: StateSummary[] = bundleData.states.map((s: StateConfig) => ({
          code: s.code,
          name: s.name,
          agency: s.agency,
          passing_score_pct: s.passing_score_pct,
          test_question_count: s.test_question_count,
          languages: Object.keys(s.languages),
          total_questions: (s.languages.en || []).length,
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
        navigateTo('start');
        setQuizMode('random');
      }
    },
    [allStates, navigateTo],
  );

  const getQuestions = useCallback(
    (stateCode: string, language: string): Question[] => {
      if (!bundle) return [];
      const sd = bundle.states.find((s) => s.code === stateCode);
      if (!sd) return [];
      return sd.languages[language] || sd.languages['en'] || [];
    },
    [bundle],
  );

  const startQuiz = useCallback(() => {
    if (!currentState) return;
    let qs: Question[];
    const allQs = getQuestions(currentState.code, lang);

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
  }, [currentState, lang, quizMode, selectedCount, getQuestions, store, navigateTo]);

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

  const enQuestionsMap = useMemo(() => {
    if (!bundle || !currentState) return new Map<number, Question>();
    const sd = bundle.states.find((s) => s.code === currentState.code);
    if (!sd) return new Map<number, Question>();
    const enQs = sd.languages['en'] || [];
    return new Map(enQs.map((q) => [q.id, q]));
  }, [bundle, currentState]);

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

  if (screen === 'loading') return <LoadingScreen />;

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
    </div>
  );
}
