import XCTest
import UIKit
@testable import DriversTest

@MainActor
final class DriversTestTests: XCTestCase {
    private struct Context {
        let suite: String
        let defaults: UserDefaults
        let store: LocalStore
        let localizer: Localizer
        let vm: QuizViewModel

        func cleanUp() { defaults.removePersistentDomain(forName: suite) }
    }

    private func context() throws -> Context {
        let suite = "DriversTestTests.\(UUID().uuidString)"
        let defaults = try XCTUnwrap(UserDefaults(suiteName: suite))
        let store = LocalStore(defaults: defaults)
        let localizer = Localizer(storage: store)
        try ApiClient.shared.loadBundle()
        let vm = QuizViewModel(storage: store, localizer: localizer)
        let state = try XCTUnwrap(ApiClient.shared.fetchStates().first { $0.code == "nj" })
        vm.selectState(state)
        return Context(suite: suite, defaults: defaults, store: store, localizer: localizer, vm: vm)
    }

    func testPreferencesAndStateStoresSurviveNewStoreInstance() throws {
        let c = try context()
        defer { c.cleanUp() }
        c.store.savedStateCode = "nj"
        c.store.savedLanguage = "es"
        var saved = QuizStore.empty
        saved.questions["7"] = QuestionRecord(seen: 2, wrong: 1, category: "signs_and_signals")
        c.store.saveStore(saved, for: "nj")
        let reopened = LocalStore(defaults: c.defaults)
        XCTAssertEqual(reopened.savedStateCode, "nj")
        XCTAssertEqual(reopened.savedLanguage, "es")
        XCTAssertEqual(reopened.loadStore(for: "nj").questions["7"]?.wrong, 1)
        XCTAssertTrue(reopened.loadStore(for: "ca").questions.isEmpty)
        reopened.clearStore(for: "nj")
        XCTAssertTrue(reopened.loadStore(for: "nj").questions.isEmpty)
    }

    func testCorruptSavedDataRecoversToEmptyStore() throws {
        let c = try context()
        defer { c.cleanUp() }
        c.defaults.set(Data("invalid json".utf8), forKey: "quiz_nj")
        XCTAssertTrue(c.store.loadStore(for: "nj").history.isEmpty)
        XCTAssertTrue(c.store.loadStore(for: "nj").questions.isEmpty)
    }

    func testWeakQuestionsRankByMissRateThenMissCount() throws {
        let c = try context()
        defer { c.cleanUp() }
        var saved = QuizStore.empty
        saved.questions = [
            "1": QuestionRecord(seen: 4, wrong: 2, category: "a"),
            "2": QuestionRecord(seen: 2, wrong: 2, category: "b"),
            "3": QuestionRecord(seen: 1, wrong: 1, category: "c"),
            "4": QuestionRecord(seen: 3, wrong: 0, category: "d")
        ]
        c.store.saveStore(saved, for: "nj")
        XCTAssertEqual(c.store.getWeakQuestions(for: "nj").map(\.id), [2, 3, 1])
    }

    func testScoringRejectsDuplicateAnswerAndPersistsCompletedQuiz() throws {
        let c = try context()
        defer { c.cleanUp() }
        c.vm.selectedCount = 10
        c.vm.startQuiz()
        XCTAssertEqual(c.vm.questions.count, 10)
        for index in 0..<10 {
            let q = try XCTUnwrap(c.vm.currentQuestion)
            let answer = try XCTUnwrap(ApiClient.shared.fetchAnswer(questionId: q.id, state: "nj", lang: "en"))
            let choice = index < 8 ? answer.answer : try XCTUnwrap(q.sortedChoiceKeys.first { $0 != answer.answer })
            c.vm.selectAnswer(choice)
            c.vm.selectAnswer(choice)
            XCTAssertEqual(c.vm.sessionResults.count, index + 1, "Duplicate taps must not count twice")
            c.vm.nextQuestion()
        }
        XCTAssertEqual(c.vm.correctCount, 8)
        XCTAssertEqual(c.vm.wrongCount, 2)
        XCTAssertEqual(c.vm.resultPct, 80)
        XCTAssertTrue(c.vm.didPass)
        XCTAssertEqual(c.vm.screen, .results)
        let persisted = c.store.loadStore(for: "nj", language: "en")
        XCTAssertEqual(persisted.history.count, 1)
        XCTAssertEqual(persisted.history.first?.pct, 80)
        XCTAssertEqual(persisted.questions.values.reduce(0) { $0 + $1.seen }, 10)
        XCTAssertEqual(c.vm.weakQuestions.count, 2)
        let restored = QuizViewModel(storage: c.store, localizer: c.localizer)
        restored.selectState(try XCTUnwrap(c.vm.currentState))
        XCTAssertEqual(restored.averageScore, 80)
        XCTAssertEqual(restored.passStreak, 1)
        XCTAssertEqual(restored.questionsSeen, 10)
    }

