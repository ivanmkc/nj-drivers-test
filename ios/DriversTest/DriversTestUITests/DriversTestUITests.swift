import XCTest

/// UI tests for the Driver's Test app.
/// These tests verify screen rendering and basic interactions
/// using XCUITest framework. The app is fully offline: it reads the bundled
/// questions_bundle.json.gz produced by tools/bundle.py, so no backend is needed.
final class DriversTestUITests: XCTestCase {

    let app = XCUIApplication()

    override func setUpWithError() throws {
        continueAfterFailure = false
        app.launchArguments += ["--uitest-reset"]
        app.launch()
    }

    // MARK: - State Picker Screen

    func testStatePickerShowsTitle() {
        // The app launches on the state picker screen
        let title = app.staticTexts["Driver's Test Practice"]
        XCTAssertTrue(title.waitForExistence(timeout: 5), "App title should be visible on launch")
    }

    func testStatePickerShowsDescription() {
        let desc = app.staticTexts["Choose your state to start practicing"]
        XCTAssertTrue(desc.waitForExistence(timeout: 5), "State picker description should be visible")
    }

    func testStatePickerShowsLanguageButtons() {
        let enButton = app.buttons["EN"]
        XCTAssertTrue(enButton.waitForExistence(timeout: 5), "EN language button should be visible")
    }

    func testStatePickerShowsStateCards() {
        let njState = findNewJersey()
        XCTAssertTrue(njState.isHittable, "Bundled New Jersey state card must be reachable")
    }

    // MARK: - Navigation

    func testSelectStateNavigatesToHome() {
        navigateToHome()

        // Should now see the home screen with state title
        let homeTitle = app.staticTexts["NJ Driver's Test"]
        XCTAssertTrue(homeTitle.waitForExistence(timeout: 5), "Should navigate to home screen after selecting state")
    }

    func testHomeScreenShowsQuizModes() {
        navigateToHome()

        XCTAssertTrue(app.staticTexts["Random"].exists, "Random mode button should be visible")
        XCTAssertTrue(app.staticTexts["Weak Spots"].exists, "Weak Spots mode button should be visible")
    }

    func testHomeScreenShowsStartButton() {
        navigateToHome()

        let startButton = app.buttons["Start Quiz"]
        XCTAssertTrue(startButton.exists, "Start Quiz button should be visible")
    }

    func testHomeScreenShowsCountSelector() {
        navigateToHome()

        XCTAssertTrue(app.staticTexts["Number of questions:"].exists, "Question count label should be visible")
    }

    func testHomeScreenShowsChangeStateButton() {
        navigateToHome()

        XCTAssertTrue(app.buttons["Change State"].waitForExistence(timeout: 3), "Change State button should be visible")
    }

    func testChangeStateNavigatesBack() {
        navigateToHome()

        tapWhenReachable(app.buttons["Change State"])

        let title = app.staticTexts["Driver's Test Practice"]
        XCTAssertTrue(title.waitForExistence(timeout: 5), "Should navigate back to state picker")
    }

    // MARK: - Language Switching

    func testLanguageSwitchToJapanese() {
        navigateToHome()

        app.buttons["language-ja"].tap()

        let jaTitle = app.staticTexts["NJ 運転免許テスト"]
        XCTAssertTrue(jaTitle.waitForExistence(timeout: 3), "Title should switch to Japanese")
    }

    func testLanguageSwitchToSpanish() {
        navigateToHome()

        app.buttons["language-es"].tap()

        let esTitle = app.staticTexts["Examen de Conducir NJ"]
        XCTAssertTrue(esTitle.waitForExistence(timeout: 3), "Title should switch to Spanish")
    }

    // MARK: - Quiz Flow

    func testStartQuizShowsQuizScreen() {
        navigateToHome()

        // Select 10 questions for faster test
        XCTAssertTrue(app.buttons["count-10"].exists, "10-question option must exist")
        app.buttons["count-10"].tap()

        tapWhenReachable(app.buttons["Start Quiz"])

        // Should see quiz progress indicator (e.g., "1 / 10")
        let counter = app.staticTexts.matching(NSPredicate(format: "label CONTAINS '/ '")).firstMatch
        XCTAssertTrue(counter.waitForExistence(timeout: 10), "Quiz screen should show question counter")
    }

    func testCompleteQuizPersistsStatsStateAndLanguageAcrossRelaunch() throws {
        app.terminate()
        app.launchArguments = ["--uitest-reset", "--uitest-clear-progress"]
        app.launch()
        capture("picker-light")
        navigateToHome()
        app.buttons["language-es"].tap()
        capture("home-es-light")
        app.buttons["count-10"].tap()
        tapWhenReachable(app.buttons["start-quiz"])
        capture("quiz-es-light")
        if #available(iOS 17.0, *) { try app.performAccessibilityAudit() }
        for index in 0..<10 {
            let counter = app.staticTexts["\(index + 1) / 10"]
            XCTAssertTrue(counter.waitForExistence(timeout: 5))
            tapWhenReachable(app.buttons["answer-A"])
            if index == 0, #available(iOS 17.0, *) { try app.performAccessibilityAudit() }
            tapWhenReachable(app.buttons["quiz-next"])
        }
        capture("results-es")
        if #available(iOS 17.0, *) { try app.performAccessibilityAudit() }
        tapWhenReachable(app.buttons["view-stats"])
        XCTAssertTrue(app.staticTexts["Tu Progreso"].waitForExistence(timeout: 5))
        XCTAssertEqual(app.staticTexts["stats-session-count"].value as? String, "1")
        capture("stats-es")
        if #available(iOS 17.0, *) { try app.performAccessibilityAudit() }
        app.terminate()
        app.launchArguments = []
        app.launch()
        XCTAssertTrue(app.staticTexts["Examen de Conducir NJ"].waitForExistence(timeout: 10))
        tapWhenReachable(app.buttons["view-stats"])
        XCTAssertEqual(app.staticTexts["stats-session-count"].value as? String, "1")
    }

