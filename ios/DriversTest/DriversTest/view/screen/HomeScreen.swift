import SwiftUI

struct HomeScreen: View {
    @ObservedObject var vm: QuizViewModel
    @ObservedObject var localizer: Localizer
    @Environment(\.dynamicTypeSize) private var dynamicTypeSize
    @ScaledMetric(relativeTo: .body) private var countButtonHeight = 44.0

    var body: some View {
        ScrollView {
            VStack(spacing: 16) {
                LanguageBarView(
                    localizer: localizer,
                    availableLangs: vm.currentState?.languages,
                    officialTestLanguages: vm.currentState?.officialTestLanguages
                )
                .padding(.bottom, 4)

                if vm.currentState?.officialTestLanguages != nil {
                    Text(localizer.localized("officialTestLangsCaption", substitutions: [
                        "agency": vm.currentState?.agency ?? "",
                    ]))
                    .font(AppTheme.body(14))
                    .foregroundColor(AppTheme.secondaryText)
                    .multilineTextAlignment(.center)
                }

                Text(localizer.localized("title", substitutions: [
                    "state": vm.currentState?.code.uppercased() ?? "",
                    "state_name": vm.currentState?.name ?? "",
                ]))
                .font(AppTheme.display(28)).fontWeight(.bold)
                .foregroundColor(AppTheme.blue)

                Text(localizer.localized("subtitle", substitutions: [
                    "state_name": vm.currentState?.name ?? "",
                    "agency": vm.currentState?.agency ?? "",
                ]))
                .font(AppTheme.body(15))
                .foregroundColor(AppTheme.secondaryText)

                if let state = vm.currentState {
                    Text(localizer.localized("passingScore", substitutions: [
                        "pass_pct": "\(state.passingScorePct)",
                        "pass_count": "\(state.passCount)",
                        "test_count": "\(state.testQuestionCount)",
                    ]))
                    .font(AppTheme.body(14))
                    .foregroundColor(AppTheme.secondaryText)
                }

                if let notice = vm.languageFallbackNotice {
                    Text(notice)
                        .font(.subheadline)
                        .foregroundColor(AppTheme.secondaryText)
                        .accessibilityIdentifier("language-fallback-notice")
                }
                // Stats banner
                if !vm.quizHistory.isEmpty {
                    StatsBannerView(vm: vm, localizer: localizer)
                }

                // Mode selector
                HStack(spacing: 8) {
                    ModeButton(
                        title: localizer.localized("modeRandom"),
                        desc: localizer.localized("modeRandomDesc"),
                        systemImage: "shuffle",
                        isActive: vm.quizMode == .random
                    ) { vm.quizMode = .random }

                    ModeButton(
                        title: localizer.localized("modeWeak"),
                        desc: localizer.localized("modeWeakDesc"),
                        systemImage: "target",
                        isActive: vm.quizMode == .weak,
                        badgeCount: vm.weakQuestions.count
                    ) { vm.quizMode = .weak }
                }

                // Count selector
                Text(localizer.localized("numQuestions"))
                    .font(AppTheme.body(15)).fontWeight(.semibold)

                let columns = dynamicTypeSize >= .xxxLarge ? 1 : 2
                VStack(spacing: 8) {
                    ForEach(Array(stride(from: 0, to: vm.countOptions.count, by: columns)), id: \.self) { start in
                        HStack(spacing: 8) {
                            ForEach(Array(vm.countOptions[start..<min(start + columns, vm.countOptions.count)]), id: \.self) { count in
                                countButton(count)
                            }
                        }
                    }
                }

                SourceCitationView(state: vm.currentState)
                if let error = vm.quizError {
                    Text(error).foregroundColor(AppTheme.errorText).accessibilityIdentifier("quiz-error")
                }
                // Start button
                let weakEmpty = vm.quizMode == .weak && vm.weakQuestions.isEmpty
                Button {
                    vm.requestQuiz()
                } label: {
                    Text(weakEmpty ? localizer.localized("noWeakSpots") : localizer.localized("startQuiz"))
                        .font(AppTheme.body(18)).fontWeight(.semibold)
                        .foregroundColor(AppTheme.onPrimary)
                        .frame(maxWidth: .infinity)
                        .padding(16)
                        .background(weakEmpty ? AppTheme.blue.opacity(0.5) : AppTheme.blue)
                        .clipShape(RoundedRectangle(cornerRadius: 12))
                }
                .disabled(weakEmpty)
                .accessibilityIdentifier("start-quiz")

                // Change state (kept above the About section so it stays on
                // screen without scrolling — UI tests and users both tap it)
                Button {
                    vm.goStatePicker()
                } label: {
                    Text(localizer.localized("changeState"))
                        .font(AppTheme.body(14))
                        .foregroundColor(AppTheme.secondaryText)
                        .frame(minHeight: 44)
                        .contentShape(Rectangle())
                }

                // About this test
                if let state = vm.currentState {
                    AboutTestSection(state: state, localizer: localizer)
                }
            }
            .padding(.horizontal, 16)
            .padding(.top, 24)
        }
        .background(AppTheme.grayLight)
        .alert(localizer.localized("studyLanguageTitle"), isPresented: $vm.showStudyWarning) {
            Button(localizer.localized("studyContinue")) { vm.acknowledgeStudyLanguage() }
            Button(localizer.localized("practiceEnglish")) { vm.practiceEnglish() }
            Button(localizer.localized("cancel"), role: .cancel) {}
        } message: {
            Text(localizer.localized("studyLanguageMessage"))
        }
    }
    private func countButton(_ count: Int) -> some View {
        let isAll = count == vm.currentState?.totalQuestions
        return Button { vm.selectedCount = count } label: {
            Text(isAll ? localizer.localized("all") : localizer.localized("questionCount", substitutions: ["count": "\(count)"]))
                .font(.body).fontWeight(.semibold)
                .fixedSize(horizontal: false, vertical: true)
                .frame(maxWidth: .infinity, minHeight: countButtonHeight)
                .padding(8)
                .foregroundColor(vm.selectedCount == count ? AppTheme.onPrimary : AppTheme.blue)
                .background(vm.selectedCount == count ? AppTheme.blue : AppTheme.card)
                .cardStyle(borderColor: AppTheme.blue)
                .contentShape(Rectangle())
        }
        .accessibilityIdentifier("count-\(count)")
    }
}

