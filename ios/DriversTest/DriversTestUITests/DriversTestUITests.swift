import UIKit
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
        if #available(iOS 17.0, *) { try auditAccessibility() }
        for index in 0..<10 {
            let counter = app.staticTexts["\(index + 1) / 10"]
            XCTAssertTrue(counter.waitForExistence(timeout: 5))
            tapWhenReachable(app.buttons["answer-A"])
            if index == 0, #available(iOS 17.0, *) { try auditAccessibility() }
            tapWhenReachable(app.buttons["quiz-next"])
        }
        capture("results-es")
        if #available(iOS 17.0, *) { try auditAccessibility() }
        tapWhenReachable(app.buttons["view-stats"])
        XCTAssertTrue(app.staticTexts["Tu Progreso"].waitForExistence(timeout: 5))
        XCTAssertEqual(app.descendants(matching: .any)["stats-session-count"].value as? String, "1")
        capture("stats-es")
        if #available(iOS 17.0, *) { try auditAccessibility() }
        app.terminate()
        app.launchArguments = []
        app.launch()
        XCTAssertTrue(app.staticTexts["Examen de Conducir NJ"].waitForExistence(timeout: 10))
        tapWhenReachable(app.buttons["view-stats"])
        XCTAssertEqual(app.descendants(matching: .any)["stats-session-count"].value as? String, "1")
    }

    func testScreensInDarkModeAtAccessibilityTextSize() throws {
        app.terminate()
        app.launchArguments = ["--uitest-reset", "--uitest-dark",
                               "-UIPreferredContentSizeCategoryName", "UICTContentSizeCategoryAccessibilityXXXL"]
        app.launch()
        capture("picker-dark-accessibility")
        navigateToHome()
        app.buttons["language-es"].tap()
        XCTAssertTrue(app.staticTexts["Examen de Conducir NJ"].waitForExistence(timeout: 5))
        capture("home-dark-accessibility")
        tapWhenReachable(app.buttons["count-10"])
        tapWhenReachable(app.buttons["start-quiz"])
        XCTAssertTrue(app.staticTexts["1 / 10"].waitForExistence(timeout: 5))
        capture("quiz-dark-accessibility")
        if #available(iOS 17.0, *) { try auditAccessibility() }
        for _ in 0..<10 {
            tapWhenReachable(app.buttons["answer-A"])
            tapWhenReachable(app.buttons["quiz-next"])
        }
        capture("results-dark-accessibility")
        tapWhenReachable(app.buttons["view-stats"])
        XCTAssertTrue(app.staticTexts["Tu Progreso"].waitForExistence(timeout: 5))
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

    @available(iOS 17.0, *)
    private func auditAccessibility() throws {
        try app.performAccessibilityAudit { issue in
            // iOS 26 intermittently reports contrast failure for this native black/white
            // tally on a flat adaptive background. Handle only that ID, only if the
            // CURRENT rendered pixels independently meet AA. Every other issue fails.
            guard issue.auditType == .contrast, let element = issue.element,
                  element.identifier == "quiz-tally",
                  let contrast = self.measuredContrast(in: element.screenshot().image),
                  contrast >= 4.5 else { return false }
            let evidence = XCTAttachment(string: "Native quiz tally rendered contrast: \(contrast):1 (AA minimum 4.5:1)")
            evidence.name = "quiz-tally-contrast-measurement"
            evidence.lifetime = .keepAlways
            self.add(evidence)
            let pixels = XCTAttachment(screenshot: element.screenshot())
            pixels.name = "quiz-tally-contrast-pixels"
            pixels.lifetime = .keepAlways
            self.add(pixels)
            return true
        }
    }

    private func measuredContrast(in image: UIImage) -> Double? {
        guard let cgImage = image.cgImage,
              let space = CGColorSpace(name: CGColorSpace.sRGB) else { return nil }
        let width = cgImage.width
        let height = cgImage.height
        guard width > 0, height > 0 else { return nil }
        var bytes = [UInt8](repeating: 0, count: width * height * 4)
        let drawn = bytes.withUnsafeMutableBytes { storage -> Bool in
            guard let context = CGContext(data: storage.baseAddress, width: width, height: height,
                                          bitsPerComponent: 8, bytesPerRow: width * 4, space: space,
                                          bitmapInfo: CGImageAlphaInfo.premultipliedLast.rawValue |
                                            CGBitmapInfo.byteOrder32Big.rawValue) else { return false }
            context.draw(cgImage, in: CGRect(x: 0, y: 0, width: width, height: height))
            return true
        }
        guard drawn else { return nil }
        var colors: [UInt32: Int] = [:]
        for index in stride(from: 0, to: bytes.count, by: 4) where bytes[index + 3] == 255 {
            let rgb = (UInt32(bytes[index]) << 16) | (UInt32(bytes[index + 1]) << 8) | UInt32(bytes[index + 2])
            colors[rgb, default: 0] += 1
        }
        let dominant = colors.sorted { $0.value > $1.value }.prefix(2)
        guard dominant.count == 2, dominant.allSatisfy({ $0.value >= width * height / 100 }) else { return nil }
        func luminance(_ rgb: UInt32) -> Double {
            let channels = [16, 8, 0].map { shift -> Double in
                let channel = Double((rgb >> shift) & 255) / 255
                return channel <= 0.04045 ? channel / 12.92 : pow((channel + 0.055) / 1.055, 2.4)
            }
            return channels[0] * 0.2126 + channels[1] * 0.7152 + channels[2] * 0.0722
        }
        let values = dominant.map { luminance($0.key) }.sorted()
        return (values[1] + 0.05) / (values[0] + 0.05)
    }

    func testMeasuredContrastKeepsLowContrastBlocking() throws {
        func swatch(_ foreground: UIColor) -> UIImage {
            UIGraphicsImageRenderer(size: CGSize(width: 100, height: 40)).image { context in
                UIColor.white.setFill()
                context.fill(CGRect(x: 0, y: 0, width: 100, height: 40))
                foreground.setFill()
                context.fill(CGRect(x: 0, y: 0, width: 50, height: 40))
            }
        }
        XCTAssertEqual(try XCTUnwrap(measuredContrast(in: swatch(.black))), 21, accuracy: 0.1)
        XCTAssertLessThan(try XCTUnwrap(measuredContrast(in: swatch(.lightGray))), 4.5)
        XCTAssertNil(measuredContrast(in: swatch(.white)), "An unmeasurable label must not bypass the audit")
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