    func testWeakModeUsesOnlyMissedQuestionsAndClearInvalidatesCache() throws {
        let c = try context()
        defer { c.cleanUp() }
        c.vm.selectedCount = 10
        c.vm.startQuiz()
        let q = try XCTUnwrap(c.vm.currentQuestion)
        let answer = try XCTUnwrap(ApiClient.shared.fetchAnswer(questionId: q.id, state: "nj", lang: "en"))
        c.vm.selectAnswer(try XCTUnwrap(q.sortedChoiceKeys.first { $0 != answer.answer }))
        XCTAssertEqual(c.vm.weakQuestions.map(\.id), [q.id])
        c.vm.goHome()
        c.vm.quizMode = .weak
        c.vm.startQuiz()
        XCTAssertEqual(c.vm.questions.map(\.id), [q.id])
        c.vm.clearData()
        XCTAssertTrue(c.vm.weakQuestions.isEmpty)
        XCTAssertEqual(c.vm.questionsSeen, 0)
        XCTAssertEqual(c.vm.averageScore, 0)
        XCTAssertEqual(c.vm.screen, .home)
    }

    func testLanguageStoresAreIsolatedAndLegacySessionsRemainAvailable() throws {
        let c = try context()
        defer { c.cleanUp() }
        var legacy = QuizStore.empty
        legacy.history = [QuizHistoryEntry(date: Date(), correct: 8, total: 10, pct: 80, mode: "random")]
        c.store.saveStore(legacy, for: "nj")
        c.localizer.currentLang = "en"
        c.vm.selectedCount = 10
        c.vm.startQuiz()
        let q = try XCTUnwrap(c.vm.currentQuestion)
        let answer = try XCTUnwrap(ApiClient.shared.fetchAnswer(questionId: q.id, state: "nj", lang: "en"))
        c.vm.selectAnswer(answer.answer)
        XCTAssertEqual(c.vm.questionsSeen, 1)
        c.vm.goHome()
        c.localizer.currentLang = "es"
        XCTAssertEqual(c.vm.questionsSeen, 0, "English progress must not appear as Spanish progress")
        XCTAssertTrue(c.vm.weakQuestions.isEmpty)
        XCTAssertEqual(c.vm.legacySessionCount, 1)
        XCTAssertEqual(c.store.loadStore(for: "nj").history.first?.pct, 80)
        c.localizer.currentLang = "en"
        XCTAssertEqual(c.vm.questionsSeen, 1)
        c.vm.clearData()
        XCTAssertTrue(c.store.loadStore(for: "nj", language: "en").questions.isEmpty)
        XCTAssertTrue(c.store.loadStore(for: "nj").history.isEmpty)
    }

    func testStudyLanguageRequiresAcknowledgmentBeforeStarting() throws {
        let c = try context()
        defer { c.cleanUp() }
        c.vm.selectState(try XCTUnwrap(ApiClient.shared.fetchStates().first { $0.code == "wy" }))
        c.localizer.currentLang = "es"
        XCTAssertTrue(c.vm.needsStudyWarning)
        c.vm.requestQuiz()
        XCTAssertTrue(c.vm.showStudyWarning)
        XCTAssertEqual(c.vm.screen, .home)
        c.vm.acknowledgeStudyLanguage()
        XCTAssertEqual(c.vm.screen, .quiz)
        XCTAssertTrue(c.store.hasAcknowledgedStudyLanguage(state: "wy", language: "es"))
        XCTAssertFalse(c.store.hasAcknowledgedStudyLanguage(state: "wy", language: "ja"))
        c.vm.practiceEnglish()
        XCTAssertEqual(c.localizer.currentLang, "en")
        XCTAssertFalse(c.vm.needsStudyWarning)
    }