// MARK: - About This Test

private struct AboutTestSection: View {
    let state: StateInfo
    @ObservedObject var localizer: Localizer
    @State private var isExpanded = false

    var body: some View {
        // Plain button-toggled collapsible (not DisclosureGroup — its
        // DisclosureTriangle automation type confuses XCUITest element queries).
        VStack(alignment: .leading, spacing: 0) {
            Button {
                withAnimation(.easeInOut(duration: 0.2)) { isExpanded.toggle() }
            } label: {
                HStack(spacing: 6) {
                    Image(systemName: "info.circle").accessibilityHidden(true)
                        .foregroundColor(AppTheme.blue)
                    Text(localizer.localized("aboutThisTest"))
                        .font(AppTheme.body(15)).fontWeight(.semibold)
                        .foregroundColor(.primary)
                    Spacer()
                    Image(systemName: "chevron.down").accessibilityHidden(true)
                        .font(AppTheme.body(14)).fontWeight(.semibold)
                        .foregroundColor(AppTheme.secondaryText)
                        .rotationEffect(.degrees(isExpanded ? 180 : 0))
                }
                .frame(minHeight: 44)
                .contentShape(Rectangle())
            }
            .buttonStyle(.plain)

            if isExpanded {
                VStack(alignment: .leading, spacing: 12) {
                    if let verification = state.verification {
                        VerificationBadgesView(verification: verification, localizer: localizer)
                    }

                    if let source = state.source {
                        SourceRow(source: source, manualUrl: state.verification?.manualUrl, localizer: localizer)
                    }

                    OfficialTestLanguagesRow(
                        officialTestLanguages: state.officialTestLanguages,
                        agency: state.agency,
                        localizer: localizer
                    )

                    if let categories = state.categories, !categories.isEmpty {
                        CategoryBreakdownView(categories: categories, localizer: localizer)
                    }
                }
                .padding(.top, 8)
            }
        }
        .padding(.horizontal, 14)
        .padding(.vertical, 6)
        .cardStyle(borderWidth: 1)
    }
}

private struct SourceRow: View {
    let source: String
    let manualUrl: String?
    @ObservedObject var localizer: Localizer

    var body: some View {
        HStack(alignment: .top, spacing: 6) {
            Text(localizer.localized("source") + ":")
                .font(AppTheme.body(14))
                .foregroundColor(AppTheme.secondaryText)

            if let urlString = manualUrl, let url = URL(string: urlString) {
                Link(destination: url) {
                    Text(source)
                        .font(AppTheme.body(14))
                        .foregroundColor(AppTheme.blue)
                        .underline()
                        .multilineTextAlignment(.leading)
                }
            } else {
                Text(source)
                    .font(AppTheme.body(14))
                    .foregroundColor(.primary)
                    .multilineTextAlignment(.leading)
            }
        }
    }
}

private struct OfficialTestLanguagesRow: View {
    let officialTestLanguages: [String]?
    let agency: String
    @ObservedObject var localizer: Localizer

    private var displayText: String {
        guard let langs = officialTestLanguages else {
            return localizer.localized("officialTestLangsNotStated", substitutions: ["agency": agency])
        }
        let named = langs.filter { $0.lowercased() != "many" }
        let hasMany = langs.contains { $0.lowercased() == "many" }
        if named.isEmpty && hasMany {
            return localizer.localized("officialTestLangsAndOthers")
        }
        var text = named.joined(separator: ", ")
        if hasMany {
            text += " " + localizer.localized("officialTestLangsAndOthers")
        }
        return text
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 4) {
            HStack(alignment: .top, spacing: 6) {
                Text(localizer.localized("officialTestLangsRow") + ":")
                    .font(AppTheme.body(14))
                    .foregroundColor(AppTheme.secondaryText)
                Text(displayText)
                    .font(AppTheme.body(14))
                    .foregroundColor(.primary)
                    .multilineTextAlignment(.leading)
            }
            Text(localizer.localized("officialTestLangsPractice"))
                .font(AppTheme.body(14))
                .foregroundColor(AppTheme.secondaryText)
                .italic()
        }
    }
}

