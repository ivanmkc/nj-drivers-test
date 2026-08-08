export interface Question {
  id: number;
  category: string;
  question: string;
  choices: Record<string, string>;
  answer: string;
  explanation: string;
  image?: string;
  evidence?: string[];
}

export interface StateVerification {
  verified_at?: string;
  overall?: string;
  manual_url?: string;
  edition?: string;
  manual_pages?: number;
  precision_avg_fidelity?: number;
  precision_grade?: string;
  questions_judged?: number;
  recall_coverage_pct?: number;
  translations?: Record<string, string>;
}

export interface StateConfig {
  code: string;
  name: string;
  agency: string;
  passing_score_pct: number;
  test_question_count: number;
  source?: string;
  categories?: Record<string, number>;
  verification?: StateVerification;
  languages: Record<string, Question[]>;
}

export interface Bundle {
  states: StateConfig[];
}

export interface StateSummary {
  code: string;
  name: string;
  agency: string;
  passing_score_pct: number;
  test_question_count: number;
  languages: string[];
  total_questions: number;
  source?: string;
  categories?: Record<string, number>;
  verification?: StateVerification;
}

export interface QuizStore {
  history: QuizResult[];
  questions: Record<string, QuestionStats>;
}

export interface QuizResult {
  date: string;
  correct: number;
  total: number;
  pct: number;
  mode: QuizMode;
}

export interface QuestionStats {
  seen: number;
  wrong: number;
  category: string;
}

export interface SessionResult {
  id: number;
  question: string;
  yourAnswer: string;
  yourAnswerText: string;
  correctAnswer: string;
  correctAnswerText: string;
  correct: boolean;
  explanation: string;
}

export type Screen = 'loading' | 'state-picker' | 'start' | 'quiz' | 'results' | 'stats';
export type QuizMode = 'random' | 'weak';
