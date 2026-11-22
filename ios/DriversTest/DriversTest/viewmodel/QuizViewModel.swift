import Foundation
import SwiftUI

@MainActor
class QuizViewModel: ObservableObject {
    @Published var screen: AppScreen = .statePicker
    @Published var allStates: [StateInfo] = []
    @Published var currentState: StateInfo?
    private var cachedStore: QuizStore?
    private var cachedStoreCode: String?
    private var cachedLanguage: String?
    @Published var showStudyWarning = false
    @Published var showLegacyStats = false

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
    @Published var isLoading = true
    @Published var loadError: String?
    @Published var quizError: String?
    @Published var languageFallbackNotice: String?

    private let localizer: Localizer
    private let api: ApiClient
    private let storage: LocalStore

    init(api: ApiClient = .shared, storage: LocalStore = .shared, localizer: Localizer = .shared) {
        self.api = api
        self.storage = storage
        self.localizer = localizer
    }

    var store: QuizStore {
        guard let state = currentState else { return .empty }
        if showLegacyStats && screen == .stats { return storage.loadStore(for: state.code) }
        if cachedStoreCode == state.code, cachedLanguage == localizer.currentLang, let cached = cachedStore {
            return cached
        }
        let loaded = storage.loadStore(for: state.code, language: localizer.currentLang)
        cachedStore = loaded
        cachedStoreCode = state.code
        cachedLanguage = localizer.currentLang
        return loaded
    }

    private func invalidateStoreCache() {
        cachedStore = nil
        cachedStoreCode = nil
        cachedLanguage = nil
        cachedWeakQuestions = nil
        cachedWeakQuestionsCode = nil
    }

    private func updateStoreCache(_ s: QuizStore) {
        cachedStore = s
        cachedStoreCode = currentState?.code
        cachedLanguage = localizer.currentLang
        cachedWeakQuestions = nil
        cachedWeakQuestionsCode = nil
    }

    private var cachedWeakQuestions: [WeakQuestion]?
    private var cachedWeakQuestionsCode: String?
    private var cachedWeakLanguage: String?