private struct VerificationBadgesView: View {
    let verification: StateVerification
    @ObservedObject var localizer: Localizer

    private var isPassing: Bool {
        verification.overall == "PASS"
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            // Adaptive grid wraps badge pills; the iOS 16 Layout protocol is
            // unavailable on this app's iOS 15 target.
            LazyVGrid(
                columns: [GridItem(.adaptive(minimum: 96), spacing: 6, alignment: .leading)],
                alignment: .leading,
                spacing: 6
            ) {
                if let grade = verification.precisionGrade {
                    BadgePill(
                        label: localizer.localized("grade"),
                        value: grade,
                        systemImage: isPassing ? "checkmark.seal" : nil
                    )
                }

                if let fidelity = verification.precisionAvgFidelity {
                    BadgePill(
                        label: localizer.localized("fidelity"),
                        value: String(format: "%.1f/10", fidelity),
                        systemImage: fidelity >= 7.0 ? "checkmark.seal" : nil
                    )
                }

                if let coverage = verification.recallCoveragePct {
                    BadgePill(
                        label: localizer.localized("coverage"),
                        value: String(format: "%.0f%%", coverage),
                        systemImage: coverage >= 80 ? "checkmark.seal" : nil
                    )
                }

                if let translations = verification.translations, !translations.isEmpty {
                    let allPass = translations.values.allSatisfy { $0 == "PASS" }
                    BadgePill(
                        label: localizer.localized("translations"),
                        value: allPass ? "OK" : "partial",
                        systemImage: allPass ? "checkmark.seal" : nil
                    )
                }
            }

            HStack(spacing: 16) {
                if let edition = verification.edition {
                    HStack(spacing: 4) {
                        Text(localizer.localized("edition") + ":")
                            .foregroundColor(AppTheme.secondaryText)
                        Text(edition)
                    }
                    .font(AppTheme.body(14))
                }

                if let verifiedAt = verification.verifiedAt {
                    HStack(spacing: 4) {
                        Text(localizer.localized("verified") + ":")
                            .foregroundColor(AppTheme.secondaryText)
                        Text(Self.formatDate(verifiedAt))
                    }
                    .font(AppTheme.body(14))
                }
            }
        }
    }

    private static func formatDate(_ iso: String) -> String {
        let formatter = ISO8601DateFormatter()
        formatter.formatOptions = [.withInternetDateTime, .withFractionalSeconds]
        if let date = formatter.date(from: iso) {
            let display = DateFormatter()
            display.dateStyle = .medium
            display.timeStyle = .none
            return display.string(from: date)
        }
        formatter.formatOptions = [.withInternetDateTime]
        if let date = formatter.date(from: iso) {
            let display = DateFormatter()
            display.dateStyle = .medium
            display.timeStyle = .none
            return display.string(from: date)
        }
        return String(iso.prefix(10))
    }
}

private struct BadgePill: View {
    let label: String
    let value: String
    var systemImage: String?

    var body: some View {
        HStack(spacing: 4) {
            if let systemImage {
                Image(systemName: systemImage).accessibilityHidden(true)
                    .font(AppTheme.body(14))
                    .foregroundColor(AppTheme.successText)
            }
            Text(label)
                .foregroundColor(AppTheme.secondaryText)
            Text(value)
                .fontWeight(.semibold)
        }
        .font(AppTheme.body(14))
        .padding(.horizontal, 10)
        .padding(.vertical, 5)
        .background(AppTheme.blueLight)
        .clipShape(RoundedRectangle(cornerRadius: 16))
    }
}

private struct CategoryBreakdownView: View {
    let categories: [String: Int]
    @ObservedObject var localizer: Localizer

    private var sortedCategories: [(name: String, count: Int)] {
        categories.map { (name: $0.key, count: $0.value) }
            .sorted { $0.count > $1.count }
    }

    private var maxCount: Int {
        categories.values.max() ?? 1
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 6) {
            ForEach(sortedCategories, id: \.name) { cat in
                HStack(spacing: 8) {
                    Text(localizer.localizedCategory(cat.name))
                        .font(AppTheme.body(14))
                        .frame(width: 120, alignment: .leading)
                        .lineLimit(1)

                    GeometryReader { geo in
                        RoundedRectangle(cornerRadius: 3)
                            .fill(AppTheme.blue)
                            .frame(width: geo.size.width * CGFloat(cat.count) / CGFloat(maxCount), height: 8)
                    }
                    .frame(height: 8)

                    Text("\(cat.count)")
                        .font(AppTheme.body(14)).fontWeight(.semibold)
                        .monospacedDigit()
                        .foregroundColor(AppTheme.secondaryText)
                        .frame(width: 30, alignment: .trailing)
                }
            }
        }
    }
}