    func testNextCannotSkipUnansweredQuestionOrRecordQuizTwice() throws {
        let c = try context()
        defer { c.cleanUp() }
        c.vm.selectedCount = 1
        c.vm.startQuiz()
        c.vm.nextQuestion()
        XCTAssertEqual(c.vm.currentIndex, 0)
        XCTAssertEqual(c.vm.screen, .quiz)
        let q = try XCTUnwrap(c.vm.currentQuestion)
        let answer = try XCTUnwrap(ApiClient.shared.fetchAnswer(questionId: q.id, state: "nj", lang: "en"))
        c.vm.selectAnswer(answer.answer)
        c.vm.nextQuestion()
        c.vm.nextQuestion()
        XCTAssertEqual(c.vm.quizHistory.count, 1)
        XCTAssertEqual(c.vm.correctCount, 1)
    }

    func testCurrentHandbookAndPendingReviewMetadataReachTheApp() throws {
        let c = try context()
        defer { c.cleanUp() }
        let arkansas = try XCTUnwrap(ApiClient.shared.fetchStates().first { $0.code == "ar" })
        XCTAssertEqual(arkansas.manualURL, "https://media.ark.org/dps/Arkansas-DL-Study-Guide-English_11122026.pdf")
        XCTAssertTrue(arkansas.contentReviewRequired)
        XCTAssertFalse(try XCTUnwrap(ApiClient.shared.fetchStates().first { $0.code == "nj" }).contentReviewRequired)
    }

    func testChangingStateCannotCreditEnglishFallbackToUnsupportedLanguage() throws {
        let c = try context()
        defer { c.cleanUp() }
        c.localizer.currentLang = "ja"
        let state = try XCTUnwrap(ApiClient.shared.fetchStates().first { $0.hasQuestions && !$0.languages.contains("ja") })
        c.vm.selectState(state)
        XCTAssertEqual(c.localizer.currentLang, "en")
        XCTAssertNotNil(c.vm.languageFallbackNotice)
        c.vm.selectedCount = 1
        c.vm.startQuiz()
        let q = try XCTUnwrap(c.vm.currentQuestion)
        let answer = try XCTUnwrap(ApiClient.shared.fetchAnswer(questionId: q.id, state: state.code, lang: "en"))
        c.vm.selectAnswer(answer.answer)
        XCTAssertEqual(c.store.loadStore(for: state.code, language: "en").questions.count, 1)
        XCTAssertTrue(c.store.loadStore(for: state.code, language: "ja").questions.isEmpty)
    }

    func testEveryReferencedSignImageDecodesAndStateResetClearsConsent() throws {
        let c = try context()
        defer { c.cleanUp() }
        var images = Set<String>()
        for state in ApiClient.shared.fetchStates().filter(\.hasQuestions) {
            let questions = ApiClient.shared.fetchQuiz(state: state.code, lang: "en", count: state.totalQuestions)
            for question in questions {
                if let name = question.image { images.insert(name) }
            }
        }
        XCTAssertFalse(images.isEmpty)
        for name in images {
            let path = try XCTUnwrap(Bundle.main.path(
                forResource: (name as NSString).deletingPathExtension,
                ofType: (name as NSString).pathExtension, inDirectory: "signs"))
            XCTAssertNotNil(UIImage(contentsOfFile: path), "Sign must decode: \(name)")
            XCTAssertNotNil(SignImageDescriptions.descriptions[name], "Sign must have a verified visual description: \(name)")
        }
        c.store.acknowledgeStudyLanguage(state: "wy", language: "es")
        c.store.clearStore(for: "wy")
        XCTAssertFalse(c.store.hasAcknowledgedStudyLanguage(state: "wy", language: "es"))
    }

    func testInvalidAnswerAndReturningToStatsCannotCorruptLanguageProgress() throws {
        let c = try context()
        defer { c.cleanUp() }
        c.vm.selectedCount = 1
        c.vm.startQuiz()
        c.vm.selectAnswer("invalid")
        XCTAssertFalse(c.vm.answered)
        XCTAssertTrue(c.vm.sessionResults.isEmpty)
        XCTAssertTrue(c.store.loadStore(for: "nj", language: "en").questions.isEmpty)
        c.vm.showStats()
        c.vm.showLegacyStats = true
        c.vm.goHome()
        c.vm.showStats()
        XCTAssertFalse(c.vm.showLegacyStats)
    }

    private final class MissingAnswerClient: ApiClient {
        override func fetchQuiz(state: String, lang: String, count: Int) -> [QuizQuestion] {
            [QuizQuestion(id: 1, category: "signs_and_signals", question: "Fixture", choices: ["A": "One", "B": "Two"], image: nil)]
        }
        override func fetchAnswer(questionId: Int, state: String, lang: String) -> AnswerResponse? { nil }
    }

