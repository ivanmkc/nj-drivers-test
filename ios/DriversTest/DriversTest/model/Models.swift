import Foundation

// MARK: - Navigation

enum AppScreen {
    case statePicker
    case home
    case quiz
    case results
    case stats
}

// MARK: - API Response Models

struct StateVerification {
    let verifiedAt: String?
    let overall: String?
    let manualUrl: String?
    let edition: String?
    let manualPages: Int?
    let precisionAvgFidelity: Double?
    let precisionGrade: String?
    let questionsJudged: Int?
    let recallCoveragePct: Double?
    let translations: [String: String]?
}

struct StateInfo: Identifiable {
    let code: String
    let name: String
    let agency: String
    let passingScorePct: Int
    let testQuestionCount: Int
    let languages: [String]
    let totalQuestions: Int
    let hasQuestions: Bool
    let source: String?
    let categories: [String: Int]?
    let verification: StateVerification?
    let officialTestLanguages: [String]?

    var id: String { code }

    var passCount: Int {
        Int(ceil(Double(testQuestionCount) * Double(passingScorePct) / 100.0))
    }
}

struct QuizQuestion: Codable, Identifiable {
    let id: Int
    let category: String
    let question: String
    let choices: [String: String]
    let image: String?

    var sortedChoiceKeys: [String] {
        choices.keys.sorted()
    }
}

struct AnswerResponse: Codable {
    let id: Int
    let answer: String
    let explanation: String
}

// MARK: - Local Storage Models

struct QuestionRecord: Codable {
    var seen: Int
    var wrong: Int
    var category: String
}

struct QuizHistoryEntry: Codable {
    let date: Date
    let correct: Int
    let total: Int
    let pct: Int
    let mode: String
}

struct QuizStore: Codable {
    var history: [QuizHistoryEntry]
    var questions: [String: QuestionRecord] // keyed by question ID string

    static let empty = QuizStore(history: [], questions: [:])
}

// MARK: - Quiz Session

struct SessionResult {
    let id: Int
    let question: String
    let yourAnswer: String
    let yourAnswerText: String
    let correctAnswer: String
    let correctAnswerText: String
    let correct: Bool
    let explanation: String
}

enum QuizMode: String {
    case random
    case weak
}

// MARK: - Weak Question

struct WeakQuestion: Identifiable {
    let id: Int
    let missRate: Double
    let wrong: Int
    let seen: Int
    let category: String
}
