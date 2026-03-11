import Foundation
import SwiftUI

enum AppScreen {
    case statePicker
    case home
    case quiz
    case results
    case stats
}

@MainActor
class QuizViewModel: ObservableObject {
    @Published var screen: AppScreen = .statePicker
    @Published var allStates: [StateInfo] = []
    @Published var currentState: StateInfo?
    @Published var isLoading = false
    @Published var errorMessage: String?

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

    let localizer = Localizer.shared
    private let api = APIService.shared
    private let storage = StorageService.shared

    var store: QuizStore {
        guard let state = currentState else { return .empty }
        return storage.loadStore(for: state.code)
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

    // Category stats for stats screen
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

    // Question miss data for badge
    func questionMissInfo(_ questionId: Int) -> (wrong: Int, seen: Int)? {
        guard let record = store.questions[String(questionId)], record.wrong > 0 else { return nil }
        return (record.wrong, record.seen)
    }

    // MARK: - Actions

    func loadStates() async {
        isLoading = true
        errorMessage = nil
        do {
            allStates = try await api.fetchStates()
            if let savedCode = storage.savedStateCode,
               let saved = allStates.first(where: { $0.code == savedCode && $0.hasQuestions }) {
                currentState = saved
                selectedCount = min(50, saved.totalQuestions)
                screen = .home
            }
        } catch {
            errorMessage = "Failed to load states. Make sure the server is running."
        }
        isLoading = false
    }

    func selectState(_ state: StateInfo) {
        currentState = state
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

    func startQuiz() async {
        guard let state = currentState else { return }
        isLoading = true
        do {
            if quizMode == .weak {
                let weak = weakQuestions
                guard !weak.isEmpty else { isLoading = false; return }
                let count = min(selectedCount, weak.count)
                let weakIds = Set(weak.prefix(count).map(\.id))
                let all = try await api.fetchQuiz(state: state.code, lang: localizer.currentLang, count: state.totalQuestions)
                questions = all.filter { weakIds.contains($0.id) }.shuffled().prefix(count).map { $0 }
            } else {
                questions = try await api.fetchQuiz(state: state.code, lang: localizer.currentLang, count: selectedCount)
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
        } catch {
            errorMessage = "Failed to load quiz."
        }
        isLoading = false
    }

    func selectAnswer(_ letter: String) async {
        guard !answered, let q = currentQuestion, let state = currentState else { return }
        answered = true
        selectedAnswer = letter

        do {
            let response = try await api.fetchAnswer(questionId: q.id, state: state.code, lang: localizer.currentLang)
            correctAnswer = response.answer
            explanation = response.explanation
            let isCorrect = letter == response.answer

            if isCorrect { correctCount += 1 } else { wrongCount += 1 }

            // Update store
            var s = storage.loadStore(for: state.code)
            let idStr = String(q.id)
            if s.questions[idStr] == nil {
                s.questions[idStr] = QuestionRecord(seen: 0, wrong: 0, category: q.category)
            }
            s.questions[idStr]!.seen += 1
            if !isCorrect { s.questions[idStr]!.wrong += 1 }
            storage.saveStore(s, for: state.code)

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
        } catch {
            errorMessage = "Failed to check answer."
        }
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
        screen = .results
    }

    func showStats() {
        screen = .stats
    }

    func clearData() {
        guard let state = currentState else { return }
        storage.clearStore(for: state.code)
        objectWillChange.send()
        screen = .home
    }
}