    func testMissingAnswerCanRetryWithoutRecordingOrAdvancing() throws {
        let c = try context()
        defer { c.cleanUp() }
        let vm = QuizViewModel(api: MissingAnswerClient(), storage: c.store, localizer: c.localizer)
        vm.selectState(try XCTUnwrap(c.vm.currentState))
        vm.startQuiz()
        vm.selectAnswer("A")
        XCTAssertFalse(vm.answered)
        XCTAssertNotNil(vm.quizError)
        XCTAssertTrue(vm.sessionResults.isEmpty)
        vm.nextQuestion()
        XCTAssertEqual(vm.currentIndex, 0)
        XCTAssertEqual(vm.screen, .quiz)
        XCTAssertTrue(c.store.loadStore(for: "nj", language: "en").questions.isEmpty)
    }

    func testEmptyBankStaysOnHomeWithRecoveryMessage() throws {
        let c = try context()
        defer { c.cleanUp() }
        c.vm.selectedCount = 0
        c.vm.startQuiz()
        XCTAssertEqual(c.vm.screen, .home)
        XCTAssertNotNil(c.vm.quizError)
        XCTAssertTrue(c.vm.quizHistory.isEmpty)
        c.vm.selectedCount = 10
        c.vm.startQuiz()
        XCTAssertEqual(c.vm.screen, .quiz)
        XCTAssertNil(c.vm.quizError)
    }

    func testAbandonedQuizRetainsAnsweredProgressWithoutCompletedHistory() throws {
        let c = try context()
        defer { c.cleanUp() }
        c.vm.startQuiz()
        let q = try XCTUnwrap(c.vm.currentQuestion)
        let answer = try XCTUnwrap(ApiClient.shared.fetchAnswer(questionId: q.id, state: "nj", lang: "en"))
        c.vm.selectAnswer(answer.answer)
        c.vm.abandonQuiz()
        XCTAssertEqual(c.vm.screen, .home)
        XCTAssertTrue(c.vm.questions.isEmpty)
        XCTAssertTrue(c.vm.quizHistory.isEmpty)
        XCTAssertEqual(c.vm.questionsSeen, 1)
        let restored = QuizViewModel(storage: c.store, localizer: c.localizer)
        restored.selectState(try XCTUnwrap(c.vm.currentState))
        XCTAssertEqual(restored.questionsSeen, 1)
        XCTAssertTrue(restored.questions.isEmpty)
        XCTAssertTrue(restored.quizHistory.isEmpty)
    }

    func testRoundedDisplayDoesNotTurnNearMissIntoPassOrStreak() throws {
        let c = try context()
        defer { c.cleanUp() }
        let q = try XCTUnwrap(ApiClient.shared.fetchQuiz(state: "nj", lang: "en", count: 1).first)
        c.vm.questions = Array(repeating: q, count: 201)
        c.vm.correctCount = 160
        XCTAssertEqual(c.vm.resultPct, 80)
        XCTAssertFalse(c.vm.didPass, "160/201 is below 80%, even though the display rounds to 80%")
        var saved = QuizStore.empty
        saved.history = [QuizHistoryEntry(date: Date(), correct: 160, total: 201, pct: 80, mode: "random")]
        c.store.saveStore(saved, for: "nj", language: "en")
        let restored = QuizViewModel(storage: c.store, localizer: c.localizer)
        restored.selectState(try XCTUnwrap(c.vm.currentState))
        XCTAssertEqual(restored.passStreak, 0)
        c.vm.correctCount = 161
        XCTAssertTrue(c.vm.didPass)
    }

    func testBundleIncludesFiftyUsableStatesAndNonemptyLocalizedBanks() throws {
        let c = try context()
        defer { c.cleanUp() }
        let states = ApiClient.shared.fetchStates().filter(\.hasQuestions)
        XCTAssertEqual(states.count, 50)
        for state in states {
            XCTAssertFalse(ApiClient.shared.fetchQuiz(state: state.code, lang: "en", count: 1).isEmpty)
            for language in state.languages {
                let question = try XCTUnwrap(ApiClient.shared.fetchQuiz(state: state.code, lang: language, count: 1).first)
                XCTAssertNotNil(ApiClient.shared.fetchAnswer(questionId: question.id, state: state.code, lang: language))
            }
        }
    }
}
