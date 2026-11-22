import SwiftUI

struct StatsBannerView: View {
    @ObservedObject var vm: QuizViewModel
    @ObservedObject var localizer: Localizer
    @Environment(\.dynamicTypeSize) private var dynamicTypeSize

    private var metrics: some View {
        Group {
            StatItem(value: "\(vm.quizHistory.count)", label: localizer.localized("quizzes"))
            StatItem(value: "\(vm.averageScore)%", label: localizer.localized("avgScore"))
            StatItem(value: "\(vm.passStreak)", label: localizer.localized("passStreak"))
        }
    }

    private var statsButton: some View {
        Button { vm.showStats() } label: {
            Text(localizer.localized("viewStats"))
                .font(AppTheme.body(14)).fontWeight(.semibold)
                .foregroundColor(AppTheme.blue)
                .frame(minWidth: 44, minHeight: 44)
                .contentShape(Rectangle())
        }
        .accessibilityIdentifier("view-stats")
    }

    var body: some View {
        VStack(spacing: 12) {
            if dynamicTypeSize.isAccessibilitySize {
                VStack(spacing: 16) { metrics }
                statsButton
            } else {
                HStack {
                    HStack(spacing: 16) { metrics }
                    Spacer()
                    statsButton
                }
            }
        }
        .padding(14)
        .cardStyle(borderWidth: 1)
    }
}
