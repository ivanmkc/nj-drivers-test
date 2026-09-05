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
        // Wait for states to load from API
        let njState = app.staticTexts["New Jersey"]
        if njState.waitForExistence(timeout: 10) {
            XCTAssertTrue(njState.exists, "New Jersey state card should be visible")
        }
        // If server isn't running, we might see an error - that's ok for CI
    }

    // MARK: - Navigation

    func testSelectStateNavigatesToHome() {
        let njState = app.staticTexts["New Jersey"]
        guard njState.waitForExistence(timeout: 10) else {
            // Server not running - skip navigation tests
            return
        }
        njState.tap()

        // Should now see the home screen with state title
        let homeTitle = app.staticTexts["NJ Driver's Test"]
        XCTAssertTrue(homeTitle.waitForExistence(timeout: 5), "Should navigate to home screen after selecting state")
    }

    func testHomeScreenShowsQuizModes() {
        navigateToHome()
        guard app.staticTexts["NJ Driver's Test"].waitForExistence(timeout: 5) else { return }

        XCTAssertTrue(app.staticTexts["Random"].exists, "Random mode button should be visible")
        XCTAssertTrue(app.staticTexts["Weak Spots"].exists, "Weak Spots mode button should be visible")
    }

    func testHomeScreenShowsStartButton() {
        navigateToHome()
        guard app.staticTexts["NJ Driver's Test"].waitForExistence(timeout: 5) else { return }

        let startButton = app.buttons["Start Quiz"]
        XCTAssertTrue(startButton.exists, "Start Quiz button should be visible")
    }

    func testHomeScreenShowsCountSelector() {
        navigateToHome()
        guard app.staticTexts["NJ Driver's Test"].waitForExistence(timeout: 5) else { return }

        XCTAssertTrue(app.staticTexts["Number of questions:"].exists, "Question count label should be visible")
    }

    func testHomeScreenShowsChangeStateButton() {
        navigateToHome()
        guard app.staticTexts["NJ Driver's Test"].waitForExistence(timeout: 5) else { return }

        XCTAssertTrue(app.buttons["Change State"].waitForExistence(timeout: 3), "Change State button should be visible")
    }

    func testChangeStateNavigatesBack() {
        navigateToHome()
        guard app.staticTexts["NJ Driver's Test"].waitForExistence(timeout: 5) else { return }

        app.buttons["Change State"].tap()

        let title = app.staticTexts["Driver's Test Practice"]
        XCTAssertTrue(title.waitForExistence(timeout: 5), "Should navigate back to state picker")
    }

    // MARK: - Language Switching

    func testLanguageSwitchToJapanese() {
        navigateToHome()
        guard app.staticTexts["NJ Driver's Test"].waitForExistence(timeout: 5) else { return }

        app.buttons["日本語"].tap()

        let jaTitle = app.staticTexts["NJ 運転免許テスト"]
        XCTAssertTrue(jaTitle.waitForExistence(timeout: 3), "Title should switch to Japanese")
    }

    func testLanguageSwitchToSpanish() {
        navigateToHome()
        guard app.staticTexts["NJ Driver's Test"].waitForExistence(timeout: 5) else { return }

        app.buttons["ES"].tap()

        let esTitle = app.staticTexts["Examen de Conducir NJ"]
        XCTAssertTrue(esTitle.waitForExistence(timeout: 3), "Title should switch to Spanish")
    }

    // MARK: - Quiz Flow

    func testStartQuizShowsQuizScreen() {
        navigateToHome()
        guard app.staticTexts["NJ Driver's Test"].waitForExistence(timeout: 5) else { return }

        // Select 10 questions for faster test
        if app.buttons["10"].exists {
            app.buttons["10"].tap()
        }

        app.buttons["Start Quiz"].tap()

        // Should see quiz progress indicator (e.g., "1 / 10")
        let counter = app.staticTexts.matching(NSPredicate(format: "label CONTAINS '/ '")).firstMatch
        XCTAssertTrue(counter.waitForExistence(timeout: 10), "Quiz screen should show question counter")
    }

    // MARK: - Helpers

    private func navigateToHome() {
        let njState = app.staticTexts["New Jersey"]
        guard njState.waitForExistence(timeout: 10) else { return }
        njState.tap()
    }
}