    var weakQuestions: [WeakQuestion] {
        guard let state = currentState else { return [] }
        if showLegacyStats && screen == .stats { return storage.getWeakQuestions(for: state.code) }
        if cachedWeakQuestionsCode == state.code, cachedWeakLanguage == localizer.currentLang, let cached = cachedWeakQuestions {
            return cached
        }
        let result = storage.getWeakQuestions(for: state.code, language: localizer.currentLang)
        cachedWeakQuestions = result
        cachedWeakQuestionsCode = state.code
        cachedWeakLanguage = localizer.currentLang
        return result
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
        return !questions.isEmpty && correctCount * 100 >= questions.count * state.passingScorePct
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

    func evidenceForCurrentQuestion() -> [String]? {
        guard answered, let q = currentQuestion, let state = currentState else { return nil }
        return api.fetchEvidence(questionId: q.id, state: state.code)
    }

    // MARK: - Actions

    func loadStates() {
        Task {
            isLoading = true
            loadError = nil

            do {
                try await Task.detached {
                    try ApiClient.shared.loadBundle()
                }.value
            } catch {
                loadError = error.localizedDescription
                isLoading = false
                return
            }

            allStates = api.fetchStates()
            // UI tests pass --uitest-reset so every test launches on the picker
            // in English (saved state AND language persist in simulator
            // UserDefaults across launches within a test run).
            if ProcessInfo.processInfo.arguments.contains("--uitest-reset") {
                if ProcessInfo.processInfo.arguments.contains("--uitest-clear-progress") {
                    for state in allStates { storage.clearStore(for: state.code) }
                }
                storage.savedStateCode = nil
                localizer.currentLang = "en"
            }
            if let savedCode = storage.savedStateCode,
               let saved = allStates.first(where: { $0.code == savedCode && $0.hasQuestions }) {
                currentState = saved
                normalizeLanguage(for: saved)
                invalidateStoreCache()
                selectedCount = min(50, saved.totalQuestions)
                screen = .home
            }
            isLoading = false
        }
    }

    func selectState(_ state: StateInfo) {
        languageFallbackNotice = nil
        normalizeLanguage(for: state)
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

    var needsStudyWarning: Bool {
        guard localizer.currentLang != "en", let state = currentState else { return false }
        let names = ["es": "spanish", "ja": "japanese", "fr": "french"]
        guard let name = names[localizer.currentLang], let official = state.officialTestLanguages else { return true }
        return !official.contains { $0.lowercased() == name }
    }

    var legacySessionCount: Int {
        guard let state = currentState else { return 0 }
        return storage.loadStore(for: state.code).history.count
    }

    func requestQuiz() {
        if needsStudyWarning, let state = currentState,
           !storage.hasAcknowledgedStudyLanguage(state: state.code, language: localizer.currentLang) {
            showStudyWarning = true
        } else {
            startQuiz()
        }
    }

    func acknowledgeStudyLanguage() {
        guard let state = currentState else { return }
        storage.acknowledgeStudyLanguage(state: state.code, language: localizer.currentLang)
        startQuiz()
    }

    func practiceEnglish() {
        localizer.currentLang = "en"
        invalidateStoreCache()
        quizMode = .random
        startQuiz()
    }

    func startQuiz() {
        showLegacyStats = false
        guard let state = currentState else { return }
        normalizeLanguage(for: state)

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
        guard !questions.isEmpty else {
            quizError = localizer.localized("quizUnavailable")
            screen = .home
            return
        }
        quizError = nil
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
        guard screen == .quiz, !answered, let q = currentQuestion, q.choices[letter] != nil,
              let state = currentState else { return }
        guard let response = api.fetchAnswer(questionId: q.id, state: state.code, lang: localizer.currentLang) else {
            quizError = localizer.localized("answerUnavailable")
            return
        }
        quizError = nil
        answered = true
        selectedAnswer = letter
        correctAnswer = response.answer
        explanation = response.explanation
        let isCorrect = letter == response.answer

        if isCorrect { correctCount += 1 } else { wrongCount += 1 }

        var s = store
        let idStr = String(q.id)
        var record = s.questions[idStr] ?? QuestionRecord(seen: 0, wrong: 0, category: q.category)
        record.seen += 1
        if !isCorrect { record.wrong += 1 }
        s.questions[idStr] = record
        storage.saveStore(s, for: state.code, language: localizer.currentLang)
        updateStoreCache(s)

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
        guard screen == .quiz, answered, currentIndex < questions.count else { return }
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
        var s = store
        s.history.append(QuizHistoryEntry(
            date: Date(),
            correct: correctCount,
            total: questions.count,
            pct: resultPct,
            mode: quizMode.rawValue
        ))
        storage.saveStore(s, for: state.code, language: localizer.currentLang)
        updateStoreCache(s)
        screen = .results
    }

    func abandonQuiz() {
        questions = []
        sessionResults = []
        answered = false
        quizError = nil
        goHome()
    }

    func showStats() {
        showLegacyStats = false
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

extension QuizViewModel {
    private func normalizeLanguage(for state: StateInfo) {
        guard !state.languages.contains(localizer.currentLang) else { return }
        let previous = localizer.langLabels[localizer.currentLang] ?? localizer.currentLang
        localizer.currentLang = "en"
        languageFallbackNotice = localizer.localized("languageFallback", substitutions: ["language": previous])
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
            if entry.total > 0 && entry.correct * 100 >= entry.total * state.passingScorePct { streak += 1 } else { break }
        }
        return streak
    }

    var bestScore: Int {
        quizHistory.map(\.pct).max() ?? 0
    }

    var questionsSeen: Int {
        store.questions.count
    }
}
