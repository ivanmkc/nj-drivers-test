import Foundation
import SwiftUI

@MainActor
class QuizViewModel: ObservableObject {
    @Published var screen: AppScreen = .statePicker
    @Published var allStates: [StateInfo] = []
    @Published var currentState: StateInfo?
    @Published private var cachedStore: QuizStore?
    private var cachedStoreCode: String?

    // Quiz state
    @Published var questions: [QuizQuestion] = []
    @Published var currentIndex = 0
    @Published var correctCount = 0
    @Published var wrongCount = 0
    @Published var answered = false
    @Published var selectedAnswer: String?
    @Published var correctAnswer: String?
    @Published var explanation: String?
    @Published var sessionResults: [SessionResult] = []

    // Settings
    @Published var quizMode: QuizMode = .random
    @Published var selectedCount = 50

    private let localizer = Localizer.shared
    private let api = ApiClient.shared
    private let storage = LocalStore.shared

    var store: QuizStore {
        guard let state = currentState else { return .empty }
        if cachedStoreCode == state.code, let cached = cachedStore {
            return cached
        }
        let loaded = storage.loadStore(for: state.code)
        cachedStore = loaded
        cachedStoreCode = state.code
        return loaded
    }

    private func invalidateStoreCache() {
        cachedStore = nil
        cachedStoreCode = nil
    }

    var weakQuestions: [WeakQuestion] {
        guard let state = currentState else { return [] }
        return storage.getWeakQuestions(for: state.code)
    }

    var quizHistory: [QuizHistoryEntry] {
        store.history
    }

    var averageScore: Int {
        let h = quizHistory
        guard !h.isEmpty else { return 0 }
        return Int(h.map { Double($0.pct) }.reduce(0, +) / Double(h.count))
    }

    var passStreak: Int {
        guard let state = currentState else { return 0 }
        let h = quizHistory
        var streak = 0
        for entry in h.reversed() {
            if entry.pct >= state.passingScorePct { streak += 1 } else { break }
        }
        return streak
    }

    var bestScore: Int {
        quizHistory.map(\.pct).max() ?? 0
    }

    var questionsSeen: Int {
        store.questions.count
    }

    var countOptions: [Int] {
        guard let state = currentState else { return [10, 25, 50] }
        let total = state.totalQuestions
        var counts = [10, 25, 50, 100].filter { $0 <= total }
        if !counts.contains(total) { counts.append(total) }
        return counts
    }

    var currentQuestion: QuizQuestion? {
        guard currentIndex < questions.count else { return nil }
        return questions[currentIndex]
    }

    var resultPct: Int {
        guard !questions.isEmpty else { return 0 }
        return Int(round(Double(correctCount) / Double(questions.count) * 100))
    }

    var didPass: Bool {
        guard let state = currentState else { return false }
        return resultPct >= state.passingScorePct
    }

    var wrongResults: [SessionResult] {
        sessionResults.filter { !$0.correct }
    }

    var categoryStats: [(category: String, pct: Int)] {
        var cats: [String: (seen: Int, correct: Int)] = [:]
        for (_, record) in store.questions {
            let cat = record.category.isEmpty ? "unknown" : record.category
            var entry = cats[cat] ?? (seen: 0, correct: 0)
            entry.seen += record.seen
            entry.correct += record.seen - record.wrong
            cats[cat] = entry
        }
        return cats.map { (category: $0.key, pct: $0.value.seen > 0 ? Int(round(Double($0.value.correct) / Double($0.value.seen) * 100)) : 0) }
            .sorted { $0.pct < $1.pct }
    }

    func questionMissInfo(_ questionId: Int) -> (wrong: Int, seen: Int)? {
        guard let record = store.questions[String(questionId)], record.wrong > 0 else { return nil }
        return (record.wrong, record.seen)
    }

    // MARK: - Actions

    func loadStates() {
        allStates = api.fetchStates()
        if let savedCode = storage.savedStateCode,
           let saved = allStates.first(where: { $0.code == savedCode && $0.hasQuestions }) {
            currentState = saved
            invalidateStoreCache()
            selectedCount = min(50, saved.totalQuestions)
            screen = .home
        }
    }

    func selectState(_ state: StateInfo) {
        currentState = state
        invalidateStoreCache()
        storage.savedStateCode = state.code
        selectedCount = min(50, state.totalQuestions)
        quizMode = .random
        screen = .home
    }

    func goStatePicker() {
        screen = .statePicker
    }

    func goHome() {
        quizMode = .random
        screen = .home
    }

    func startQuiz() {
        guard let state = currentState else { return }

        if quizMode == .weak {
            let weak = weakQuestions
            guard !weak.isEmpty else { return }
            let count = min(selectedCount, weak.count)
            let weakIds = Set(weak.prefix(count).map(\.id))
            let all = api.fetchQuiz(state: state.code, lang: localizer.currentLang, count: state.totalQuestions)
            questions = all.filter { weakIds.contains($0.id) }.shuffled().prefix(count).map { $0 }
        } else {
            questions = api.fetchQuiz(state: state.code, lang: localizer.currentLang, count: selectedCount)
        }
        currentIndex = 0
        correctCount = 0
        wrongCount = 0
        sessionResults = []
        answered = false
        selectedAnswer = nil
        correctAnswer = nil
        explanation = nil
        screen = .quiz
    }

    func selectAnswer(_ letter: String) {
        guard !answered, let q = currentQuestion, let state = currentState else { return }
        answered = true
        selectedAnswer = letter

        guard let response = api.fetchAnswer(questionId: q.id, state: state.code, lang: localizer.currentLang) else {
            return
        }
        correctAnswer = response.answer
        explanation = response.explanation
        let isCorrect = letter == response.answer

        if isCorrect { correctCount += 1 } else { wrongCount += 1 }

        var s = storage.loadStore(for: state.code)
        let idStr = String(q.id)
        var record = s.questions[idStr] ?? QuestionRecord(seen: 0, wrong: 0, category: q.category)
        record.seen += 1
        if !isCorrect { record.wrong += 1 }
        s.questions[idStr] = record
        storage.saveStore(s, for: state.code)
        invalidateStoreCache()

        sessionResults.append(SessionResult(
            id: q.id,
            question: q.question,
            yourAnswer: letter,
            yourAnswerText: q.choices[letter] ?? "",
            correctAnswer: response.answer,
            correctAnswerText: q.choices[response.answer] ?? "",
            correct: isCorrect,
            explanation: response.explanation
        ))
    }

    func nextQuestion() {
        currentIndex += 1
        if currentIndex >= questions.count {
            finishQuiz()
            return
        }
        answered = false
        selectedAnswer = nil
        correctAnswer = nil
        explanation = nil
    }

    private func finishQuiz() {
        guard let state = currentState else { return }
        var s = storage.loadStore(for: state.code)
        s.history.append(QuizHistoryEntry(
            date: Date(),
            correct: correctCount,
            total: questions.count,
            pct: resultPct,
            mode: quizMode.rawValue
        ))
        storage.saveStore(s, for: state.code)
        invalidateStoreCache()
        screen = .results
    }

    func showStats() {
        screen = .stats
    }

    func clearData() {
        guard let state = currentState else { return }
        storage.clearStore(for: state.code)
        invalidateStoreCache()
        objectWillChange.send()
        screen = .home
    }
}
