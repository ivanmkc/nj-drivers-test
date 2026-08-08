import SwiftUI

struct HomeScreen: View {
    @ObservedObject var vm: QuizViewModel
    @ObservedObject var localizer: Localizer

    var body: some View {
        ScrollView {
            VStack(spacing: 16) {
                LanguageBarView(localizer: localizer, availableLangs: vm.currentState?.languages)
                    .padding(.bottom, 4)

                Text(localizer.localized("title", substitutions: [
                    "state": vm.currentState?.code.uppercased() ?? "",
                    "state_name": vm.currentState?.name ?? "",
                ]))
                .font(.system(size: 28, weight: .bold))
                .foregroundColor(AppTheme.blue)

                Text(localizer.localized("subtitle", substitutions: [
                    "state_name": vm.currentState?.name ?? "",
                    "agency": vm.currentState?.agency ?? "",
                ]))
                .font(.system(size: 15))
                .foregroundColor(AppTheme.gray)

                if let state = vm.currentState {
                    Text(localizer.localized("passingScore", substitutions: [
                        "pass_pct": "\(state.passingScorePct)",
                        "pass_count": "\(state.passCount)",
                        "test_count": "\(state.testQuestionCount)",
                    ]))
                    .font(.system(size: 13))
                    .foregroundColor(AppTheme.gray)
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
                    .font(.system(size: 15, weight: .semibold))

                HStack(spacing: 8) {
                    ForEach(vm.countOptions, id: \.self) { count in
                        let isAll = count == vm.currentState?.totalQuestions
                        Button {
                            vm.selectedCount = count
                        } label: {
                            Text(isAll ? localizer.localized("all") : "\(count)")
                                .font(.system(size: 16, weight: .semibold))
                                .padding(.horizontal, 20)
                                .padding(.vertical, 10)
                                .foregroundColor(vm.selectedCount == count ? AppTheme.onPrimary : AppTheme.blue)
                                .background(vm.selectedCount == count ? AppTheme.blue : AppTheme.card)
                                .cardStyle(borderColor: AppTheme.blue)
                                .frame(minHeight: 44)
                                .contentShape(Rectangle())
                        }
                    }
                }

                // Start button
                let weakEmpty = vm.quizMode == .weak && vm.weakQuestions.isEmpty
                Button {
                    vm.startQuiz()
                } label: {
                    Text(weakEmpty ? localizer.localized("noWeakSpots") : localizer.localized("startQuiz"))
                        .font(.system(size: 18, weight: .semibold))
                        .foregroundColor(AppTheme.onPrimary)
                        .frame(maxWidth: .infinity)
                        .padding(16)
                        .background(weakEmpty ? AppTheme.blue.opacity(0.5) : AppTheme.blue)
                        .clipShape(RoundedRectangle(cornerRadius: 12))
                }
                .disabled(weakEmpty)

                // About this test
                if let state = vm.currentState {
                    AboutTestSection(state: state, localizer: localizer)
                }

                // Change state
                Button {
                    vm.goStatePicker()
                } label: {
                    Text(localizer.localized("changeState"))
                        .font(.system(size: 14))
                        .foregroundColor(AppTheme.gray)
                }

            }
            .padding(.horizontal, 16)
            .padding(.top, 24)
        }
        .background(AppTheme.grayLight)
    }
}

// MARK: - About This Test

private struct AboutTestSection: View {
    let state: StateInfo
    @ObservedObject var localizer: Localizer
    @State private var isExpanded = false

    var body: some View {
        DisclosureGroup(isExpanded: $isExpanded) {
            VStack(alignment: .leading, spacing: 12) {
                if let verification = state.verification {
                    VerificationBadgesView(verification: verification, localizer: localizer)
                }

                if let source = state.source {
                    SourceRow(source: source, manualUrl: state.verification?.manualUrl, localizer: localizer)
                }

                if let categories = state.categories, !categories.isEmpty {
                    CategoryBreakdownView(categories: categories, localizer: localizer)
                }
            }
            .padding(.top, 8)
        } label: {
            HStack(spacing: 6) {
                Image(systemName: "info.circle")
                    .foregroundColor(AppTheme.blue)
                Text(localizer.localized("aboutThisTest"))
                    .font(.system(size: 15, weight: .semibold))
                    .foregroundColor(.primary)
            }
        }
        .padding(14)
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
                .font(.system(size: 13))
                .foregroundColor(AppTheme.gray)

            if let urlString = manualUrl, let url = URL(string: urlString) {
                Link(destination: url) {
                    Text(source)
                        .font(.system(size: 13))
                        .foregroundColor(AppTheme.blue)
                        .underline()
                        .multilineTextAlignment(.leading)
                }
            } else {
                Text(source)
                    .font(.system(size: 13))
                    .foregroundColor(.primary)
                    .multilineTextAlignment(.leading)
            }
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
                            .foregroundColor(AppTheme.gray)
                        Text(edition)
                    }
                    .font(.system(size: 12))
                }

                if let verifiedAt = verification.verifiedAt {
                    HStack(spacing: 4) {
                        Text(localizer.localized("verified") + ":")
                            .foregroundColor(AppTheme.gray)
                        Text(Self.formatDate(verifiedAt))
                    }
                    .font(.system(size: 12))
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
                Image(systemName: systemImage)
                    .font(.system(size: 11))
                    .foregroundColor(AppTheme.green)
            }
            Text(label)
                .foregroundColor(AppTheme.gray)
            Text(value)
                .fontWeight(.semibold)
        }
        .font(.system(size: 12))
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
                    Text(cat.name.replacingOccurrences(of: "_", with: " ").capitalized)
                        .font(.system(size: 12))
                        .frame(width: 120, alignment: .leading)
                        .lineLimit(1)

                    GeometryReader { geo in
                        RoundedRectangle(cornerRadius: 3)
                            .fill(AppTheme.blue)
                            .frame(width: geo.size.width * CGFloat(cat.count) / CGFloat(maxCount), height: 8)
                    }
                    .frame(height: 8)

                    Text("\(cat.count)")
                        .font(.system(size: 12, weight: .semibold))
                        .monospacedDigit()
                        .foregroundColor(AppTheme.gray)
                        .frame(width: 30, alignment: .trailing)
                }
            }
        }
    }
}
