import SwiftUI

struct StatsScreen: View {
    @ObservedObject var vm: QuizViewModel
    @ObservedObject var localizer: Localizer
    @State private var showResetAlert = false
    @Environment(\.dynamicTypeSize) private var dynamicTypeSize

    private var avgScoreColor: Color {
        let pct = vm.averageScore
        let passingPct = vm.currentState?.passingScorePct ?? 70
        if pct >= passingPct { return AppTheme.green }
        if pct >= 50 { return AppTheme.orange }
        return AppTheme.red
    }

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                // Back button
                Button {
                    vm.goHome()
                } label: {
                    HStack(spacing: 6) {
                        Image(systemName: "chevron.left").accessibilityHidden(true)
                        Text(localizer.localized("back"))
                    }
                    .font(AppTheme.body(15)).fontWeight(.semibold)
                    .foregroundColor(AppTheme.blue)
                }

                .frame(minHeight: 44)

                Text(localizer.localized("yourProgress"))
                    .font(AppTheme.display(22)).fontWeight(.bold)

                LanguageBarView(localizer: localizer, availableLangs: vm.currentState?.languages,
                                officialTestLanguages: vm.currentState?.officialTestLanguages)
                Text(localizer.localized(
                    vm.showLegacyStats ? "legacyLanguageStats" : "languageStats",
                    substitutions: ["language": localizer.langLabels[localizer.currentLang] ?? localizer.currentLang]
                ))
                    .font(.subheadline)
                if vm.needsStudyWarning {
                    Button(localizer.localized("englishStats")) { localizer.currentLang = "en" }
                        .frame(minHeight: 44)
                }
                if vm.legacySessionCount > 0 {
                    Button(localizer.localized("legacyStats", substitutions: ["count": "\(vm.legacySessionCount)"])) {
                        vm.showLegacyStats.toggle()
                    }
                    .frame(minHeight: 44)
                        .font(.subheadline)
                        .foregroundColor(AppTheme.secondaryText)
                }
                // Top stats grid
                let metricsLayout = dynamicTypeSize >= .xxxLarge ?
                    AnyLayout(VStackLayout(spacing: 10)) : AnyLayout(HStackLayout(spacing: 10))
                metricsLayout {
                    StatCardView(value: "\(vm.quizHistory.count)", label: localizer.localized("quizzes"),
                                 color: AppTheme.blue, accessibilityID: "stats-session-count")
                    StatCardView(value: "\(vm.averageScore)%", label: localizer.localized("avgScore"), color: avgScoreColor)
                    StatCardView(value: "\(vm.questionsSeen)", label: localizer.localized("qsSeen"), color: .primary)
                }

                metricsLayout {
                    StatCardView(value: "\(vm.passStreak)", label: localizer.localized("passStreak"), color: AppTheme.green)
                    StatCardView(value: "\(vm.bestScore)%", label: localizer.localized("bestScore"), color: .primary)
                }

                // Score history chart
                VStack(alignment: .leading, spacing: 12) {
                    Text(localizer.localized("scoreHistory"))
                        .font(AppTheme.body(15)).fontWeight(.semibold)

                    if vm.quizHistory.count >= 2 {
                        ScoreChartView(
                            history: vm.quizHistory,
                            passingPct: vm.currentState?.passingScorePct ?? 70
                        )
                        .frame(height: 180)
                    } else {
                        Text(localizer.localized(vm.quizHistory.isEmpty ? "statsEmpty" : "statsOneMore"))
                            .font(.body)
                            .foregroundColor(AppTheme.secondaryText)
                            .fixedSize(horizontal: false, vertical: true)
                            .frame(maxWidth: .infinity)
                            .padding(.vertical, 24)
                    }
                }
                .padding(16)
                .cardStyle(borderWidth: 1)

                // Category bars
                if !vm.categoryStats.isEmpty {
                    VStack(alignment: .leading, spacing: 12) {
                        Text(localizer.localized("accuracyByCategory"))
                            .font(AppTheme.body(15)).fontWeight(.semibold)

                        ForEach(vm.categoryStats, id: \.category) { cat in
                            CategoryBarView(category: cat.category, pct: cat.pct, localizer: localizer)
                        }
                    }
                }

                // Weak questions
                let weak = vm.weakQuestions
                if !weak.isEmpty {
                    VStack(alignment: .leading, spacing: 12) {
                        Text(localizer.localized("mostMissed"))
                            .font(AppTheme.body(15)).fontWeight(.semibold)

                        ForEach(weak.prefix(15)) { w in
                            WeakItemView(weak: w, localizer: localizer)
                        }
                    }
                }

                // Reset button
                Divider()
                    .padding(.top, 8)

                Button {
                    showResetAlert = true
                } label: {
                    Text(localizer.localized("resetAll"))
                        .font(AppTheme.body(15)).fontWeight(.semibold)
                        .foregroundColor(AppTheme.errorText)
                        .frame(maxWidth: .infinity)
                        .padding(12)
                        .cardStyle(borderColor: AppTheme.redLight)
                }
                .alert(
                    localizer.localized("resetConfirm", substitutions: ["state_name": vm.currentState?.name ?? ""]),
                    isPresented: $showResetAlert
                ) {
                    Button(localizer.localized("cancel"), role: .cancel) {}
                    Button(localizer.localized("resetButton"), role: .destructive) {
                        vm.clearData()
                    }
                }
            }
            .padding(16)
        }
        .background(AppTheme.grayLight)
    }
}
