import SwiftUI

struct ResultsScreen: View {
    @ObservedObject var vm: QuizViewModel
    @ObservedObject var localizer: Localizer

    var body: some View {
        ScrollView {
            VStack(spacing: 16) {
                // Score circle
                ZStack {
                    Circle()
                        .stroke(vm.didPass ? AppTheme.green : AppTheme.red, lineWidth: 6)
                        .frame(width: 160, height: 160)

                    VStack(spacing: 2) {
                        Text("\(vm.resultPct)%")
                            .font(.system(size: 42, weight: .bold))
                            .foregroundColor(vm.didPass ? AppTheme.green : AppTheme.red)
                        Text(vm.didPass ? localizer.t("pass") : localizer.t("fail"))
                            .font(.system(size: 14, weight: .semibold))
                            .foregroundColor(vm.didPass ? AppTheme.green : AppTheme.red)
                            .textCase(.uppercase)
                    }
                }
                .padding(.top, 24)

                Text(vm.didPass ? localizer.t("congratulations") : localizer.t("keepPracticing"))
                    .font(.system(size: 22, weight: .bold))

                if let state = vm.currentState {
                    Text(localizer.t("resultDetail", vars: [
                        "correct": "\(vm.correctCount)",
                        "total": "\(vm.questions.count)",
                        "pass_pct": "\(state.passingScorePct)",
                        "agency": state.agency,
                    ]))
                    .font(.system(size: 15))
                    .foregroundColor(AppTheme.gray)
                    .multilineTextAlignment(.center)
                    .lineSpacing(3)
                }

                // Action buttons
                Button {
                    vm.goHome()
                } label: {
                    Text(localizer.t("newQuiz"))
                        .font(.system(size: 18, weight: .semibold))
                        .foregroundColor(.white)
                        .frame(maxWidth: .infinity)
                        .padding(16)
                        .background(AppTheme.blue)
                        .clipShape(RoundedRectangle(cornerRadius: 12))
                }

                Button {
                    vm.showStats()
                } label: {
                    Text(localizer.t("viewStats"))
                        .font(.system(size: 18, weight: .semibold))
                        .foregroundColor(AppTheme.blue)
                        .frame(maxWidth: .infinity)
                        .padding(16)
                        .background(AppTheme.card)
                        .overlay(
                            RoundedRectangle(cornerRadius: 12)
                                .stroke(AppTheme.blue, lineWidth: 2)
                        )
                        .clipShape(RoundedRectangle(cornerRadius: 12))
                }

                // Review section
                if !vm.wrongResults.isEmpty {
                    VStack(alignment: .leading, spacing: 12) {
                        Text(localizer.t("reviewMissed", vars: ["count": "\(vm.wrongResults.count)"]))
                            .font(.system(size: 18, weight: .semibold))

                        ForEach(vm.wrongResults, id: \.id) { result in
                            ReviewItemView(result: result, localizer: localizer)
                        }
                    }
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .padding(.top, 8)
                } else {
                    VStack(spacing: 8) {
                        Text(localizer.t("perfectScore"))
                            .font(.system(size: 18, weight: .semibold))
                        Text(localizer.t("perfectMsg"))
                            .font(.system(size: 15))
                            .foregroundColor(AppTheme.gray)
                    }
                    .padding(.top, 8)
                }
            }
            .padding(16)
        }
        .background(AppTheme.grayLight)
    }
}