    func testScreensInDarkModeAtAccessibilityTextSize() throws {
        app.terminate()
        app.launchArguments = ["--uitest-reset", "--uitest-dark",
                               "-UIPreferredContentSizeCategoryName", "UICTContentSizeCategoryAccessibilityXXXL"]
        app.launch()
        capture("picker-dark-accessibility")
        navigateToHome()
        capture("home-dark-accessibility")
        tapWhenReachable(app.buttons["count-10"])
        tapWhenReachable(app.buttons["start-quiz"])
        XCTAssertTrue(app.staticTexts["1 / 10"].waitForExistence(timeout: 5))
        capture("quiz-dark-accessibility")
        if #available(iOS 17.0, *) { try app.performAccessibilityAudit() }
        for _ in 0..<10 {
            tapWhenReachable(app.buttons["answer-A"])
            tapWhenReachable(app.buttons["quiz-next"])
        }
        capture("results-dark-accessibility")
        tapWhenReachable(app.buttons["view-stats"])
        capture("stats-dark-accessibility")
    }

    @available(iOS 17.0, *)
    func testAccessibilityOnPickerAndHome() throws {
        try app.performAccessibilityAudit { issue in
            print("Accessibility audit: \(issue.detailedDescription)")
            return false
        }
        navigateToHome()
        try app.performAccessibilityAudit { issue in
            print("Accessibility audit: \(issue.detailedDescription)")
            return false
        }
    }

    func testPendingContentReviewNoticeAndCurrentHandbookLink() {
        let search = app.textFields["state-search"]
        XCTAssertTrue(search.waitForExistence(timeout: 10))
        search.tap()
        search.typeText("Arkansas\n")
        app.staticTexts["Arkansas"].tap()
        XCTAssertTrue(app.staticTexts["AR Driver's Test"].waitForExistence(timeout: 5))
        XCTAssertTrue(app.staticTexts["bank-content-review"].exists)
        XCTAssertTrue(app.descendants(matching: .any)["current-handbook-link"].exists)
        capture("content-review-notice")
    }

    func testStudyOnlyConsentCanCancelAndPracticeEnglish() {
        app.terminate()
        app.launchArguments = ["--uitest-reset", "--uitest-clear-progress"]
        app.launch()
        let search = app.textFields["state-search"]
        XCTAssertTrue(search.waitForExistence(timeout: 10))
        search.tap()
        search.typeText("Wyoming\n")
        app.staticTexts["Wyoming"].tap()
        app.buttons["language-es"].tap()
        tapWhenReachable(app.buttons["start-quiz"])
        let warning = app.alerts.firstMatch
        XCTAssertTrue(warning.waitForExistence(timeout: 5))
        warning.buttons["Cancelar"].tap()
        XCTAssertFalse(app.staticTexts["1 / 10"].exists)
        tapWhenReachable(app.buttons["start-quiz"])
        XCTAssertTrue(warning.waitForExistence(timeout: 5))
        warning.buttons["Iniciar una práctica en inglés"].tap()
        XCTAssertTrue(app.buttons["answer-A"].waitForExistence(timeout: 5))
        capture("study-consent-english-retest")
    }

    func testQuizExitCanCancelThenLeaveWithoutCompletedSession() {
        app.terminate()
        app.launchArguments = ["--uitest-reset", "--uitest-clear-progress"]
        app.launch()
        navigateToHome()
        app.buttons["count-10"].tap()
        tapWhenReachable(app.buttons["start-quiz"])
        tapWhenReachable(app.buttons["exit-quiz"])
        let confirmation = app.alerts.firstMatch
        XCTAssertTrue(confirmation.waitForExistence(timeout: 5))
        confirmation.buttons["Keep practicing"].tap()
        XCTAssertTrue(app.buttons["answer-A"].exists)
        tapWhenReachable(app.buttons["exit-quiz"])
        confirmation.buttons["Leave quiz"].tap()
        XCTAssertTrue(app.staticTexts["NJ Driver's Test"].waitForExistence(timeout: 5))
        XCTAssertFalse(app.buttons["view-stats"].exists)
    }

    private func tapWhenReachable(_ element: XCUIElement) {
        _ = element.waitForExistence(timeout: 2)
        for _ in 0..<20 {
            if element.exists && element.isHittable { element.tap(); return }
            app.swipeUp()
        }
        for _ in 0..<20 {
            if element.exists && element.isHittable { element.tap(); return }
            app.swipeDown()
        }
        XCTFail("Required control must be reachable: \(element)")
    }

    private func capture(_ name: String) {
        let attachment = XCTAttachment(screenshot: app.screenshot())
        attachment.name = name
        attachment.lifetime = .keepAlways
        add(attachment)
    }

    // MARK: - Helpers

    private func findNewJersey() -> XCUIElement {
        let state = app.staticTexts["New Jersey"]
        let search = app.textFields["state-search"]
        XCTAssertTrue(search.waitForExistence(timeout: 10), "State search must load")
        search.tap()
        search.typeText("New Jersey\n")
        XCTAssertTrue(state.waitForExistence(timeout: 10), "Bundled New Jersey state must exist")
        for _ in 0..<15 {
            if state.isHittable { return state }
            app.swipeUp()
        }
        XCTFail("Matching state must be reachable by scrolling")
        return state
    }

    private func navigateToHome() {
        findNewJersey().tap()
        XCTAssertTrue(app.staticTexts["NJ Driver's Test"].waitForExistence(timeout: 5),
                      "Selecting New Jersey must open its home screen")
    }
}
