import SwiftUI

struct StatsScreen: View {
    @ObservedObject var vm: QuizViewModel
    @ObservedObject var localizer: Localizer
    @State private var showResetAlert = false

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
                        Image(systemName: "chevron.left")
                        Text(localizer.localized("back"))
                    }
                    .font(.system(size: 15, weight: .semibold))
                    .foregroundColor(AppTheme.blue)
                }

                Text(localizer.localized("yourProgress"))
                    .font(.system(size: 22, weight: .bold))

                // Top stats grid
                LazyVGrid(columns: [
                    GridItem(.flexible()),
                    GridItem(.flexible()),
                    GridItem(.flexible()),
                ], spacing: 10) {
                    StatCardView(value: "\(vm.quizHistory.count)", label: localizer.localized("quizzes"), color: AppTheme.blue)
                    StatCardView(value: "\(vm.averageScore)%", label: localizer.localized("avgScore"), color: avgScoreColor)
                    StatCardView(value: "\(vm.questionsSeen)", label: localizer.localized("qsSeen"), color: .primary)
                }

                LazyVGrid(columns: [
                    GridItem(.flexible()),
                    GridItem(.flexible()),
                ], spacing: 10) {
                    StatCardView(value: "\(vm.passStreak)", label: localizer.localized("passStreak"), color: AppTheme.green)
                    StatCardView(value: "\(vm.bestScore)%", label: localizer.localized("bestScore"), color: .primary)
                }

                // Score history chart
                VStack(alignment: .leading, spacing: 12) {
                    Text(localizer.localized("scoreHistory"))
                        .font(.system(size: 15, weight: .semibold))

                    if vm.quizHistory.count >= 2 {
                        ScoreChartView(
                            history: vm.quizHistory,
                            passingPct: vm.currentState?.passingScorePct ?? 70
                        )
                        .frame(height: 180)
                    } else {
                        Text(vm.quizHistory.isEmpty ? localizer.localized("statsEmpty") : localizer.localized("statsOneMore"))
                            .font(.system(size: 14))
                            .foregroundColor(AppTheme.gray)
                            .frame(maxWidth: .infinity)
                            .frame(height: 120)
                    }
                }
                .padding(16)
                .cardStyle(borderWidth: 1)

                // Category bars
                if !vm.categoryStats.isEmpty {
                    VStack(alignment: .leading, spacing: 12) {
                        Text(localizer.localized("accuracyByCategory"))
                            .font(.system(size: 15, weight: .semibold))

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
                            .font(.system(size: 15, weight: .semibold))

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
                        .font(.system(size: 15, weight: .semibold))
                        .foregroundColor(AppTheme.red)
                        .frame(maxWidth: .infinity)
                        .padding(12)
                        .cardStyle(borderColor: AppTheme.redLight)
                }
                .alert(localizer.localized("resetConfirm", substitutions: ["state_name": vm.currentState?.name ?? ""]), isPresented: $showResetAlert) {
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
