import SwiftUI

struct StatsScreen: View {
    @ObservedObject var vm: QuizViewModel
    @ObservedObject var localizer: Localizer
    @State private var showResetAlert = false

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                // Back button
                Button {
                    vm.goHome()
                } label: {
                    HStack(spacing: 6) {
                        Image(systemName: "chevron.left")
                        Text(localizer.t("back"))
                    }
                    .font(.system(size: 15, weight: .semibold))
                    .foregroundColor(AppTheme.blue)
                }

                Text(localizer.t("yourProgress"))
                    .font(.system(size: 22, weight: .bold))

                // Top stats grid
                LazyVGrid(columns: [
                    GridItem(.flexible()),
                    GridItem(.flexible()),
                    GridItem(.flexible()),
                ], spacing: 10) {
                    StatCardView(value: "\(vm.quizHistory.count)", label: localizer.t("quizzes"), color: AppTheme.blue)
                    StatCardView(value: "\(vm.averageScore)%", label: localizer.t("avgScore"), color: AppTheme.green)
                    StatCardView(value: "\(vm.questionsSeen)", label: localizer.t("qsSeen"), color: .primary)
                }

                LazyVGrid(columns: [
                    GridItem(.flexible()),
                    GridItem(.flexible()),
                ], spacing: 10) {
                    StatCardView(value: "\(vm.passStreak)", label: localizer.t("passStreak"), color: AppTheme.green)
                    StatCardView(value: "\(vm.bestScore)%", label: localizer.t("bestScore"), color: .primary)
                }

                // Score history chart
                VStack(alignment: .leading, spacing: 12) {
                    Text(localizer.t("scoreHistory"))
                        .font(.system(size: 15, weight: .semibold))

                    if vm.quizHistory.count >= 2 {
                        ScoreChartView(
                            history: vm.quizHistory,
                            passingPct: vm.currentState?.passingScorePct ?? 70
                        )
                        .frame(height: 180)
                    } else {
                        Text(vm.quizHistory.isEmpty ? "Take a quiz to see your progress" : "Take one more quiz to see the chart")
                            .font(.system(size: 14))
                            .foregroundColor(AppTheme.gray)
                            .frame(maxWidth: .infinity)
                            .frame(height: 120)
                    }
                }
                .padding(16)
                .background(AppTheme.card)
                .overlay(
                    RoundedRectangle(cornerRadius: 12)
                        .stroke(AppTheme.border, lineWidth: 1)
                )
                .clipShape(RoundedRectangle(cornerRadius: 12))

                // Category bars
                if !vm.categoryStats.isEmpty {
                    VStack(alignment: .leading, spacing: 12) {
                        Text(localizer.t("accuracyByCategory"))
                            .font(.system(size: 15, weight: .semibold))

                        ForEach(vm.categoryStats, id: \.category) { cat in
                            CategoryBarView(category: cat.category, pct: cat.pct)
                        }
                    }
                }

                // Weak questions
                let weak = vm.weakQuestions
                if !weak.isEmpty {
                    VStack(alignment: .leading, spacing: 12) {
                        Text(localizer.t("mostMissed"))
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
                    Text(localizer.t("resetAll"))
                        .font(.system(size: 15, weight: .semibold))
                        .foregroundColor(AppTheme.red)
                        .frame(maxWidth: .infinity)
                        .padding(12)
                        .background(AppTheme.card)
                        .overlay(
                            RoundedRectangle(cornerRadius: 12)
                                .stroke(AppTheme.redLight, lineWidth: 2)
                        )
                        .clipShape(RoundedRectangle(cornerRadius: 12))
                }
                .alert(localizer.t("resetConfirm", vars: ["state_name": vm.currentState?.name ?? ""]), isPresented: $showResetAlert) {
                    Button("Cancel", role: .cancel) {}
                    Button("Reset", role: .destructive) {
                        vm.clearData()
                    }
                }
            }
            .padding(16)
        }
        .background(AppTheme.grayLight)
    }
}
