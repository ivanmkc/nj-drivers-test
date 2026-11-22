import SwiftUI

struct ResultsScreen: View {
    @ObservedObject var vm: QuizViewModel
    @ObservedObject var localizer: Localizer
    @Environment(\.dynamicTypeSize) private var dynamicTypeSize

    var body: some View {
        ScrollView {
            VStack(spacing: 16) {
                SourceCitationView(state: vm.currentState)
                // Score circle
                ZStack {
                    Circle()
                        .stroke(vm.didPass ? AppTheme.green : AppTheme.red, lineWidth: 6)
                        .frame(width: dynamicTypeSize.isAccessibilitySize ? 220 : 160,
                               height: dynamicTypeSize.isAccessibilitySize ? 220 : 160)

                    VStack(spacing: 2) {
                        Text("\(vm.resultPct)%")
                            .font(AppTheme.display(42)).fontWeight(.bold)
                            .monospacedDigit()
                            .foregroundColor(vm.didPass ? AppTheme.green : AppTheme.red)
                        Text(vm.didPass ? localizer.localized("pass") : localizer.localized("fail"))
                            .font(AppTheme.body(14)).fontWeight(.semibold)
                            .foregroundColor(.primary)
                            .textCase(.uppercase)
                    }
                }
                .padding(.top, 24)

                Text(vm.didPass ? localizer.localized("congratulations") : localizer.localized("keepPracticing"))
                    .font(AppTheme.display(22)).fontWeight(.bold)

                if let state = vm.currentState {
                    Text(localizer.localized("resultDetail", substitutions: [
                        "correct": "\(vm.correctCount)",
                        "total": "\(vm.questions.count)",
                        "pass_pct": "\(state.passingScorePct)",
                        "agency": state.agency,
                    ]))
                    .font(AppTheme.body(15))
                    .foregroundColor(AppTheme.secondaryText)
                    .multilineTextAlignment(.center)
                    .lineSpacing(3)
                }

                if vm.needsStudyWarning {
                    VStack(alignment: .leading, spacing: 8) {
                        Text(localizer.localized("studyLanguageFooter"))
                            .font(.headline)
                        Button(localizer.localized("practiceEnglish")) { vm.practiceEnglish() }
                            .frame(minHeight: 44)
                    }
                    .padding(16)
                    .cardStyle()
                }
                // Action buttons
                Button {
                    vm.goHome()
                } label: {
                    Text(localizer.localized("newQuiz"))
                        .font(AppTheme.body(18)).fontWeight(.semibold)
                        .foregroundColor(AppTheme.onPrimary)
                        .frame(maxWidth: .infinity)
                        .padding(16)
                        .background(AppTheme.blue)
                        .clipShape(RoundedRectangle(cornerRadius: 12))
                }

                Button {
                    vm.showStats()
                } label: {
                    Text(localizer.localized("viewStats"))
                        .font(AppTheme.body(18)).fontWeight(.semibold)
                        .foregroundColor(AppTheme.blue)
                        .frame(maxWidth: .infinity)
                        .padding(16)
                        .cardStyle(borderColor: AppTheme.blue)
                }

                .accessibilityIdentifier("view-stats")

                // Review section
                if !vm.wrongResults.isEmpty {
                    VStack(alignment: .leading, spacing: 12) {
                        Text(localizer.localized("reviewMissed", substitutions: ["count": "\(vm.wrongResults.count)"]))
                            .font(AppTheme.body(18)).fontWeight(.semibold)

                        ForEach(vm.wrongResults, id: \.id) { result in
                            ReviewItemView(result: result, localizer: localizer)
                        }
                    }
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .padding(.top, 8)
                } else {
                    VStack(spacing: 8) {
                        Text(localizer.localized("perfectScore"))
                            .font(AppTheme.body(18)).fontWeight(.semibold)
                        Text(localizer.localized("perfectMsg"))
                            .font(AppTheme.body(15))
                            .foregroundColor(AppTheme.secondaryText)
                    }
                    .padding(.top, 8)
                }
            }
            .padding(16)
        }
        .background(AppTheme.grayLight)
    }
}
